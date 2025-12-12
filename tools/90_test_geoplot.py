from es_geo_locator.geoLocator import GeoLocatorDB

import geopandas as gpd
import pandas as pd
import geoplot as gplt
import shapely
import json 

import matplotlib.pyplot as plt
import geoplot.crs as gcrs

geolocator = GeoLocatorDB()
geolocator.load_data()


def main():
    res =   geolocator.search_unidad_adm("Extremadura")
    for item in res.data:
        item['geometry'] = shapely.from_geojson(json.dumps(item['geometry']))
    

    df = pd.DataFrame(res.data)
    gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")

    pdf = [{"geometry": shapely.Point(item['longitud'], item['latitud']),"radius": item["radius"]} for item in res.data]
    gdf_p = gpd.GeoDataFrame(pdf, geometry="geometry", crs="EPSG:4326")    
    cdf = [{"geometry": item['geometry'].buffer(item["radius"])} for item in pdf]  
    gdf_c = gpd.GeoDataFrame(cdf, geometry="geometry", crs="EPSG:4326")

    prj = gcrs.AlbersEqualArea()
    #prj = gcrs.Mercator()

    ax = gplt.polyplot(gdf, projection=prj,
        edgecolor='white', facecolor='lightgray',
        figsize=(12, 8))

    limits = ax.get_xlim()+ax.get_ylim()
    print ("LIMITS")
    print (limits)
    print("GDF1")
    print(gdf.head())
    print("GDF2")
    print(gdf_p.head())
    gplt.pointplot(gdf_p, ax=ax, projection=prj,
        color='red', alpha=0.3,)
    gplt.polyplot(gdf_c, ax=ax, projection=prj,
        color='blue', alpha=0.1, edgecolor='darkred')
    plt.savefig("map.png")
    pass

if __name__ == "__main__":
    main()