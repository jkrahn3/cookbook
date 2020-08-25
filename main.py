from recipes import *
from ingredients import *
from main_menu import *
from modify_recipes import *


if __name__ == '__main__':
    db.connect()
    # db.create_tables([Recipe], safe=True)
    # add_test_recipes()
    menu_loop()
    # print_recipe('black bean enchiladas')
    # try:
    # except IntegrityError:
    #     print(f'Recipe test already exists')
    # add_recipe()
