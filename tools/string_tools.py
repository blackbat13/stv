class StringTools:
    @staticmethod
    def capitalize_first_letter(word: str) -> str:
        """Capitalize first letter of the given word"""
        return word.replace(word[0], word[0].upper(), 1)

    @staticmethod
    def lowercase_first_letter(word: str) -> str:
        """Lowercase first letter of the given word"""
        return word.replace(word[0], word[0].lower(), 1)

    @staticmethod
    def is_blank_line(line: str):
        return len(line.strip()) == 0