"""
Este modulo define las estructuras de datos para la aplicación "sequí­as históricas".
"""

from typing import Optional

class LlmModelConfig:

    @staticmethod
    def from_dict(data: dict, default: dict={}) -> 'LlmModelConfig':
        """
        Crea una instancia de LlmModelConfig a partir de un diccionario,
        utilizando valores predeterminados cuando sea necesario.
        """
        name = data.get('name', default.get('name', 'default_model'))
        model_name = data.get('model', default.get('model', 'gpt-3.5-turbo'))
        temperature = data.get('temperature', default.get('temperature', 0.7))
        max_tokens = data.get('max_new_tokens', default.get('max_new_tokens', 150))

        return LlmModelConfig(name, model_name, temperature, max_tokens)
    """
    Configuración para el modelo de lenguaje.
    """
    def __init__(self, name: str, model_name: str, temperature: float, max_tokens: int):
        self.name = name
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

class PdfFileInfo:
    def __init__(self, path:str, year:int, 
                month:Optional[int]=None, 
                day:Optional[int]=None, 
                page:Optional[int]=None,
                coherent_path:Optional[bool]=None,
                periodico:Optional[str]=None,
                num_pages:Optional[int]=None,
                is_clean:bool=False,
                is_one_page:bool=False):
        self.path = path
        self.year = year
        self.month = month
        self.day = day
        self.page = page
        self.coherent_path = coherent_path
        self.periodico = periodico
        self.num_pages = num_pages
        self.is_clean = is_clean
        self.is_one_page = is_one_page
    pass

    def clean_path(self) -> str:
        if self.periodico and self.year and self.month and self.day and self.is_one_page and self.page:
            return f"{self.periodico}/{self.year}/{self.month:02d}/{self.day:02d}/{self.year:04d}{self.month:02d}{self.day:02d}_{self.page:04d}.pdf"
        return None
        #return self.path