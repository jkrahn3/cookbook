from recipes import *


if __name__ == '__main__':
    db.connect()
    Recipe.menu_loop()
