class VariableNamesManager:

    def __init__(self, *, varnames_pool=None, next_unused_id=None):
        if varnames_pool is None:
            varnames_pool = set()
        self._varnames_pool = varnames_pool

        if next_unused_id is None:
            next_unused_id = 0
        self._next_unused_id = next_unused_id

    def identifier_by_name(self, name):
        self._varnames_pool.add(name)
        return name

    def name_by_identifier(self, identifier):
        return identifier

    def create_new_identifier(self, *, old_identifier=None):
        while str(self._next_unused_id) in self._varnames_pool:
            self._next_unused_id += 1
        result = str(self._next_unused_id)
        self._varnames_pool.add(result)
        return result
