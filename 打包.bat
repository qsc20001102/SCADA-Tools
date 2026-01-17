pyinstaller -F main.py ^
    --icon=Image/icon.png ^
    --add-data "Image;Image" ^
    --distpath dabao ^
    --name SCADA-Tools^
    -w ^
    --clean
