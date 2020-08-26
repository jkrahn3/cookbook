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

    def __str__(self):
        out = ''
        for key, value in self.menu_dict.items():
            text = value.__doc__ if isinstance(
                value, types.FunctionType) else value
            out += f'\n{key.rjust(3)}) {text}'
        return out
