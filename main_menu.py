import json
from collections import OrderedDict
from peewee import *
from modify_recipes import *
from recipes import Recipe


def initialize():
    db.connect()
    db.create_tables([Recipe], safe=True)


def menu_loop():
    """Show the menu"""
    choice = None
    while choice != 'q':
        for key, value in menu.items():
            print(f'{key}) {value.__doc__}')
        print('q) Quit')
        choice = input('\nAction: ').lower().strip()

        if choice in menu:
            menu[choice]()


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

    save_input = input(f'Save {name} recipe? [Y/n]:  ').strip()
    if save_input.lower() == 'y':
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


def view_recipes(search_query=None):
    """Show recipe names"""
    recipes = Recipe.select()
    if search_query:
        recipes = recipes.where(Recipe.ingredient_list.contains(search_query))
    print('\n\n id - name')
    for recipe in recipes:
        print(f'{str(recipe.id).rjust(3)} - {recipe.name}')
    print('\r\r')


def show_whole_recipe():
    """Show whole recipe"""
    recipe = select_recipe()
    print(f'\nRecipe: {recipe.name}')
    print(f'Prep Time: {recipe.prep_time}')
    print(f'Cook Time: {recipe.cook_time}\n')
    print(f'Ingredients:')
    print_recipe(recipe=recipe)
    print(f'Instructions: {recipe.instructions}\n')


def search_recipes():
    """Search for recipes by ingredient"""
    view_recipes(input('Search ingredients:  '))


menu = OrderedDict([
    ('1', view_recipes),
    ('2', search_recipes),
    ('3', get_ingredients),
    ('4', print_recipe),
    ('5', show_whole_recipe),
    ('6', add_recipe),
    ('7', modify_recipe),
    ('8', delete_recipe),
])
