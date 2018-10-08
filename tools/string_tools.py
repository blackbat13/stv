class StringTools:
    @staticmethod
    def to_first_word(word: str) -> str:
        """Uppercase first letter of the given word"""
        return word.replace(word[0], word[0].upper(), 1)
