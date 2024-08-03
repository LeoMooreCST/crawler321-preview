python -m venv ./
.\Scripts\activate
mv .\crawler321\ .\Lib\site-packages\
mv .\crawler321-0.1.0.dist-info\ .\Lib\site-packages\
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/      
pip install --upgrade spark_ai_python -i https://pypi.tuna.tsinghua.edu.cn/simple/
