"""
Este modulo define las estructuras de datos para la aplicación "sequí­as históricas".
"""

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
