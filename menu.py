import types


class DocStringMenu():
    """Class for looping text-based menu with functions as available options.
    Takes user input to decide what action to take next.
    Input q to exit menu.

    Should be instantiated with a tuple or list of functions to be displayed as options.

    Function definitions for menu options should have a docstring where the first
    line is what will be displayed in the menu. For example:

    def example():
        '''Example option.
        This is just an example function
        '''
        pass

    def example2():
        '''Example option 2.
        This is another example function.
        '''

    menu = DocStringMenu((example, example2))
    menu.loop_menu():

        Displays menu like:

        1) Example option.
        2) Example option 2.
    """

    def __init__(self, options: tuple, *args, **kwargs):
        self.options = options
        self.menu_dict = {}

        for idx, option in enumerate(self.options, start=1):
            self.menu_dict[str(idx)] = option

    def show(self, *args, **kwargs):
        self.print_menu()
        print('  q) Quit this menu.')
        choice = input('\nAction: ').lower().strip()
        if choice == 'q':
            return False
        elif choice in self.menu_dict.keys():
            self.menu_dict[choice](*args, **kwargs)
        return True

    def loop_menu(self, *args, **kwargs):
        loop_menu = True
        while loop_menu:
            loop_menu = self.show(*args, **kwargs)

    def print_menu(self):
        out = ''
        for key, value in self.menu_dict.items():
            if isinstance(value, types.FunctionType) or isinstance(value, types.MethodType):
                text = value.__doc__.split('\n', 1)[0]
            else:
                text = value
            out += f'\n{key.rjust(3)}) {text}'
        print(out)


class RecipeMenu(DocStringMenu):
    """Subclass of DocStringMenu.

    Allows for running methods before and after each menu iteration.
    This is intended so that, if using the menu to update a database
    and printing out information from the database on each loop,
    the information printed can reflect the updates.

    An example use would be, if updating some component of a recipe,
    this would print the recipe, then take user input to update the
    recipe, then refresh the recipe, then display the updated recipe.

        loop_dict = {
                'kwargs_to_refresh': {'recipe': recipe},
                'run_before': print_recipe,
                'run_after': refresh_recipe,
            }

            recipe_menu = RecipeMenu(options)
            recipe_menu.loop_menu(**loop_dict)
    """

    def __init__(self, options: tuple, *args, **kwargs):
        super().__init__(options, *args, **kwargs)

    def loop_menu(self, *args, **kwargs):
        kwargs_to_refresh = kwargs.get('kwargs_to_refresh')
        run_before = kwargs.get('run_before')
        run_after = kwargs.get('run_after')
        loop_menu = True

        while loop_menu:
            run_before(**kwargs_to_refresh) if run_before else None
            loop_menu = self.show(*args, **kwargs_to_refresh)
            kwargs_to_refresh = run_after(
                **kwargs_to_refresh) if run_after else kwargs_to_refresh
