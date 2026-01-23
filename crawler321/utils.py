import os
os.environ["LOKY_MAX_CPU_COUNT"] = "4"
import re, time, math, json, joblib, string, random
import numpy as np
import pandas as pd
from io import StringIO
from collections import Counter
from urllib.parse import urljoin
from sklearn.cluster import DBSCAN
from bs4 import BeautifulSoup, Comment
from sklearn.preprocessing import StandardScaler, LabelEncoder


# 获取当前文件的绝对路径
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


def get_pretty_soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, 'lxml')
'''
    获取charset
'''
def get_charset_of_html(raw_html: str) -> str:
    charset_match = re.search(r'charset="?([\w-]+)"?', raw_html)
    if charset_match:
        charset = charset_match.group(1)
        return charset
    else:
        return None
    

'''
    过滤tags
'''
def get_filtered_tags(soup: BeautifulSoup, filter_labels: list=None):
    filter_labels = filter_labels if filter_labels else ['head', 'script', 'style', 'nav', 'footer', 'title']
    for label in soup(filter_labels):
        label.decompose()
    return soup


'''
    过滤class, id中包含的关键词
'''
def get_filtered_keywords(soup: BeautifulSoup, filter_keywords: list=None):
    filter_keywords = filter_keywords if filter_keywords else \
                    ["nav", "header", "hd", "head", "footer", "foot", "aside", "copy", "crumb", "bread"]
    def contains_keywords(attr_value):
        return any(keyword in attr_value for keyword in filter_keywords)
    tags_removed = soup.find_all(
        lambda tag: tag.name != 'html' 
        and any(contains_keywords(attr) for attr in tag.get('class', []))
        or contains_keywords(tag.get('id', '')))
    for tag in tags_removed:
        tag.decompose()
    return soup


'''
    去除空标签
'''
def remove_empty_tags(soup: BeautifulSoup):
    def isBlankLabel(elements):
        return all(element.strip() == '' for element in elements)
    while True:
        flag = True
        empty_tags = soup.find_all()
        for tag in empty_tags:
            try:
                if not tag.contents or isBlankLabel(tag.contents):
                    tag.decompose()
                    flag = False
            except Exception:
                continue
        if flag == True:
            break
    return soup

def get_mata_data(html: str, metas: list=None) -> dict:
    soup = get_pretty_soup(html)
    metas = metas or ["keywords", "description", "author", "source"]
    result = {}
    def get_content(tags):
        for attr, value in tags.attrs.items():
            if attr.lower() == 'content':
                return value
        return None
    result['title'] = soup.title.string.strip() if soup.title else None
    for name in metas:
        tags = soup.find(lambda tag: tag.name.lower() == 'meta' 
                        and tag.attrs.get('name', '').lower() == name.lower())
        result[name] = get_content(tags).strip() if tags else None
    return result


'''
-----------------------------Tools for NoExtractionStrategy-----------------------------
'''
def extract_raw_html(html) -> str:
    # 使用Beautiful Soup解析HTML内容
    soup = get_pretty_soup(html)
    for link in soup.find_all('link', attrs={'rel': 'stylesheet'}):
        link.decompose()
    # 去除所有空标签
    # for link in soup.find_all('a'):
    #     link.decompose()
    soup = remove_empty_tags(soup=soup)
    # 找出所有的文本信息
    all_text = soup.find_all(string=True)
    # 进行文本清洗和格式化
    cleaned_text = []
    for text in all_text:
        # 去除空白字符和换行符
        text = text.strip()
        if text:
            cleaned_text.append(re.sub(r'\s+', ' ', text))
            # 使用正则表达式去除多余的空白字符（如果有的话）
            # text = re.sub(r'\s+', ' ', text).replace('：', ':').replace('；', ';')
            # # 判断文本块的结尾字符，决定是否添加句号
            # if text.endswith(('。', ';', ':')):
            #     cleaned_text.append(text)
            # else:
            #     cleaned_text.append(text)  # 默认加上句号
    # 将清洗后的文本以分号分隔组合成一个字符串
    result = ''.join(cleaned_text).replace('html', '').replace('>', '').replace('当前位置:', '').replace('»', '')
    result = re.sub(r'\n+', '\\n', result)   # 去连续空行
    return result


'''
    过滤网页内容

    :param html:
    :param filter_labels: ...
    :param filter_keywords: ...

    :return soup.prettify()
'''
def html_filter(html: str, 
                filter_labels: list=None, 
                filter_keywords: list=None):
    soup = get_pretty_soup(html)
    # delete comments
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    # delete styles
    for link in soup.find_all('link', attrs={'rel': 'stylesheet'}):
        link.decompose()
    # delete labels
    soup = get_filtered_tags(soup=soup, filter_labels=filter_labels)
    # delete keywords
    soup = get_filtered_keywords(soup=soup, filter_keywords=filter_keywords)
    # delete all the blanks
    return remove_empty_tags(soup=soup)


'''
    获取下一页的链接

    :param html: ...
    :param base_url: ...
    :param next_keywords: ...

    :return next_pagination_url -> str

'''
def get_next_pagination(soup: BeautifulSoup, 
                        base_url: str, 
                        next_keywords: list=None):
    next_keywords = next_keywords or ["下一页", "下页", "后页"]
    # 动态生成正则表达式，匹配包含关键字的文本
    keywords_pattern = re.compile("|".join(map(re.escape, next_keywords)), re.IGNORECASE)
    # 查找所有<a>标签
    a_tags = soup.find_all('a')
    # 遍历所有<a>标签，查找包含关键字的标签并获取href属性
    for a in a_tags:
        if keywords_pattern.search(a.get_text()):
            return urljoin(base_url, a['href'])
    return ""

'''
    获取soup中所有的<a>中的links

    :param soup: ...
    :param base_url: ...
    
    :return hrefs -> set()
            parents -> list
'''
def get_a_links(soup: BeautifulSoup,
                base_url: str):
    hrefs = []
    record = set()
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if not href.startswith('javascript') and \
           not href.startswith('#') and href != '' \
           and href not in record:
            record.add(href)
            parent_tag = a_tag.find_parent()
            hrefs.append({
                "url": urljoin(base_url, href),
                "content": ''.join(s.strip() for s in a_tag.find_all(string=True, recursive=True)),
                "parent_name": parent_tag.name,
                "parent_class": ''.join(parent_tag.get('class')) if parent_tag.get('class') else '#####'
            })
    return hrefs


'''
-----------------------------Tools for PageLinksExtractionStrategy-----------------------------
'''

'''
    计算两个urls的交集
'''
def get_common_urls(urls1: list, urls2: list) -> set:
    set1 = {item['url'] for item in urls1}
    intersection = {item['url'] for item in urls2 if item['url'] in set1}
    return intersection


'''
    计算两个urls的差集
'''
def get_diff_urls(origins: list, commons: set) -> list:
    return [item for item in origins if item['url'] not in commons]


'''
    格式化聚类所需的网页结构特征
'''
def formalize_urls(urls: list):
    infos = []
    for url in urls:
        features = {
            'domain': '',
            'length': 0,
            'segment': 0,
            'parent_name': '',
            'parent_class': '',
            'sub_url': '',
            'full_url':'',
            'content': '',
        }
        features['full_url'] = url['url']
        features['parent_name'] =  url['parent_name']
        features['parent_class'] = url['parent_class']
        features['content'] = url['content']
        link = features['full_url'].replace('http://', '').replace('https://', '')
        features['length'] = len(link)
        link_split = link.split('/')
        
        features['domain'] = link_split[0]
        features['segment'] = len(link_split)
        features['sub_url'] = ''.join(link_split[1:])
        infos.append(features)
    # infos = []
    # for url in urls:
    #     full_url = url['url']
    #     link = full_url.replace('http://', '').replace('https://', '')
    #     link_split = link.split('/')

    #     features = {
    #         'domain': link_split[0],
    #         'length': len(link),
    #         'segment': len(link_split),
    #         'parent_name': url['parent_name'],
    #         'parent_class': url['parent_class'],
    #         'sub_url': ''.join(link_split[1:]),
    #         'full_url': full_url
    #     }

    #     infos.append(features)

    return infos


'''
    做聚类: 需要优化一下
    DBSCAN是一种基于密度的聚类算法，它能够在具有噪声的空间数据库中发现任意形状的簇。
    它的基本思想是将密度相连的点划分为同一簇，并将密度较低的点视为噪声点。
    它的算法步骤主要包括寻找核心点和合并临时聚类簇两个过程。
    它需要指定两个参数，即邻域半径ε和最小邻域点数MinPoints
'''
def clustering_urls(urls: list, min_cluster=8):
    # print("[Logger]🍎 Beginning clustering_urls")
    # start_time = time.time()
    # 提取类别特征
    domains = [url['domain'] for url in urls]
    parent_names = [url['parent_name'] for url in urls]

    # 使用LabelEncoder对类别特征进行编码
    domain_encoder = LabelEncoder()
    parent_name_encoder = LabelEncoder()

    encoded_domains = domain_encoder.fit_transform(domains)
    encoded_parent_names = parent_name_encoder.fit_transform(parent_names)
    # 特征向量化
    def extract_features(url, encoded_domains, encoded_parent_names, index):
        domain = encoded_domains[index]
        length = url['length']
        segment = url['segment']
        parent_name = encoded_parent_names[index]
        parent_class_length = len(url['parent_class'])
        sub_url_length = len(url['sub_url'])
        
        return [domain, length, segment, parent_name, parent_class_length, sub_url_length]

    # 构建特征矩阵
    features = np.array([extract_features(url, encoded_domains, encoded_parent_names, idx) for idx, url in enumerate(urls)])

    # 标准化特征
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    # # 使用DBSCAN聚类算法进行链接聚类
    dbscan = DBSCAN(eps=0.8, min_samples=min_cluster)
    clusters = dbscan.fit_predict(features_scaled)
    # print(f"[Logger]⏰ clustering_urls: {time.time() - start_time}s")
    return clusters


'''
-----------------------------Tools for TextExtractionStrategy-----------------------------
'''
'''
    计算节点信息密度
'''
def calculate_density(node: BeautifulSoup):
    # 计算节点自身的直接文本内容
    text_length = len(''.join(node.find_all(string=True, recursive=False)))
    link_length = sum(len(link.get_text(strip=True)) for link in node.find_all('a', recursive=False))
    total_length = len(str(node))
    if total_length == 0:
        return 0, 0
    text_density = text_length / total_length
    link_density = link_length / total_length
    return text_density, link_density


'''
    获取主要内容
'''
def extract_main_content(soup: BeautifulSoup):
    main_contents = []
    seen_contents = []
    for node in soup.find_all(recursive=True):
        text_density, link_density = calculate_density(node=node)
        if text_density > 0.5 and link_density < 0.2:
            content = ''.join(node.find_all(string=True, recursive=False)).strip()
            if content and content not in seen_contents:
                main_contents.append(content)
                seen_contents.append(content)
    return main_contents


'''
    计算信息熵
'''
def calculate_entropy(content: str):
    if not content:
        return 0
    counter = Counter(content)
    entropy = -sum((count / len(content)) * math.log2(count / len(content)) for count in counter.values())
    return entropy


'''
    移除熵值低的结点
'''
def remove_low_entropy_node(contents: list) ->list:
    return [content for content in contents 
            if calculate_entropy(content) > 2.0]


'''
-----------------------------Tools for ObjectExtractionStrategy-----------------------------
'''
def html_object_encoding(soup: BeautifulSoup) -> str:
    # print("[Logger]🍎 Beginning htm_object_encoding")
    # print("[Logger]🖊 编码前的长度为:", len(str(soup)))
    start_time = time.time()
    html_str = str(soup)
    replace_strs = {
        "：": ":",
        "&nbsp;": "",
        "&nbsp；": "",
        "&nbsp": "",
        "\u3000": "",
        "\xa0":"",
        "--": "",
        "##": "",
        "$": ""
    }
    # 创建正则表达式将所有替换的模式合并
    replace_pattern = re.compile("|".join(map(re.escape, replace_strs.keys())))
    # 替换函数
    def replace_match(match):
        return replace_strs[match.group(0)]
    html_str = replace_pattern.sub(replace_match, html_str)
    # html_str = str(soup).replace("：", ":").replace("&nbsp", "").replace("--", "").replace("##", "")
    html_str = re.sub(r'\d{2}:\d{2}:\d{2}', '', html_str)
    # with open("test.html", "w", encoding="UTF-8") as f:
    #     f.write(html_str)
    # print(html_str)
    soup = get_pretty_soup(html_str)
    
    res = StringIO()
    stack = [soup]
    # 递归解析
    while stack:
        current = stack.pop()
        if isinstance(current, str):
            text = re.sub(r'[\n\r\t]', '', current.strip())
            if text.endswith(":"):
                res.write(f"##{text[:-1]}##")
            elif text == ":":
                current_res = res.getvalue().rstrip("--")
                res = StringIO(current_res)
                last_sep_index = current_res.rfind("--")
                if last_sep_index != -1:
                    new_res = current_res[:last_sep_index + 2] + "$##" + current_res[last_sep_index + 2:] + "##"
                    res = StringIO(new_res)
                else:
                    res.write("##" + current_res + "##")
            elif text != "":
                index = text.find(":")
                if index == -1:
                    res.write(text + "--$")
                else:
                    res.write("##" + text[:index] + "##" + text[index + 1:] + "--$")
        elif hasattr(current, 'children'):
            stack.extend(reversed(list(current.children)))
    # print("[Logger]🖊 编码后的长度为:", len(str(res.getvalue())))
    # print(f"[Logger]⏰ htm_object_encoding: {time.time() - start_time}s")
    return res.getvalue()


'''
    提取出实体, 可以改进
'''
def extract_object_pairs(encoded_text) -> list:
    # pattern = re.compile(r"##([^\s#]+)##([^\s]+)--")
    # pattern = re.compile(r"##([^\s#\-\$]+)##([^\s#\-\$]+)--\$")
    # pattern = re.compile(r"##([^#\-\$]+)##([^#\-\$]+)--\$")
    # pattern = re.compile(r"##([^\s#\-$\-]+(?:-[^\s#\-$\-]*)*)##([^\s#\-$\-]+(?:-[^\s#\-$\-]*)*)--\$")
    # pattern = re.compile(r"##([^-#\$][^-#\$]*(?:-[^-#\$]*(?!--))*)##([^-#\$][^-#\$]*(?:-[^-#\$]*(?!--))*)--\$")
    pattern = re.compile(r"##([^#\$]+)##([^#\$]+)--\$")
    objects = pattern.findall(encoded_text)
    results = []
    for key, value in objects:
        if results and results[-1].get(key) is None:
            results[-1][key] = value
        else:
            results.append({key: value})
    return results


'''
-----------------------------Tools for XPathExtractionStrategy-----------------------------
'''
AbsoluteXPATHString = """
    function absoluteXPath(element) {
            var comp, comps = [];
            var parent = null;
            var xpath = '';
            var getPos = function(element) {
                var position = 1, curNode;
                if (element.nodeType == Node.ATTRIBUTE_NODE) {
                    return null;
                }
                for (curNode = element.previousSibling; curNode; curNode = curNode.previousSibling) {
                    if (curNode.nodeName == element.nodeName) {
                        ++position;
                    }
                }
                return position;
            };
            
            if (element instanceof Document) {
                return '/';
            }

            for (; element && !(element instanceof Document); element = element.nodeType == Node.ATTRIBUTE_NODE ? element.ownerElement : element.parentNode) {
                comp = comps[comps.length] = {};
                switch (element.nodeType) {
                    case Node.TEXT_NODE:
                        comp.name = 'text()';
                        break;
                    case Node.ATTRIBUTE_NODE:
                        comp.name = '@' + element.nodeName;
                        break;
                    case Node.PROCESSING_INSTRUCTION_NODE:
                        comp.name = 'processing-instruction()';
                        break;
                    case Node.COMMENT_NODE:
                        comp.name = 'comment()';
                        break;
                    case Node.ELEMENT_NODE:
                        comp.name = element.nodeName;
                        break;
                }
                comp.position = getPos(element);
            }

            for (var i = comps.length - 1; i >= 0; i--) {
                comp = comps[i];
                xpath += '/' + comp.name.toLowerCase();
                if (comp.position !== null) {
                    xpath += '[' + comp.position + ']';
                }
            }

            return xpath;
        }
    return absoluteXPath(arguments[0]);
"""


def formalize_xpath(xpath: str) -> str:
    index = xpath.rfind('/')
    pattern = re.compile(r'\[.*?\]')
    cleaned_path = pattern.sub('', xpath[:index])
    return cleaned_path + xpath[index:]

def get_web_feature(soup: BeautifulSoup):
    features = {
        "a_ratio": 0,
        "dd_ratio": 0,
        "content_tag_ratio": 0,
        "content_ratio": 0,
        "colon": 0
    }
    a_count, dd_count, content_tag_count, content_length = 0, 0, 0, 0
    # 统计<a>数目
    for a_tag in soup.find_all('a'):
        if a_tag.contents and isinstance(a_tag.contents, str) and \
        (":" in ''.join(a_tag.contents) or "：" in ''.join(a_tag.contents)):
            continue
        href = a_tag.get('href', '')
        if href.startswith('javascript') or href.startswith('#') \
           or a_tag.find('img') or a_tag.find('video') or href=='':
            continue
        a_count += 1
    # 统计object内容
    dd_count = dd_count + len(soup.find_all('dd')) + len(soup.find_all('tr'))
    def is_date_format(s):
    # 匹配格式xx-xx-xx，例如23-07-24
        pattern1 = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        # 匹配格式xx-xx，例如23-07
        pattern2 = re.compile(r'^\d{2}-\d{2}$')
        pattern3 = re.compile(r'^\d{4}-\d{2}$')
        return pattern1.match(s) or pattern2.match(s) or pattern3.match(s)

    for tag in soup.find_all(True):
        if tag.name not in ['a', 'dl', 'table', 'tr', 'td', 'dd', 'h1', 'h2', 'h3', 'h4', 'h5']:
            text = tag.find(string=True, recursive=False)
            if text and (':' in text or '：' in text):
                dd_count += 1
            if tag.parent.name not in ['a', 'dl', 'table', 'tr', 'td', 'dd', 'h1', 'h2', 'h3', 'h4', 'h5']:
                if text and text.strip() and (":" not in text and "：" not in text) and not is_date_format(text):
                    content_tag_count += 1
                    content_length += len(text.strip())
    total = a_count + dd_count + content_tag_count
    if total > 0:
        features['a_ratio'] = a_count / total
        features['dd_ratio'] =  dd_count / total
        features['content_tag_ratio'] = content_tag_count / total
    if content_tag_count > 0:
        features['content_ratio'] = content_length / content_tag_count
    return features

def pred_web_category(features: dict, model_name: str) -> str:
    scaler_path = os.path.join(__location__, "models", model_name, "scaler.pkl")
    model_path = os.path.join(__location__, "models", model_name, "model.pkl")
    scaler = joblib.load(scaler_path)
    model  = joblib.load(model_path)
    features2 = pd.DataFrame([features])
    formalized_features = scaler.transform(features2)
    return model.predict(formalized_features)[0]

KEYWORDELEMENTSCRIPT = """
    var elements = document.querySelectorAll('*');
    var matchingElements = [];
    for (var i = 0; i < elements.length; i++) {
        var text = elements[i].textContent.replace(/\\s+/g, '');
        if (text.includes(arguments[0])) {
            matchingElements.push(elements[i]);
        }
    }
    return matchingElements;    
"""
def formalize_result(obj) -> dict:
    return json.loads(
        obj.model_dump_json(indent=4)
    )

def generate_identifier(length=8) -> str:
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def is_media_type(url: str, file_types=None) -> bool:
    supported_types = file_types or ['pdf', 'doc', 'docx', 'xlsx', 'xls', 'mp3', 'mp4', 'png', 'jpg', 'jpeg']
    return any(
        url.lower().endswith(f'.{file_type}') 
        for file_type in supported_types
    )

def get_media_type(url: str) -> str:
    idx = url.lower().rfind('.')
    if idx != -1:
        return url[idx+1:]
    return ''