import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QComboBox,
    QVBoxLayout, QHBoxLayout, QGroupBox, QGridLayout, QTextEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QScrollArea,QSpacerItem, QSizePolicy, QFileDialog
)
from PyQt5.QtCore import Qt
from run_crawler import RunCrawler
from crawler_strategy import RequestsCrawlerStrategy
from extraction_strategy import *

class MainWindow(QWidget):
    class LevelCrawl:
        def __init__(self):
            # 提取策略
            self.extract_strategy = self.create_QComboBox(
                ["自动识别", "PageLinks", "Text", "Object", "LLVM", "无", "自定义"]
            )
            self.extract_strategy.currentIndexChanged.connect(self.update_strategy)
            self.dynamic_widget = QGridLayout()
            self.update_strategy(0)  # 初始化动态内容
        def update_strategy(self, index):
            # 清空动态布局
            self.clear_layout(self.dynamic_widget)
            # 根据不同策略添加不同的配置项
            if index == 1:  # PageLinks
                label_min_len = QLabel("最小聚集:")
                self.min_len_input = QLineEdit("8")
                
                label_auto_filter = QLabel("自动过滤:")
                self.auto_filter = self.create_QComboBox(["是", "否"])
                self.auto_filter.setFixedWidth(250)
                
                label_sequential = QLabel("连续爬取:")
                self.sequential = self.create_QComboBox(["是", "否"])
                self.sequential.setFixedWidth(250)

                self.dynamic_widget.addWidget(label_min_len, 0, 0)
                self.dynamic_widget.addWidget(self.min_len_input, 0, 1)
                self.dynamic_widget.addWidget(label_auto_filter, 0, 2)
                self.dynamic_widget.addWidget(self.auto_filter, 0, 3)
                self.dynamic_widget.addWidget(label_sequential, 1, 0)
                self.dynamic_widget.addWidget(self.sequential, 1, 1)

            elif index == 3:  # Object
                self.object_keys = QLineEdit()
                self.dynamic_widget.addWidget(QLabel("keys:"), 0, 0)
                self.dynamic_widget.addWidget(self.object_keys, 0, 1)
            elif index == 4:
                pass
            # 更新布局显示
            self.dynamic_widget.update()
        def clear_layout(self, layout):
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    self.clear_layout(child.layout())
        def create_QComboBox(self, items: list=None, default: int=0):
            qComboBox = QComboBox()
            qComboBox.addItems(items)
            qComboBox.setCurrentIndex(default)
            return qComboBox
        def addItems(self, level_layout: QVBoxLayout) -> QVBoxLayout:
            extract_layout = QHBoxLayout()
            label_extract = QLabel("提取策略:")
            label_extract.setFixedWidth(150)
            extract_layout.addWidget(label_extract)
            extract_layout.addWidget(self.extract_strategy)
            extract_personal_layout = QHBoxLayout()
            extract_personal_button = QPushButton("自定义")
            extract_personal_layout.addWidget(extract_personal_button)
            extract_personal_button.setFixedWidth(100)
            extract_layout.addWidget(extract_personal_button)
            extract_widget = QWidget()
            extract_widget.setLayout(extract_layout)
            extract_widget.setFixedHeight(80)
            level_layout.addWidget(extract_widget)
            level_layout.addLayout(self.dynamic_widget)
            return level_layout
        def get_extract_strategy(self):
            # ["自动识别", "PageLinks", "Text", " "Object", "LLVM", "无", "自定义"]
            # [0,              1,         2,       3,        4,      5,     6]
            index = self.extract_strategy.currentIndex()
            if index == 0:
                return True, None
            elif index == 1:
                return False, PageLinksExtractionStrategy(
                    min_len=int(self.min_len_input.text()),
                    auto_filter=True if self.auto_filter.currentIndex() == 0 else False,
                    sequential=True if self.sequential.currentIndex() == 0 else False
                )
            elif index == 2:
                return False, TextExtractionStrategy()
            elif index == 3:
                return False, ObjectExtractionStrategy(
                    objects=self.object_keys.text().split(',')
                )
            elif index == 4:
                return False, LLMExtractionStrategy()
            else:
                return False,  NoExtractionStrategy()

    def __init__(self):
        super().__init__()
        self.level_crawl1 = self.LevelCrawl()
        self.level_crawl2 = self.LevelCrawl()
        self.run_crawler = RunCrawler(
            crawler_strategy=RequestsCrawlerStrategy(),
            cache=False,
            report=False,
            new_crawl=False
        )
        self.second_level_data = {
            "titles": [], 
            "urls": []
        }
        self.initUI()
    def update_crawl_strategy(self, index):
        if index == 0:
            self.run_crawler.set_crawler_strategy(RequestsCrawlerStrategy())
    def update_cache(self, index):
        self.run_crawler.set_cache(
            True if index == 0 else False
        )
    def update_report(self, index):
        self.run_crawler.set_report(
            True if index == 0 else False
        )
    def update_new_crawl(self, index):
        self.run_crawler.set_new_crawl(
            True if index == 0 else False
        )
    def initUI(self):
        self.setFixedSize(1600, 900)
        self.setStyleSheet("""
            QWidget {
                font-family: '微软雅黑';
                font-size: 14pt;
            }
            QLineEdit, QTextEdit {
                border-radius: 10px;
                padding: 5px;
                border: 1px solid #ccc;
            }
            QPushButton {
                border-radius: 10px;
                padding: 5px;
                background-color: #0078d4;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QGroupBox {
                font-weight: bold;
                margin-top: 10px;
            }
            QLabel {
                margin-right: 10px;
            }
            QReadOnlyLabel {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                background-color: #f0f0f0;
            }
            QLineEdit {
                font-size: 15px;               
            }
            QTextEdit {
                font-size: 15px; 
            }
        """)

        # RunCrawler 启动器配置
        run_crawler_group = QGroupBox("RunCrawler 启动器配置")
        run_crawler_layout = QGridLayout()
        run_crawler_layout.setContentsMargins(0, 40, 0, 0)  # 设置底部间距为 20px
        
        label_crawl_strategy = QLabel("爬取策略:")
        label_crawl_strategy.setFixedWidth(120)
        self.crawl_strategy = self.create_QComboBox(["Requests"])
        self.crawl_strategy.setFixedWidth(200)
        self.crawl_strategy.currentIndexChanged.connect(self.update_crawl_strategy)

        label_cache = QLabel("启用缓存:")
        label_cache.setFixedWidth(120)
        self.cache = self.create_QComboBox(["是", "否"], 1)
        self.cache.currentIndexChanged.connect(self.update_cache)

        label_report = QLabel("报告展示:")
        label_report.setFixedWidth(120)
        self.report = self.create_QComboBox(["是", "否"], 1)
        self.report.currentIndexChanged.connect(self.update_report)

        label_newcrawl = QLabel("新的记录:")
        label_newcrawl.setFixedWidth(120)
        self.new_crawl = self.create_QComboBox(["是", "否"], 1)
        self.new_crawl.currentIndexChanged.connect(self.update_new_crawl)
        
        button_action = QPushButton("添加动作")
        button_proxy = QPushButton("设置代理")
        button_action.setFixedWidth(100)
        button_proxy.setFixedWidth(100)

        widgts = [label_crawl_strategy, self.crawl_strategy, label_cache, 
                  self.cache, label_report, self.report, label_newcrawl, self.new_crawl, button_proxy]
        self.addGridItems(
            run_crawler_layout, 0, [0, 1, 2, 3, 4, 5, 6, 7, 8], widgts
        )
        run_crawler_group.setLayout(run_crawler_layout)

        # 爬虫配置
        spider_group = QGroupBox("爬虫配置")
        spider_group.setFixedHeight(400)  # 设置固定高度为400像
        spider_layout = QGridLayout()
        spider_group.setLayout(spider_layout)
        spider_layout.setContentsMargins(0, 30, 0, 0)

        first_level_group = QGroupBox("一级爬虫配置")
        first_level_layout = QVBoxLayout()
        first_level_layout.setContentsMargins(0, 30, 0, 0)
        self.url_input = QLineEdit()
        url_layout = QHBoxLayout()
        label_url = QLabel("URL:")
        label_url.setFixedWidth(100)
        url_layout.addWidget(label_url)
        url_layout.addWidget(self.url_input)
        url_widget = QWidget()
        url_widget.setLayout(url_layout)
        url_widget.setFixedHeight(80)
        first_level_layout.addWidget(url_widget)
        first_level_layout = self.level_crawl1.addItems(first_level_layout)
        self.run_button_first = QPushButton("Run")
        self.run_button_first.clicked.connect(self.run_crawl_level1)
        # self.run_button.clicked.connect(self.handle_run_button)  # 连接按钮点击事件
        self.run_button_first.setFixedWidth(100)
        fixed_spacer = QSpacerItem(20, 100, QSizePolicy.Minimum, QSizePolicy.Fixed)
        first_level_layout.addItem(fixed_spacer)
        first_level_layout.addWidget(self.run_button_first) 
        first_level_group.setLayout(first_level_layout)

        second_level_group = QGroupBox("二级爬虫配置")
        second_level_layout = QGridLayout()
        second_level_layout.setContentsMargins(0, 30, 0, 0)
        # 创建一个两列的表格
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(2)  # 设置列数为2
        self.table_widget.setColumnWidth(0, 100)
        self.table_widget.setColumnWidth(1, 250)
        self.table_widget.setHorizontalHeaderLabels(["Title", "URL"])  # 设置表头
        # 添加示例数据
        self.fill_second_level_data()
        
        # 将表格添加到二级爬虫配置组
          # 将 QTableWidget 放入 QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.table_widget)  # 将 QTableWidget 设为滚动区域的内容
        scroll_area.setWidgetResizable(True)  # 使内容自适应大小
        
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)  # 始终显示垂直滚动条
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)  # 始终显示水平滚动条
        scroll_area.setMinimumWidth(400)
        scroll_area.setMaximumWidth(400)
        scroll_area.setFixedWidth(400)
        second_level_layout.addWidget(scroll_area, 0, 1)

        second_level_right_layout = QVBoxLayout()
        second_level_right_layout.setContentsMargins(0, 30, 0, 0)
        second_level_right_layout = self.level_crawl2.addItems(second_level_right_layout)    
        self.run_button_second = QPushButton("Run")
        # self.run_button.clicked.connect(self.handle_run_button)  # 连接按钮点击事件
        self.run_button_second.setFixedWidth(100)
        self.run_button_second.clicked.connect(self.run_crawl_level2)
        fixed_spacer = QSpacerItem(20, 100, QSizePolicy.Minimum, QSizePolicy.Fixed)

        # 将固定间距添加到布局中
        second_level_right_layout.addItem(fixed_spacer)

        # 将按钮添加到布局中，按钮会固定在距离顶部200像素的位置
        second_level_right_layout.addWidget(self.run_button_second) 
        second_level_layout.addLayout(second_level_right_layout, 0, 2)
        second_level_group.setLayout(second_level_layout)
        # spider_layout = QGridLayout()
        # 设置列的伸展因子
        first_level_group.setMinimumWidth(700)
        first_level_group.setMaximumWidth(700)

        second_level_group.setMinimumWidth(800)
        second_level_group.setMaximumWidth(800)

        spider_layout.addWidget(first_level_group, 0, 0)
        spider_layout.addWidget(second_level_group, 0, 1)
        spider_group.setLayout(spider_layout)

        # 结果展示
        result_group = QGroupBox("结果展示")
        result_layout = QVBoxLayout()
        result_layout.setContentsMargins(0, 30, 0, 0)

        result_menu_layout = QHBoxLayout()

        label_intime_refresh = QLabel("是否实时刷新:")
        label_save_as = QLabel("自动保存为:")
        label_save_path = QLabel("自定义保存路径:")

        self.intime_refresh = self.create_QComboBox(["是", "否"])
        self.save_as = self.create_QComboBox(["无", "json"])
        self.save_path = QLineEdit()
        self.btn_select_folder = QPushButton("选择文件夹", self)
        self.btn_select_folder.clicked.connect(self.open_folder_dialog)
        result_menu_layout.addWidget(label_intime_refresh)
        result_menu_layout.addWidget(self.intime_refresh)
        result_menu_layout.addWidget(label_save_as)
        result_menu_layout.addWidget(self.save_as)
        result_menu_layout.addWidget(label_save_path)
        result_menu_layout.addWidget(self.save_path)
        result_menu_layout.addWidget(self.btn_select_folder)

        result_layout.addLayout(result_menu_layout)

        # 左栏
        left_layout = QGridLayout()
        self.url_label = QLabel("URL: ")
        self.title_label = QLabel("Title: ")
        self.keywords_label = QLabel("Keywords: ")
        self.description_label = QLabel("Description: ")
        self.author_label = QLabel("Author: ")
        self.source_label = QLabel("Source: ")

        self.url_value = QTextEdit()
        self.url_value.setReadOnly(True)
        self.title_value = QTextEdit()
        self.title_value.setReadOnly(True)
        self.keywords_value = QTextEdit()
        self.keywords_value.setReadOnly(True)
        self.description_value = QTextEdit()
        self.description_value.setReadOnly(True)
        self.author_value = QTextEdit()
        self.author_value.setReadOnly(True)
        self.source_value = QTextEdit()
        self.source_value.setReadOnly(True)
    
        left_layout.addWidget(self.url_label, 0, 0)
        left_layout.addWidget(self.url_value, 0, 1)
        left_layout.addWidget(self.title_label, 1, 0)
        left_layout.addWidget(self.title_value, 1, 1)
        left_layout.addWidget(self.keywords_label, 2, 0)
        left_layout.addWidget(self.keywords_value, 2, 1)
        left_layout.addWidget(self.description_label, 3, 0)
        left_layout.addWidget(self.description_value, 3, 1)
        left_layout.addWidget(self.author_label, 4, 0)
        left_layout.addWidget(self.author_value, 4, 1)
        left_layout.addWidget(self.source_label, 5, 0)
        left_layout.addWidget(self.source_value, 5, 1)

        # 右栏
        right_layout = QVBoxLayout()
        self.res_text = QTextEdit()
        self.res_text.setReadOnly(True)

        right_layout.addWidget(self.res_text)

        # 结果展示布局
        display_layout = QHBoxLayout()
        display_layout.addLayout(left_layout, 3)
        display_layout.addLayout(right_layout, 7)
        result_layout.addLayout(display_layout)

        result_group.setLayout(result_layout)

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.addWidget(run_crawler_group)
        main_layout.addWidget(spider_group)
        main_layout.addWidget(result_group)

        self.setLayout(main_layout)
        self.setWindowTitle('Crawler321')
        self.show()
    def create_QComboBox(self, items: list=None, default: int=0):
        qComboBox = QComboBox()
        qComboBox.addItems(items)
        qComboBox.setCurrentIndex(default)
        return qComboBox
    def addGridItems(self, 
                     layout:QGridLayout,
                     row: int, 
                     coloums: list=[], 
                     items: list=[]
                    ) -> QGridLayout:
        idx = 0
        while idx < len(items):
            layout.addWidget(items[idx], row, coloums[idx])
            idx = idx + 1
        return layout
    def run_crawl_level1(self):
        # ["自动识别", "PageLinks", "Text", "XPaths", "Object", "LLVM", "无", "自定义"]
        url = self.url_input.text()
        auto_identify, extraction = self.level_crawl1.get_extract_strategy()
        result = self.run_crawler.run(
            url=url,
            auto_identify=auto_identify,
            extraction_strategy=extraction
        )
        result_dict = json.loads(result)
        if self.save_as.currentIndex() == 1:
            self.result_to_json(result)
        if self.intime_refresh.currentIndex() == 0:
            self.manifest_result(result_dict)
        if isinstance(extraction, PageLinksExtractionStrategy):
            self.second_level_data["urls"] = result_dict.get("res")["0"]["urls"]
            self.second_level_data["titles"] = result_dict.get("res")["0"]["titles"]
            self.fill_second_level_data()
    def run_crawl_level2(self):
        # ["自动识别", "PageLinks", "Text", "XPaths", "Object", "LLVM", "无", "自定义"]
        auto_identify, extraction = self.level_crawl2.get_extract_strategy()
        for url in self.second_level_data.get("urls"):
            result = self.run_crawler.run(
                url=url,
                auto_identify=auto_identify,
                extraction_strategy=extraction
            )
            result_dict = json.loads(result)
            if self.intime_refresh.currentIndex() == 0:
                self.manifest_result(result_dict)
    def manifest_result(self, result: dict):
        # 映射字段到控件
        fields_to_widgets = {
            "url": self.url_value,
            "title": self.title_value,
            "keywords": self.keywords_value,
            "description": self.keywords_value,
            "author": self.keywords_value,
            "source": self.keywords_value
        }
        # 遍历字段和对应控件
        for field, widget in fields_to_widgets.items():
            value = result.get(field)
            if value:
                widget.setPlainText(value)
        self.res_text.setPlainText(
            utf8_to_unicode(json.dumps(result.get("res"), indent=4))
        )
    def fill_second_level_data(self):
        # 设置行数（根据数据长度）
        num_rows = len(self.second_level_data["urls"])  # 假设 urls 和 titles 长度一致
        self.table_widget.setRowCount(num_rows)
        # 填充数据
        for row in range(num_rows):
            for col, key in enumerate(self.second_level_data.keys()):
                item = QTableWidgetItem(self.second_level_data[key][row])
                self.table_widget.setItem(row, col, item)
    def result_to_json(self, data: str):
        path = self.save_path.text()
        if not path:
            self.save_path.setText('Please select save path!')
        with open(os.path.join(path, "result.json"), "w+", encoding="UTF-8") as file:
            file.write(data)
    def open_folder_dialog(self):
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder:
            self.save_path.setText(folder)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())

# from PyQt5.QtWidgets import (
#     QApplication, QWidget, QVBoxLayout, QPushButton, QDialog, QLineEdit, QLabel, QHBoxLayout
# )

# class ConfigDialog(QDialog):
#     def __init__(self, parent=None):
#         super(ConfigDialog, self).__init__(parent)

#         self.setWindowTitle("Configuration")

#         # 创建布局
#         layout = QVBoxLayout()

#         # 添加自定义组件，例如文本框
#         self.config_input = QLineEdit(self)
#         layout.addWidget(QLabel("Enter configuration:"))
#         layout.addWidget(self.config_input)

#         # 创建确定和取消按钮
#         buttons_layout = QHBoxLayout()

#         self.ok_button = QPushButton("OK", self)
#         self.cancel_button = QPushButton("Cancel", self)
#         buttons_layout.addWidget(self.ok_button)
#         buttons_layout.addWidget(self.cancel_button)

#         # 添加按钮到主布局
#         layout.addLayout(buttons_layout)

#         # 设置布局
#         self.setLayout(layout)

#         # 连接按钮信号到槽函数
#         self.ok_button.clicked.connect(self.accept)
#         self.cancel_button.clicked.connect(self.reject)

#     def get_config(self):
#         return self.config_input.text()

# class MainWindow(QWidget):
#     def __init__(self):
#         super().__init__()

#         self.setWindowTitle("Main Window")

#         # 创建主布局
#         layout = QVBoxLayout()

#         # 显示选定的配置信息
#         self.config_label = QLabel("Current Configuration: None", self)
#         layout.addWidget(self.config_label)

#         # 创建按钮用于打开对话框
#         self.config_button = QPushButton("Open Config Dialog", self)
#         self.config_button.clicked.connect(self.open_config_dialog)
#         layout.addWidget(self.config_button)

#         # 设置布局
#         self.setLayout(layout)

#     def open_config_dialog(self):
#         # 创建并打开自定义对话框
#         dialog = ConfigDialog(self)

#         # 如果用户点击OK按钮
#         if dialog.exec_() == QDialog.Accepted:
#             config_value = dialog.get_config()
#             self.config_label.setText(f"Current Configuration: {config_value}")
#         else:
#             # 用户点击Cancel按钮，清空配置信息
#             self.config_label.setText("Current Configuration: None")

# # 创建应用程序
# app = QApplication([])

# # 创建并显示主窗口
# window = MainWindow()
# window.show()

# # 运行应用程序
# app.exec_()
