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
        raise NotImplementedError()

    def _setattr(self, key, value):
        raise NotImplementedError()


class DictionaryObject(AttributeObject):
    def __init__(self, initial_items={}):
        super().__init__("_dictionary")
        self._dictionary = dict(initial_items)

    def _getattr(self, item):
        return self._dictionary.get(item)

    def _setattr(self, key, value):
        self._dictionary[key] = value

    def _copy(self):
        return DictionaryObject(self._dictionary)
