from sequias_historicas.ModelManager import ModelManager
from es_geo_locator.geoLocator import GeoLocatorDB 

def main():
    manager = ModelManager.load_yaml_config()
    geo_db = GeoLocatorDB()

    geo_db.download_nuc()
    geo_db.download_geonames()
    geo_db.load_data()

    print("Installation test passed.")

if __name__ == "__main__":
    main()