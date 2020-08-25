from collections import OrderedDict
import json
from peewee import DoesNotExist
from recipes import Recipe


IDX_HEADER_WIDTH = 7
INGR_HEADER_WIDTH = 40
AMT_HEADER_WIDTH = 10
UNIT_HEADER_WIDTH = 10
PREP_HEADER_WIDTH = 30
OPT_HEADER_WIDTH = 10

idx_header_str = 'Index'.center(IDX_HEADER_WIDTH)
ingr_header_str = 'Ingredient'.center(INGR_HEADER_WIDTH)
amt_header_str = 'Amount'.center(AMT_HEADER_WIDTH)
unit_header_str = 'Unit'.center(UNIT_HEADER_WIDTH)
prep_header_str = 'Prep'.center(PREP_HEADER_WIDTH)
opt_header_str = 'Optional'.center(OPT_HEADER_WIDTH)

ING_HEADER_STR = f'|{idx_header_str}|{ingr_header_str}|{amt_header_str}|{unit_header_str}|{prep_header_str}|{opt_header_str}|\n'


def select_recipe():
    recipe = None
    recipe_name = input('\n\nWhich recipe? Enter recipe id or recipe name:  ')
    try:
        recipe = Recipe.get(Recipe.id == recipe_name)
    except DoesNotExist:
        try:
            recipe = Recipe.get(Recipe.name == recipe_name)
        except (DoesNotExist, NameError):
            print('\n\nThis recipe does not exist. Try again.\n\n')
    return recipe


def set_ingredient_details():
    """User input to set parameters for an ingredient"""
    ingredient_name = input('Enter name of ingredient:  ').strip()
    ingredient_units = input(
        f'Enter unit of measurement for {ingredient_name} (e.g. tsp or cup):  ').strip()
    ingredient_amount = input(
        f'Enter number of {ingredient_units} for {ingredient_name}:  ').strip()
    prep = input(
        f'Enter any required prep for {ingredient_name} such as skinned or minced:  ').strip()
    if input(f'Is {ingredient_name} optional? [Y/n]:  ').lower() == 'y':
        optional = True
    else:
        optional = False

    ingredient_dict = {
        "ingredient_name": ingredient_name,
        "ingredient_amount": ingredient_amount,
        "ingredient_units": ingredient_units,
        "optional": optional,
        "prep": prep,
    }

    return ingredient_dict


def modify_recipe():
    """Modify recipe"""
    choice = None
    recipe = select_recipe()
    while choice != 'q':
        print(f'\n{recipe.name} selected. Choose next action\n')
        for key, value in modify_recipe_menu.items():
            print(f'{key}) {value.__doc__}')
        print('q) quit to main menu')
        choice = input('\nAction:  ')
        if choice in modify_recipe_menu:
            modify_recipe_menu[choice](recipe)
            recipe = refresh_recipe(recipe)


def refresh_recipe(recipe_id):
    return Recipe.get_by_id(recipe_id)


def update_field(recipe, field, updated_field=None):
    """Update field for row of database. Input is recipe and
    which field to update such as recipe.name or recipe.prep_time.
    """
    if field != 'ingredient list':
        updated_field = input(
            f'\n\nEnter the new {field}:  ')

    choices = {
        'name': (recipe.name, recipe.update(name=updated_field).where(Recipe.name == recipe.name)),
        'ingredient list': (recipe.ingredient_list, recipe.update(ingredient_list=json.dumps(updated_field)).where(Recipe.name == recipe.name)),
        'prep time': (recipe.prep_time, recipe.update(prep_time=updated_field).where(Recipe.name == recipe.name)),
        'cook time': (recipe.cook_time, recipe.update(cook_time=updated_field).where(Recipe.name == recipe.name)),
        'instructions': (recipe.instructions, recipe.update(instructions=updated_field).where(Recipe.name == recipe.name)),
    }

    original_value = choices.get(field)[0]

    if input(f'Change {field} from {original_value} to {updated_field}? [y/N]:  ').lower() == 'y':
        choices.get(field)[1].execute()
        print(f'{recipe.name} updated successfully')
    else:
        print(f'{recipe.name} not updated')


def update_name(recipe):
    """Update name"""
    update_field(recipe, field='name')


def update_ingredients(recipe):
    """Add, delete, or modify ingredients"""
    choice = None
    print_recipe(recipe)
    while choice != 'q':
        print(f'\n\n{recipe.name} selected. Choose next action\n')
        for key, value in modify_ingredients_menu.items():
            print(f'{key}) {value.__doc__}')
        print('q) quit to main menu')
        choice = input('\nAction:  ')
        if choice in modify_ingredients_menu:
            modify_ingredients_menu[choice](recipe)


def get_ingredients(recipe=None):
    """Show ingredients"""
    if recipe is None:
        recipe = select_recipe()
    ingr_json = json.loads(recipe.ingredient_list)
    print('\r\r')
    for idx, item in enumerate(ingr_json, 1):
        print(f'{str(idx).rjust(2)} - {item.get("ingredient_name")}')
    print('\r\r')
    return ingr_json


def print_recipe(recipe=None, print_ingr=True):
    """Show ingredients with details"""
    if recipe is None:
        recipe = select_recipe()
    ingr_json = json.loads(recipe.ingredient_list)

    ingr_str = ING_HEADER_STR
    ingr_str += '=' * (len(ING_HEADER_STR) - 1) + '\n'
    for idx, item in enumerate(ingr_json, 1):
        ingr_str += show_ingr(item, idx)
    if print_ingr:
        print(f'\n{ingr_str}')
    return ingr_str, ingr_json


def show_ingr(ingr_to_print, idx):
    """Prints one ingredient with detals. Takes one ingredient dict"""
    idx_str = str(idx).rjust(IDX_HEADER_WIDTH-1)
    name_str = str(ingr_to_print.get('ingredient_name')
                   ).center(INGR_HEADER_WIDTH)
    amt_str = str(ingr_to_print.get('ingredient_amount')
                  ).center(AMT_HEADER_WIDTH)
    unit_str = str(ingr_to_print.get('ingredient_units')
                   ).center(UNIT_HEADER_WIDTH)
    prep_str = str(ingr_to_print.get('prep')).center(PREP_HEADER_WIDTH)
    opt_str = ('y'.center(OPT_HEADER_WIDTH) if ingr_to_print.get(
        'optional') else 'n'.center(OPT_HEADER_WIDTH))
    ingr_str = f'|{idx_str} |{name_str}|{amt_str}|{unit_str}|{prep_str}|{opt_str}|\n'
    return ingr_str


def add_ingredient(recipe):
    """Add ingredient"""
    _, ingr_json = print_recipe(recipe, print_ingr=False)
    new_ingr = set_ingredient_details()
    ingr_json.append(new_ingr)
    Recipe.update(ingredient_list=json.dumps(ingr_json)).where(
        Recipe.name == recipe.name).execute()
    pass


def delete_ingredient(recipe):
    """Delete ingredient"""
    _, ingr_json = print_recipe(recipe, print_ingr=False)
    ingr_to_del = input('What is the index of the ingredient to delete?:  ')
    try:
        idx_to_del = int(ingr_to_del) - 1
    except ValueError:
        print('\nNeed to enter a number!')
    else:
        ingr_to_del = ingr_json.pop(idx_to_del).get('ingredient_name')
        if input(f'Delete {ingr_to_del}? [y/N]:  '):
            Recipe.update(ingredient_list=json.dumps(ingr_json)).where(
                Recipe.name == recipe.name).execute()


def modify_ingredient(recipe):
    """Modify ingredient"""
    _, ingr_json = print_recipe(recipe, print_ingr=False)
    ingr_to_del = input('What is the index of the ingredient to modify?:  ')
    try:
        idx_to_mod = int(ingr_to_del) - 1
    except ValueError:
        print('\nNeed to enter a number!')
    else:
        mod_one_ingr_menu_loop(recipe, ingr_json, idx_to_mod)


def mod_one_ingr_menu_loop(recipe, ingr_json, idx):
    """Menu to decide what part of an ingredient to modify"""
    choice = None
    print(ING_HEADER_STR[:-1])
    print(show_ingr(ingr_json[idx], idx + 1))
    ingr_name = ingr_json[idx].get("ingredient_name")
    while choice != 'q':
        print(
            f'\n\n{ingr_name} selected. Choose next action\n')
        for key, value in mod_one_ingr_menu.items():
            print(f'{key}) {value.__doc__}')
        print('q) quit to main menu')
        choice = input('\nAction:  ')
        if choice in mod_one_ingr_menu:
            mod_one_ingr_menu[choice](recipe, ingr_json, idx)


def mod_ingr_name(recipe, ingr_json, idx):
    """Change name."""
    new_name = input(
        f'Enter new name for {ingr_json[idx].get("ingredient_name")}:  ')
    ingr_json[idx].update({'ingredient_name': new_name})
    update_field(recipe, 'ingredient list', ingr_json)


def mod_ingr_amount(recipe, ingr_json, idx):
    """Change amount and unit."""
    new_amount = input(
        f'Enter new amount for {ingr_json[idx].get("ingredient_name")}:  ')
    new_unit = input(
        f'Enter new units for {ingr_json[idx].get("ingredient_name")}:  ')
    ingr_json[idx].update({'ingredient_amount': new_amount})
    ingr_json[idx].update({'ingredient_units': new_unit})
    update_field(recipe, 'ingredient list', ingr_json)
    pass


def mod_ingr_prep(recipe, ingr_json, idx):
    """Change prep."""
    new_prep = input(
        f'Enter new prep for {ingr_json[idx].get("ingredient_name")}:  ')
    ingr_json[idx].update({'prep': new_prep})
    update_field(recipe, 'ingredient list', ingr_json)
    pass


def mod_ingr_opt(recipe, ingr_json, idx):
    """Change optional."""
    new_opt = False
    if input(f'Is {ingr_json[idx].get("ingredient_name")} optional? [y/N]:  ') == 'y':
        new_opt = True
    ingr_json[idx].update({'optional': new_opt})
    update_field(recipe, 'ingredient list', ingr_json)
    pass


mod_one_ingr_menu = OrderedDict([
    ('1', mod_ingr_name),
    ('2', mod_ingr_amount),
    ('3', mod_ingr_prep),
    ('4', mod_ingr_opt),


])


modify_ingredients_menu = OrderedDict([
    ('1', add_ingredient),
    ('2', delete_ingredient),
    ('3', modify_ingredient),
])


def update_prep_time(recipe):
    """Update prep time"""
    update_field(recipe, field='prep time')


def update_cook_time(recipe):
    """Update cook time"""
    update_field(recipe, field='cook time')


def update_instructions(recipe):
    """Update instructions"""
    update_field(recipe, field='instructions')


modify_recipe_menu = OrderedDict([
    ('1', update_name),
    ('2', update_ingredients),
    ('3', update_prep_time),
    ('4', update_cook_time),
    ('5', update_instructions),
])
