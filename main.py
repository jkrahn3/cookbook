from recipes import *
from ingredients import *
from main_menu import *
from modify_recipes import *


# mod_one_ingr_menu = (
#     mod_ingr_name),
#     mod_ingr_amount),
#     mod_ingr_prep),
#     mod_ingr_opt),
# )


# modify_ingredients_menu=(
#      add_ingredient),
#      delete_ingredient),
#      modify_ingredient),
# )


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
