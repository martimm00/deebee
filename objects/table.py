import os


class Table:
    def __init__(self, name: str, path: os.path) -> None:
        self._name = name if name and path else "test"
        self._path = path if path and name else "test"

    @property
    def name(self) -> str:
        """
        self._name getter.
        """
        return self._name

    @name.setter
    def name(self, new_name: str) -> None:
        """
        self._name setter.
        """
        self._name = new_name

    @property
    def path(self) -> os.path:
        """
        self._path getter.
        """
        return self._path


