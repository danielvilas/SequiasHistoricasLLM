"""
Este modulo define las estructuras de datos para la aplicación "sequí­as históricas".
"""

from typing import Optional

class LlmModelConfig:

    @staticmethod
    def from_dict(data: dict) -> 'LlmModelConfig':
        """
        Crea una instancia de LlmModelConfig a partir de un diccionario,
        utilizando valores predeterminados cuando sea necesario.
        """
        name = data.get('name', 'default_model')
        base = data.get('base', 'gpt-3.5-turbo')
        overides = data.get('overrides', {})

        return LlmModelConfig(name, base, overides)
    """
    Configuración para el modelo de lenguaje.
    """
    def __init__(self, name: str, base: str,overides: dict):
        self.name = name
        self.base = base
        self.overides = overides
        self.config:dict = None
    
    def _override_config(self, cfg, overides):

        for key, value in overides.items():
            if isinstance(value, dict):
                if key not in cfg:
                    cfg[key] = value
                else:
                    cfg[key] = self._override_config(cfg[key], value)
            else:
                cfg[key] = value
        return cfg

    def load_config(self, config: dict):
        self.config = config
        if self.overides:
            self.config=self._override_config(self.config, self.overides)

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