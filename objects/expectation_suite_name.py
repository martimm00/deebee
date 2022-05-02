from constants.path_constants import EXPECTATION_SUITES_PATH


class ExpectationSuiteName:
    def __init__(self, name: str) -> None:
        """
        Initializes ExpectationSuiteName object.
        :param name: String with name set by the
        user.
        """
        self._directory = EXPECTATION_SUITES_PATH
        self._name = name
        self._ge_name = self._build_ge_name()

    @property
    def name(self) -> str:
        """
        self._name getter.
        :return: String with interface name.
        """
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        """
        self._name setter.
        :param name: String with new name set by the user.
        """
        self._name = name
        self._ge_name = self._build_ge_name()

    @property
    def directory(self) -> str:
        """
        self._directory getter.
        :return: String with directory name.
        """
        return self._directory

    @property
    def ge_name(self) -> str:
        """
        self._ge_name getter.
        :return: String with Expectation Suite name for
        great_expectations.
        """
        return self._ge_name

    def _build_ge_name(self) -> str:
        """
        Builds great_expectations Expectation Suite name from the
        directory and the name set by the user.
        :return: String with great_expectations Expectation
        Suite name.
        """
        return self.directory + "." + self.name

    def __contains__(self, string: str) -> bool:
        """
        Returns if Expectation Suite name contains the given string.
        :return: Bool that tells if the given string is contained by
        the name.
        """
        return string in self.name

    def __eq__(self, other_name: str) -> bool:
        """
        Returns if the given name is equal to this one.
        :param other_name: String with another name.
        :return: Bool that tells if the given name is equal to the
        existing one.
        """
        return self.name == other_name

    def __len__(self) -> int:
        """
        Returns Expectation Suite name length.
        :return: Int with its length.
        """
        return len(self.name)

    def __repr__(self) -> str:
        """
        Representation method.
        """
        return self.name

    def __str__(self) -> str:
        """
        String method.
        """
        return self.name
