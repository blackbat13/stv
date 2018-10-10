class StringTools:
    @staticmethod
    def capitalize_first_letter(word: str) -> str:
        """Capitalize first letter of the given word"""
        return word.replace(word[0], word[0].upper(), 1)
