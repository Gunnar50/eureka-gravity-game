# Eureka

## Run locally
Install requirements from requirements.txt file
```
pip install -r requirements
```

or install pygame directly
```
pip install pygame
```

Run with `python main.py`

## Compile locally
Windows firewall might complain, so you might have to disable firewall or antivirus

Install `pyinstaller`
```
pip install pyinstaller
```


Use the following command to compile to an `.exe` file
```
pyinstaller --onefile --windowed --add-data "assets:assets" --hidden-import pygame --name Eureka main.py
```

This will generate a `dist` folder, copy the `assets` folder inside the `dist` folder and run the `Eureka.exe` file