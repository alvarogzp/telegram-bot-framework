class DictionaryObject:
    def __init__(self):
        self._dictionary = {}

    def __getattr__(self, item):
        return self._dictionary.get(item)

    def __setattr__(self, key, value):
        if key == "_dictionary":
            super().__setattr__(key, value)
        else:
            self._dictionary[key] = value

    def _copy(self):
        new = self.__class__.__new__(self.__class__)
        new._dictionary = self._dictionary.copy()
        return new
