
import requests

import logging

LOG = logging.getLogger(__name__)

base_url_ign = "https://api-features.ign.es/collections/"


class Ign_OgcClient:
    """Base client for interacting with IGN OGC API."""

    def __init__(self, collection: str, base_url: str = base_url_ign):
        """Initialize the client with the specified collection and base URL.
        Args:
            collection (str): The collection to interact with.
            base_url (str): The base URL of the OGC API.
        """
        self.collection = collection
        self.base_url = base_url
        if self.base_url[-1] != '/':
            self.base_url += '/'
        self.session: requests.Session = requests.Session()
        self.session.headers.update(self.build_headers())


    def _get_items(self, limit: int = 100, offset: int = 0, params: dict = None) -> dict:
        """
            Retrieve items from the specified collection with pagination.
            Args:
                limit (int): The maximum number of items to retrieve.
                offset (int): The starting point for retrieval.
                params (dict): Additional query parameters.
            Returns:
                dict: The JSON response from the API.
        """
        if params is None:
            params = {}

        params.update({
            "limit": limit,
            "offset": offset
        })

        url = f"{self.base_url}{self.collection}/items"
        LOG.debug(f"Requesting items from {url} with params: {params}")

        response = self.session.get(url, params=params, headers=self.build_headers())
        LOG.debug(f"Response status code: {response.status_code}")
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Failed to retrieve items"}

    def build_headers(self) -> dict:
        """
        Build headers for the API requests.
        Should be re-implemented in subclasses if needed.
        Returns:
            dict: A dictionary of headers.
        """
        return {"Accept": "application/json"}

    def build_params_search_all_items(self) -> dict:
        """
        Build parameters for searching all items.
        Should be re-implemented in subclasses.
        Returns:

        dict: A dictionary of parameters for the search.
        """
        return {}

    def build_params_search_by_name(self, name: str) -> dict:
        """
        Build parameters for searching items by name.
        Should be re-implemented in subclasses.
        Args:
            name (str): The name to search for.
        Returns:
            dict: A dictionary of parameters for the search.
        """
        raise NotImplementedError(
            "This method should be implemented in a subclass")

    def extract_item_info(self, item: dict) -> list:
        """
        Extract relevant information from an item.
        Should be re-implemented in subclasses.
        Args:
            item (dict): The item from which to extract information.

        Returns:
            list: A list of extracted information.
        """
        raise NotImplementedError(
            "This method should be implemented in a subclass")

    def search_item(self, name: str) -> list:
        """
        Search for items by name.
        Args:
            name (str): The name to search for.
        Returns:
            list: A list of items matching the search criteria.
        """
        params = self.build_params_search_by_name(name)
        results = self._get_items(params=params)

        if "features" in results:
            return [self.extract_item_info(item,skip_geometry=False) for item in results["features"]]
        else:
            return []

    def get_all_items(self) -> list:
        """
        Retrieve all items from the collection.
        Returns:
            list: A list of all items in the collection.
        """
        offset = 0
        limit = 1000
        all_items = []
        while True:
            params = self.build_params_search_all_items()
            results = self._get_items(limit=limit, offset=offset, params=params)
            if "features" in results:
                all_items.extend([self.extract_item_info(item)
                                 for item in results["features"]])
                if len(results["features"]) < limit:
                    break
                offset += limit
            else:
                break
            #if offset > limit: return all_items
        return all_items


class Ign_Nucleos_Poblacion_Client(Ign_OgcClient):
    """Client for interacting with IGN Nucleos de Poblacion collection."""

    def __init__(self, base_url: str = base_url_ign):
        """
        Initialize the client for the IGN Nucleos de Poblacion collection.
        """
        super().__init__(collection="nuc", base_url=base_url)

    def build_params_search_by_name(self, name: str) -> dict:
        """
        Build parameters for searching Nucleos de Poblacion by name.
        Args:
            name (str): The name to search for.
        Returns:
            dict: A dictionary of parameters for the search.
        """
        return {
            "nombre": name
        }
    
    def build_params_search_all_items(self) -> dict:
        """
        Build parameters for searching all Nucleos de Poblacion items.
        This implementation skips geometry to reduce data size.
        Returns:
            dict: A dictionary of parameters for the search.
        """
        return {"skipGeometry": "true"}

    def extract_item_info(self, item: dict, skip_geometry=True) -> dict:
        """
        Extract relevant information from a Nucleos de Poblacion item.
        Args:
            item (dict): The item from which to extract information.
        Returns:
            list: A list of extracted information.
        """
        if skip_geometry and "geometry" in item:
            item.pop("geometry")
        LOG.debug(f"Extracting information from item: {item}")
        
        properties = item.get("properties", {})
        # nombre = properties.get("nombre", "")
        # provincia = properties.get("provincia", "")
        # comunidad = properties.get("comunidad", "")
        # lat = properties.get("latitud", "")
        # lon = properties.get("longitud", "")

        ret = {
            "id": item.get("id", ""),
            "nombre": properties.get("nombre", ""),
            "capital": properties.get("capital", ""),
            "provincia": properties.get("cpro", ""),
            "comunidad": properties.get("comunidad", ""),
            "latitud": properties.get("latitud", ""),
            "longitud": properties.get("longitud", ""),
            "tipo": properties.get("tipo", ""),
            "codine": properties.get("codine", "")
        }
        if "geometry" in item:
            ret["geometry"] = item["geometry"]    
        return ret
