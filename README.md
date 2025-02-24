# Eureka

This game was build for the [Alakajam 21 Game Jam](https://alakajam.com/21st-alakajam/1595/eureka/) and the theme was **Gravity**!

A small but fun game inspired by **Isaac Newton's** discovery of gravity! The goal is to move the character to catch falling apples, but avoid other fruits. Who can get the highest score?

Using the left and right arrow keys, the player has 30 seconds to catch 10 apples (100 points). They will then move on to the next level, where the timer is reset and the speed of the falling fruits is slightly increased every time. If the player catches the wrong fruit, they will be immobilised for 2 seconds.


## Run locally
Install requirements from requirements.txt file
```
pip install -r requirements.txt
```

or install pygame directly
```
pip install pygame
```

Run with `python main.py`

## Compile locally
Windows firewall might complain, so you might have to disable firewall or antivirus

Install the requirements + `pyinstaller`
```
pip install -r requirements.txt
pip install pyinstaller
```

Use the following command to compile to an `.exe` file
```
pyinstaller --onefile --windowed --add-data "assets:assets" --hidden-import pygame --name Eureka main.py
```

This will generate a `dist` folder, copy the `assets` folder inside the `dist` folder and run the `Eureka.exe` file