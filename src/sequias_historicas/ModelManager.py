from .models import LlmModelConfig

from typing import Dict, List
import yaml

class ModelManager:
    
    @staticmethod
    def load_yaml_config(yaml_file: str = "models.yaml", data_path: str = "data/") -> 'ModelManager':
        """
        Carga la configuración del modelo desde un archivo YAML.
        """
        with open(data_path + yaml_file, 'r') as file:
            config_data = yaml.safe_load(file)
        
        manager = ModelManager(config_data.get('default', None))
        manager.load_config(config_data.get('models', []))
        return manager
    
    """
    Clase para gestionar la configuración del modelo de lenguaje.
    """
    def __init__(self, default_config: dict = {}):
        self.default_config = default_config
        self.model_config:dict = {}

    def load_config(self, config_data: List[Dict ]):
        """
        Carga la configuración del modelo desde un diccionario.
        """
        for model_cfg in config_data:
            model = LlmModelConfig.from_dict(model_cfg, self.default_config)
            self.model_config[model.name] = model
            
    def get_model_config(self, name: str) -> LlmModelConfig:
        """
        Devuelve la configuración actual del modelo.
        """
        if name not in self.model_config:
            raise ValueError(f"La configuración del modelo '{name}' no ha sido cargada.")
        return self.model_config[name]
