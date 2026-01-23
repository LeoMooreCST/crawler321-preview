pyinstaller --onefile --noconsole --add-data "./crawler321/models;models" --name "crawler321" --specpath . --distpath ./dist --workpath ./build ./crawler321/main.py
pyinstaller crawler321.spec