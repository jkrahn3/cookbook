from recipes import *
from modify_recipes import menu_loop


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
