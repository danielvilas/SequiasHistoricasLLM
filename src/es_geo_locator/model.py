class LookupResult:
    def __init__(self, name: str, data: dict, source: str):
        self.name = name
        self.data = data
        self.source = source

    def to_dict(self):
        return {
            "name": self.name,
            "data": self.data,
            "source": self.source
        }
    
class NameNormalizer:
    def __init__(self):
        pass

    def normalize_name(self, name: str) -> str:
        """
        Normalize the name for consistent lookup.

        Name normalization steps:
         * remove leading/trailing whitespace and converts to lowercase.
         * replace multiple spaces with a single space.
         * replace  accents with their non-accented counterparts.
         * lowercase the name.

        Args:
            name (str): The name to normalize.  
        Returns:
            str: The normalized name.
        """
        name = name.strip().lower()
        name = ' '.join(name.split())

        accents = {'a': ['á', 'à'],
                   'e': ['é', 'è'],
                   'i': ['í', 'ì'],
                   'o': ['ó', 'ò'],
                   'u': ['ú', 'ù', 'ü'],
                   ' ': ['\'', '’', '´', '`','«','»'],
                   }

        for repl, accented_chars in accents.items():
            for accented_char in accented_chars:
                name = name.replace(accented_char, repl)
        
        return name