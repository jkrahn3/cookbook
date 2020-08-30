from menu import DocStringMenu, RecipeMenu
import datetime
import json

from collections import OrderedDict
from peewee import *

db = SqliteDatabase('recipes.db')


class Recipe(Model):
    name = TextField()
    date_created = DateTimeField(default=datetime.datetime.now)
    ingredient_list = TextField()
    prep_time = TimeField(null=True)
    cook_time = TimeField(null=True)
    instructions = TextField(null=True)

    class Meta:
        database = db
        db_table = 'recipes'

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

    @staticmethod
    def initialize():
        db.connect()
        db.create_tables([Recipe], safe=True)

    @classmethod
    def menu_loop(cls):
        """Main program loop. Displays menu to create, read, update, or delete recipes"""
        main_menu_options = (
            cls.view_recipes,
            cls.search_recipes,
            cls.print_ingredients,
            cls.show_whole_recipe,
            cls.add_recipe,
            cls.modify_recipe,
            cls.delete_recipe,
        )

        main_menu = DocStringMenu(main_menu_options)
        main_menu.loop_menu()

    @classmethod
    def modify_recipe(cls, *args, **kwargs):
        """Modify recipe.
        Menu to select options for modifying a single recipe.
        """
        modify_recipe_options = (
            cls.update_name,
            cls.modify_ingredients,
            cls.update_prep_time,
            cls.update_cook_time,
            cls.update_instructions,
        )
        recipe = cls.select_recipe()
        mod_recipe_menu = RecipeMenu(
            modify_recipe_options)

        loop_dict = {
            'kwargs_to_refresh': {'recipe': recipe},
            'run_before': cls.show_whole_recipe,
            'run_after': cls.refresh_recipe,

        }
        mod_recipe_menu.loop_menu(**loop_dict)

    @classmethod
    def modify_ingredients(cls, *args, **kwargs):
        """Add, delete, or modify ingredients.
        Menu for modifying the ingredients of a recipe

        Required parameter: 'recipe' in kwargs
        """
        recipe = kwargs.get('recipe')
        modify_ingredients_options = (
            cls.add_ingredient,
            cls.delete_ingredient,
            cls.modify_ingredient,
        )

        mod_ingr_menu = RecipeMenu(
            modify_ingredients_options)
        loop_dict = {
            'kwargs_to_refresh': {'recipe': recipe},
            'run_before': cls.print_ingredients,
            'run_after': cls.refresh_recipe,
        }
        mod_ingr_menu.loop_menu(**loop_dict)

    @classmethod
    def mod_one_ingr_menu_loop(cls, recipe, ingr_json, idx):
        """Menu to decide what part of an ingredient to modify."""
        mod_one_ingr_options = (
            cls.mod_ingr_name,
            cls.mod_ingr_amount,
            cls.mod_ingr_prep,
            cls.mod_ingr_opt,
        )

        mod_one_ingr_menu = RecipeMenu(
            mod_one_ingr_options)

        ingr_name = ingr_json[idx].get('ingredient_name')

        loop_dict = {
            'kwargs_to_refresh': {'recipe': recipe,
                                  'ingr_json': ingr_json,
                                  'idx': idx},
            'run_before': cls.print_ingredients,
            'run_after': cls.refresh_ingr,
        }
        mod_one_ingr_menu.loop_menu(**loop_dict)

    @classmethod
    def select_recipe(cls):
        """User dialog to select a recipe. Loops if invalid input is given."""
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
                    cls.view_recipes()
                    print('\nThis recipe does not exist. Try again.')
        return recipe

    @staticmethod
    def view_recipes(search_query=None):
        """Show recipe names.
        Prints recipe names with their respective ids

        Parameter: search_query (not required)
                    pass in string as input to only display
                    recipes that contain that string in the
                    ingredients list.
        """
        recipes = Recipe.select()
        if search_query:
            recipes = recipes.where(
                Recipe.ingredient_list.contains(search_query))
        print('\n\n id - name')
        for recipe in recipes:
            print(f'{str(recipe.id).rjust(3)} - {recipe.name}')
        print('\r\r')

    @staticmethod
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
            'ingredient_name': ingredient_name,
            'ingredient_amount': ingredient_amount,
            'ingredient_units': ingredient_units,
            'optional': optional,
            'prep': prep,
        }

        return ingredient_dict

    @staticmethod
    def refresh_recipe(*args, **kwargs):
        """Updates recipe for displaying new changes."""
        recipe = kwargs.get('recipe')
        return {'recipe': Recipe.get_by_id(recipe.id)}

    @classmethod
    def refresh_ingr(cls, *args, **kwargs):
        """Updates recipe and preserves kwargs for displaying new changes to ingredients."""
        recipe = cls.refresh_recipe(**kwargs).get('recipe')
        kwargs['recipe'] = recipe
        return kwargs

    @staticmethod
    def update_field(recipe, field, updated_field=None):
        """Modifies one field of a recipe in the database. 

        Parameters:
            recipe - recipe to modify
            field - string representing what field to modify. Choose from:
                'name'
                'ingredient list'
                'prep time'
                'cook time'
                'instructions'
            updated field - new value to update to. Only needed for modifying ingredients.
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

    @classmethod
    def update_name(cls, *args, **kwargs):
        """Update recipe name."""
        recipe = kwargs.get('recipe')
        cls.update_field(recipe, field='name')

    @classmethod
    def print_ingredients(cls, print_ingr=True, *args, **kwargs):
        """Show ingredients.
        Prints formatted table of all ingredients with ingredient details."""
        recipe = kwargs.get('recipe')
        if recipe is None:
            recipe = cls.select_recipe()
        ingr_json = json.loads(recipe.ingredient_list)

        ingr_str = cls.ING_HEADER_STR
        ingr_str += '=' * (len(cls.ING_HEADER_STR) - 1) + '\n'
        for idx, item in enumerate(ingr_json, 1):
            ingr_str += cls.show_ingr(item, idx)
        if print_ingr:
            print(f'\n{ingr_str}')
        return ingr_str, ingr_json

    @classmethod
    def show_ingr(cls, ingr_to_print, idx, *args, **kwargs):
        """Returns formatted table of one ingredient with detals.
        Takes dict for single ingredient.
        """
        idx_str = str(idx).rjust(cls.IDX_HEADER_WIDTH-1)
        name_str = str(ingr_to_print.get('ingredient_name')
                       ).center(cls.INGR_HEADER_WIDTH)
        amt_str = str(ingr_to_print.get('ingredient_amount')
                      ).center(cls.AMT_HEADER_WIDTH)
        unit_str = str(ingr_to_print.get('ingredient_units')
                       ).center(cls.UNIT_HEADER_WIDTH)
        prep_str = str(ingr_to_print.get('prep')).center(cls.PREP_HEADER_WIDTH)
        opt_str = ('y'.center(cls.OPT_HEADER_WIDTH) if ingr_to_print.get(
            'optional') else 'n'.center(cls.OPT_HEADER_WIDTH))
        ingr_str = f'|{idx_str} |{name_str}|{amt_str}|{unit_str}|{prep_str}|{opt_str}|\n'
        return ingr_str

    @classmethod
    def add_ingredient(cls, *args, **kwargs):
        """Add ingredient.
        Adds an ingredient to a recipe.

        Parameters required: 'recipe' in kwargs
        """

        recipe = kwargs.get('recipe')
        _, ingr_json = cls.print_ingredients(print_ingr=False, *args, **kwargs)
        new_ingr = cls.set_ingredient_details()
        if input(f'Add {new_ingr.get("ingredient_name")}? [Y/n]:  ') != 'n':
            ingr_json.append(new_ingr)
            Recipe.update(ingredient_list=json.dumps(ingr_json)).where(
                Recipe.name == recipe.name).execute()

    @classmethod
    def delete_ingredient(cls, *args, **kwargs):
        """Delete ingredient.
        Deletes one ingredient from a recipe.
        Asks for confirmation before executing.

        Parameter required: 'recipe' in kwargs
        """

        recipe = kwargs.get('recipe')
        _, ingr_json = cls.print_ingredients(print_ingr=False, *args, **kwargs)
        ingr_to_del = input(
            'What is the index of the ingredient to delete?:  ')
        try:
            idx_to_del = int(ingr_to_del) - 1
            ingr_to_del = ingr_json.pop(idx_to_del).get('ingredient_name')
        except (ValueError, IndexError):
            print('\nEnter a valid number!')
        else:
            if input(f'Delete {ingr_to_del}? [y/N]:  '):
                Recipe.update(ingredient_list=json.dumps(ingr_json)).where(
                    Recipe.name == recipe.name).execute()

    @classmethod
    def modify_ingredient(cls, *args, **kwargs):
        """Modify ingredient.
        Select an ingredient, then start a menu to choose how to modify it.
        """
        recipe = kwargs.get('recipe')
        _, ingr_json = _, ingr_json = cls.print_ingredients(
            print_ingr=False, *args, **kwargs)
        ingr_to_del = input(
            'What is the index of the ingredient to modify?:  ')
        try:
            idx_to_mod = int(ingr_to_del) - 1
            cls.mod_one_ingr_menu_loop(recipe, ingr_json, idx_to_mod)
        except (ValueError, IndexError):
            print('\nNeed to enter a number in range!')

    @classmethod
    def mod_ingr_name(cls, recipe, ingr_json, idx):
        """Change ingredient name."""
        new_name = input(
            f'Enter new name for {ingr_json[idx].get("ingredient_name")}:  ')
        ingr_json[idx].update({'ingredient_name': new_name})
        cls.update_field(recipe, 'ingredient list', ingr_json)

    @classmethod
    def mod_ingr_amount(cls, recipe, ingr_json, idx):
        """Change ingredient amount and unit."""
        new_amount = input(
            f'Enter new amount for {ingr_json[idx].get("ingredient_name")}:  ')
        new_unit = input(
            f'Enter new units for {ingr_json[idx].get("ingredient_name")}:  ')
        ingr_json[idx].update({'ingredient_amount': new_amount})
        ingr_json[idx].update({'ingredient_units': new_unit})
        cls.update_field(recipe, 'ingredient list', ingr_json)

    @classmethod
    def mod_ingr_prep(cls, recipe, ingr_json, idx):
        """Change ingredient prep."""
        new_prep = input(
            f'Enter new prep for {ingr_json[idx].get("ingredient_name")}:  ')
        ingr_json[idx].update({'prep': new_prep})
        cls.update_field(recipe, 'ingredient list', ingr_json)

    @classmethod
    def mod_ingr_opt(cls, recipe, ingr_json, idx):
        """Change if ingredient is optional."""
        new_opt = False
        if input(f'Is {ingr_json[idx].get("ingredient_name")} optional? [y/N]:  ') == 'y':
            new_opt = True
        ingr_json[idx].update({'optional': new_opt})
        cls.update_field(recipe, 'ingredient list', ingr_json)

    @classmethod
    def update_prep_time(cls, *args, **kwargs):
        """Update recipe prep time."""
        recipe = kwargs.get('recipe')
        cls.update_field(recipe, field='prep time')

    @classmethod
    def update_cook_time(cls, *args, **kwargs):
        """Update recipe cook time."""
        recipe = kwargs.get('recipe')
        cls.update_field(recipe, field='cook time')

    @classmethod
    def update_instructions(cls, *args, **kwargs):
        """Update recipe instructions."""
        recipe = kwargs.get('recipe')
        cls.update_field(recipe, field='instructions')

    @classmethod
    def show_whole_recipe(cls, *args, **kwargs):
        """Show whole recipe.
        Prints the recipe name, prep time, and cook time,
        followed by a formatted table of all the ingredients,
        followed by the instructions for the recipe.
        """
        recipe = kwargs.get('recipe')
        if recipe == None:
            recipe = cls.select_recipe()
        print(f'\nRecipe: {recipe.name}')
        print(f'Prep Time: {recipe.prep_time}')
        print(f'Cook Time: {recipe.cook_time}\n')
        print(f'Ingredients:')
        cls.print_ingredients(recipe=recipe)
        print(f'Instructions: {recipe.instructions}\n')

    @classmethod
    def add_recipe(cls):
        """Add new recipe.
        Gives the option to add ingredients.
        Prep time, cook time, and recipe instructions must be
        added from modify recipe menu.
        """
        ingredient_list = []
        name = input('Enter the recipe name: ').strip()

        run = True
        while run:
            if input('Add an ingredient? [y/N]:  ').lower() == 'y':
                ingredient_list.append(cls.set_ingredient_details())
            else:
                run = False

        if input(f'Save {name} recipe? [Y/n]:  ').lower() != 'n':
            Recipe.create(
                name=name, ingredient_list=json.dumps(ingredient_list))

    @classmethod
    def delete_recipe(cls):
        """Delete recipe."""
        recipe = cls.select_recipe()
        if recipe is not None:
            if input(f'Delete {recipe.name}? [y/N]:  ').lower() == 'y':
                recipe.delete_instance()
                print("recipe deleted")

    @staticmethod
    def add_test_recipes():
        Recipe.create(name='garlic bread', ingredient_list=json.dumps(
            test_recipes.garlic_bread_ingredients))
        Recipe.create(name='black bean enchiladas', ingredient_list=json.dumps(
            test_recipes.black_bean_enchiladas_ingredients))

    @classmethod
    def search_recipes(cls):
        """Search recipes by ingredient."""
        cls.view_recipes(input('Search ingredients:  '))
