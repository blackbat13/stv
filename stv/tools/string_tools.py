"""Module for string tools."""


class StringTools:
    """
    Collection of methods to simplify working with strings.
    """

    @staticmethod
    def capitalize_first_letter(word: str) -> str:
        """
        Capitalize first letter of the given word
        :param word:
        :return:
        """
        return word.replace(word[0], word[0].upper(), 1)

    @staticmethod
    def lowercase_first_letter(word: str) -> str:
        """
        Lowercase first letter of the given word
        :param word:
        :return:
        """
        return word.replace(word[0], word[0].lower(), 1)

    @staticmethod
    def is_blank_line(line: str):
        """
        Checks if line consists only of white characters or no characters.
        :param line: line to check
        :return: True if line is blank, False otherwise.

        Example:
        >>> StringTools.is_blank_line("   ")
        True

        >>> StringTools.is_blank_line("  a  ")
        False
        """
        return len(line.strip()) == 0
