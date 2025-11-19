pyinstaller -F main.py ^
    --icon=Image/icon.png ^
    --add-data "Image;Image" ^
    --distpath dabao ^
    --name MyApp ^
    -w ^
    --clean
