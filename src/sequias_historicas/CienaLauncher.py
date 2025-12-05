from ciena_llm import ClimateImpactExtractor
from .ModelManager import ModelManager
import time
import yaml
import os

class CienaLauncher:
    def __init__(self, modelManager=None):
        if modelManager is None:
            modelManager = ModelManager.load_yaml_config()
        self.modelManager = modelManager
    
    def _build_config(self,model):
        model = self.modelManager.get_model_config(model)
        return model.config

    def build_config_file(self, model:str, output_folder:str):
        os.makedirs(output_folder, exist_ok=True)
        config_path = os.path.join(output_folder, "ciena_config.yaml")
        with open(config_path, "wb") as f:
            cfg = self._build_config(model)
            yaml_str = yaml.dump(
                    cfg, default_flow_style=False, allow_unicode=True
            )
            f.write(yaml_str.encode("utf-8"))
        return config_path

    def _save_config(self, input_folder:str, output_folder:str, extractor:ClimateImpactExtractor):
         pass
    
    def _save_results(self, output_folder:str, extractor:ClimateImpactExtractor, articles):
        # Save results:
        # - Summary of the results
        extractor.output_manager.write_summary_to_csv(
            articles, os.path.join(output_folder, "summary.csv")
        )
        # - Excluded problematic articles
        extractor.output_manager.write_excluded_problematic_articles_to_csv(
            os.path.join(output_folder, "excluded_problematic_articles.csv")
        )
        # - Parsing errors
        parsing_errors = extractor.output_manager.write_parsing_errors_to_json(
            os.path.join(output_folder, "parsing_errors.json")
        )
        total_parsing_errors = parsing_errors["total"]
        # - Execution times
        execution_times = extractor.output_manager.write_execution_times_to_json(
            os.path.join(output_folder, "execution_times.json")
        )


        pass

    def launch(self, model:str, input_folder:str,output_folder:str):
        print("Launching Ciena process...")
        config_path = self.build_config_file(model, output_folder)
        start_time = time.time()
        extractor = ClimateImpactExtractor(config_path)
        self._save_config(input_folder, output_folder, extractor)
        articles = extractor(dataset_path=input_folder)
        self._save_results(output_folder, extractor, articles)

        test_execution_time = time.time() - start_time
        print(f"Ciena process finished in {test_execution_time} seconds.")
