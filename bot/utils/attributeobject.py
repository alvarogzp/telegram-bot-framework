class AttributeObject:
    def __init__(self, *excluded_keys):
        self._excluded_keys = excluded_keys

    def __getattr__(self, item):
        return self._getattr(item)

    def __setattr__(self, key, value):
        if key == "_excluded_keys" or key in self._excluded_keys:
            super().__setattr__(key, value)
        else:
            self._setattr(key, value)

    def _getattr(self, item):
        pass

    def _setattr(self, key, value):
        pass


class DictionaryObject(AttributeObject):
    def __init__(self):
        super().__init__("_dictionary")
        self._dictionary = {}

    def _getattr(self, item):
        return self._dictionary.get(item)

    def _setattr(self, key, value):
        self._dictionary[key] = value

    def _copy(self):
        new = DictionaryObject()
        new._dictionary = self._dictionary.copy()
        return new
