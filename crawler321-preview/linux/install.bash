python3 -m venv ./
mv ./crawler321/ ./lib/python3.10/site-packages/
mv ./crawler321-0.1.0.egg-info/ ./lib/python3.10/site-packages/

# shellcheck disable=SC1091
source bin/activate

# 安装依赖包
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
pip install --upgrade spark_ai_python -i https://pypi.tuna.tsinghua.edu.cn/simple/

mkdir chrome
cd chrome || exit
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install --fix-missing ./google-chrome-stable_current_amd64.deb

cd ..
rm -rf chrome