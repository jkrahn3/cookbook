from collections import OrderedDict
import json
from peewee import DoesNotExist

from recipes import Recipe
from menu import DocStringMenu, RecipeMenu

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


def initialize():
    db.connect()
    db.create_tables([Recipe], safe=True)


def menu_loop():
    main_menu_options = (
        view_recipes,
        search_recipes,
        print_ingredients,
        show_whole_recipe,
        add_recipe,
        modify_recipe,
        delete_recipe,
    )

    main_menu = DocStringMenu(main_menu_options)
    main_menu.loop_menu()


def modify_recipe(*args, **kwargs):
    """Modify recipe"""
    modify_recipe_options = (
        update_name,
        modify_ingredients,
        update_prep_time,
        update_cook_time,
        update_instructions,
    )
    recipe = select_recipe()
    mod_recipe_menu = RecipeMenu(
        modify_recipe_options)

    loop_dict = {
        'kwargs_to_refresh': {'recipe': recipe},
        'run_before': show_whole_recipe,
        'run_after': refresh_recipe,

    }
    mod_recipe_menu.loop_menu(**loop_dict)


def modify_ingredients(*args, **kwargs):
    """Add, delete, or modify ingredients"""
    recipe = kwargs.get('recipe')
    modify_ingredients_options = (
        add_ingredient,
        delete_ingredient,
        modify_ingredient,
    )

    mod_ingr_menu = RecipeMenu(
        modify_ingredients_options)
    loop_dict = {
        'kwargs_to_refresh': {'recipe': recipe},
        'run_before': print_ingredients,
        'run_after': refresh_recipe,
    }
    mod_ingr_menu.loop_menu(**loop_dict)


def mod_one_ingr_menu_loop(recipe, ingr_json, idx):
    """Menu to decide what part of an ingredient to modify"""
    mod_one_ingr_options = (
        mod_ingr_name,
        mod_ingr_amount,
        mod_ingr_prep,
        mod_ingr_opt,
    )

    mod_one_ingr_menu = RecipeMenu(
        mod_one_ingr_options)

    ingr_name = ingr_json[idx].get('ingredient_name')
    run_before = show_ingr(ingr_json[idx], idx + 1)
    run_after = refresh_recipe

    loop_dict = {
        'kwargs_to_refresh': {'recipe': recipe,
                              'ingr_json': ingr_json,
                              'idx': idx},
        'run_before': print_ingredients,
        'run_after': refresh_ingr,
    }
    mod_one_ingr_menu.loop_menu(**loop_dict)


def select_recipe():
    recipe = None
    while recipe == None:
        recipe_name = input(
            '\n\nWhich recipe? Enter recipe id or recipe name:  ')
        try:
            recipe = Recipe.get(Recipe.id == recipe_name)
        except DoesNotExist:
            try:
                recipe = Recipe.get(Recipe.name == recipe_name)
            except (DoesNotExist, NameError):
                view_recipes()
                print('\nThis recipe does not exist. Try again.')
    return recipe


def view_recipes(search_query=None):
    """Show recipe names"""
    recipes = Recipe.select()
    if search_query:
        recipes = recipes.where(Recipe.ingredient_list.contains(search_query))
    print('\n\n id - name')
    for recipe in recipes:
        print(f'{str(recipe.id).rjust(3)} - {recipe.name}')
    print('\r\r')


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


def refresh_recipe(*args, **kwargs):
    recipe = kwargs.get('recipe')
    return {'recipe': Recipe.get_by_id(recipe.id)}


def refresh_ingr(*args, **kwargs):
    recipe = refresh_recipe(**kwargs).get('recipe')
    kwargs['recipe'] = recipe
    return kwargs


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


def update_name(*args, **kwargs):
    """Update name"""
    recipe = kwargs.get('recipe')
    update_field(recipe, field='name')


def print_ingredients(print_ingr=True, *args, **kwargs):
    """Show ingredients with details"""
    recipe = kwargs.get('recipe')
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


def show_ingr(ingr_to_print, idx, *args, **kwargs):
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


def add_ingredient(*args, **kwargs):
    """Add ingredient"""
    recipe = kwargs.get('recipe')
    _, ingr_json = print_ingredients(print_ingr=False, *args, **kwargs)
    new_ingr = set_ingredient_details()
    if input(f'Add {new_ingr.get("ingredient_name")}? [Y/n]:  ') != 'n':
        ingr_json.append(new_ingr)
        Recipe.update(ingredient_list=json.dumps(ingr_json)).where(
            Recipe.name == recipe.name).execute()


def delete_ingredient(*args, **kwargs):
    """Delete ingredient"""
    recipe = kwargs.get('recipe')
    _, ingr_json = print_ingredients(print_ingr=False, *args, **kwargs)
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


def modify_ingredient(*args, **kwargs):
    """Modify ingredient"""
    recipe = kwargs.get('recipe')
    _, ingr_json = _, ingr_json = print_ingredients(
        print_ingr=False, *args, **kwargs)
    ingr_to_del = input('What is the index of the ingredient to modify?:  ')
    try:
        idx_to_mod = int(ingr_to_del) - 1
    except ValueError:
        print('\nNeed to enter a number!')
    else:
        mod_one_ingr_menu_loop(recipe, ingr_json, idx_to_mod)


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


def mod_ingr_prep(recipe, ingr_json, idx):
    """Change prep."""
    new_prep = input(
        f'Enter new prep for {ingr_json[idx].get("ingredient_name")}:  ')
    ingr_json[idx].update({'prep': new_prep})
    update_field(recipe, 'ingredient list', ingr_json)


def mod_ingr_opt(recipe, ingr_json, idx):
    """Change optional."""
    new_opt = False
    if input(f'Is {ingr_json[idx].get("ingredient_name")} optional? [y/N]:  ') == 'y':
        new_opt = True
    ingr_json[idx].update({'optional': new_opt})
    update_field(recipe, 'ingredient list', ingr_json)


def update_prep_time(*args, **kwargs):
    """Update prep time"""
    recipe = kwargs.get('recipe')
    update_field(recipe, field='prep time')


def update_cook_time(*args, **kwargs):
    """Update cook time"""
    recipe = kwargs.get('recipe')
    update_field(recipe, field='cook time')


def update_instructions(*args, **kwargs):
    """Update instructions"""
    recipe = kwargs.get('recipe')
    update_field(recipe, field='instructions')


def show_whole_recipe(*args, **kwargs):
    """Show whole recipe"""
    recipe = kwargs.get('recipe')
    if recipe == None:
        recipe = select_recipe()
    print(f'\nRecipe: {recipe.name}')
    print(f'Prep Time: {recipe.prep_time}')
    print(f'Cook Time: {recipe.cook_time}\n')
    print(f'Ingredients:')
    print_ingredients(recipe=recipe)
    print(f'Instructions: {recipe.instructions}\n')


def add_recipe():
    """Add new recipe"""
    ingredient_list = []
    name = input('Enter the recipe name: ').strip()

    run = True
    while run:
        if input('Add an ingredient? [y/N]:  ').lower() == 'y':
            ingredient_list.append(set_ingredient_details())
        else:
            run = False

    if input(f'Save {name} recipe? [Y/n]:  ').lower() != 'n':
        Recipe.create(name=name, ingredient_list=json.dumps(ingredient_list))


def delete_recipe():
    """Delete recipe"""
    recipe = select_recipe()
    if recipe is not None:
        if input(f'Delete {recipe.name}? [y/N]:  ').lower() == 'y':
            recipe.delete_instance()
            print("recipe deleted")


def add_test_recipes():
    Recipe.create(name='garlic bread', ingredient_list=json.dumps(
        test_recipes.garlic_bread_ingredients))
    Recipe.create(name='black bean enchiladas', ingredient_list=json.dumps(
        test_recipes.black_bean_enchiladas_ingredients))


def search_recipes():
    """Search for recipes by ingredient"""
    view_recipes(input('Search ingredients:  '))
