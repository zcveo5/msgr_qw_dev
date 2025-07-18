class ModWin(Win):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__super__ = super()

Win = ModWin