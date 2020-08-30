import types


class DocStringMenu():
    def __init__(self, options: tuple, *args, **kwargs):
        self.options = options
        self.menu_dict = {}

        for idx, option in enumerate(self.options, start=1):
            self.menu_dict[str(idx)] = option

    def show(self, *args, **kwargs):
        print(self)
        print('  q) Quit this menu')
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

    def __str__(self):
        out = ''
        for key, value in self.menu_dict.items():
            if isinstance(value, types.FunctionType) or isinstance(value, types.MethodType):
                text = value.__doc__
            else:
                text = value
            out += f'\n{key.rjust(3)}) {text}'
        return out


class RecipeMenu(DocStringMenu):
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
