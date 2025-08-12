from functools import cache
from geopandas.geodataframe import GeoDataFrame
import pandas as pd
import geopandas as gpd
import pydeck as pdk
import matplotlib.pyplot as plt
import matplotlib.colors
from matplotlib.colors import ListedColormap
import os
import urllib.request
from shapely.geometry import MultiPolygon

DATA_DIR = './data'
FILENAME = 'Parcels.zip'
ZIPPATH = DATA_DIR + '/' + FILENAME
CACHENAME = 'cachedata.geojson'    
CACHEPATH = DATA_DIR + '/' + CACHENAME

def init():
    if not os.path.exists(DATA_DIR):
        print("Creating folder:", DATA_DIR)
        os.makedirs(DATA_DIR)

    parcelsdownload = 'https://dciimages.danecounty.gov/Parcels/Parcels.zip'
    if not os.path.isfile(ZIPPATH):
        print("Downloading from:", parcelsdownload)
        urllib.request.urlretrieve(parcelsdownload, ZIPPATH)

def read_data():
    init()
    data = gpd.read_file(ZIPPATH, use_arrow=True)
    return data

def cache_data(gdf):
    print("Caching Data")
    gdf.to_file(DATA_DIR + "/cachedata.geojson", driver='GeoJSON');

def get_data():

    if os.path.isfile(CACHEPATH):
        print("Reading Cached Data...")
        return gpd.read_file(CACHEPATH, use_arrow=True)

    gdf = read_data()

    gdf = filter_data(gdf)

    cache_data(gdf)

    return gdf

def filter_data(gdf):
    gdf = gdf.filter(['Sum_LandVa', 'Sum_Improv','PrimaryAdd', 'PropertyAd', 'Shape_STAr', 'Municipali','geometry'])
    gdf = gdf[gdf['Municipali'] == 'City of Madison']
    gdf = gdf.to_crs('4326')
    gdf['VAL_PER_AREA'] = gdf.apply(lambda row: get_total_val(row), axis=1)
    gdf = gdf[gdf['PrimaryAdd'] == 'Yes']

    return gdf


def points_from_polygons(polygons):
    points = []
    for mpoly in polygons:
        # if isinstance(mpoly, MultiPolygon):
        #     polys = list(mpoly)
        # else:
        polys = [mpoly]
        for polygon in polys:
            for point in polygon.exterior.coords:
                points.append(point)
            for interior in polygon.interiors:
                for point in interior.coords:
                    points.append(point)
    return points

def get_total_val(row):
    landval = row['Sum_LandVa']
    improv = row['Sum_Improv']
    area = row['Shape_STAr']
    
    totalval = landval + improv

    valperarea = totalval / area

    # if valperarea < 0.0001:
    #     valperarea = 0.0001

    return valperarea

def doplot(gdf):
    print("plotting now")
    plot3d(gdf)
    

def plot3d(gdf):
    scaleCol = "VAL_PER_AREA"

    min_count = gdf[scaleCol].min()
    max_count = gdf[scaleCol].max()
    diff = max_count - min_count
    
    color_scheme = f"""[
        50 + 130 * ({scaleCol} - {min_count})/{diff}, 
        150 - 150 * ({scaleCol} - {min_count})/{diff}, 
        50 + 130 * ({scaleCol} - {min_count})/{diff}
        ]"""

    tracts = pdk.Layer(
        "GeoJsonLayer",
        gdf,
        opacity=1,
        stroked=True,
        filled=True,
        extruded=True,
        wireframe=True,
        pickable=True,
        get_elevation=f"{scaleCol}", # Converting to population density per sq m to per sq mile
        get_fill_color=color_scheme,
        # get_fill_color=f"{scaleCol}==0?[0,0,0,0]:[{scaleCol}+95, {scaleCol}, {scaleCol}]"

        get_line_color=color_scheme,
    )
    
    # All together
    # You can customize by adding more layers if you wish
    r = pdk.Deck(layers=[tracts],)
    
    # Exporting as an html file
    r.to_html("./3dmap.html")

def printdata(gdf):
    # gdf = gdf[gdf['Municipali'] == 'City of Madison']
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    # print(gdf['PropertyAd'])
    # gdf = gdf[type(gdf['PropertySt']) is str]
    gdf = gdf[gdf['PropertyAd'].notna()]
    gdf = gdf[gdf['PropertyAd'].str.contains("4817 SHEBOYGAN AVE")]
    # gdf = gdf.sort_values(by=['VAL_PER_AREA'])
    print(gdf.columns)

def domain():
    doplot(gdf)

if __name__ == '__main__':
    gdf = get_data()
    doplot(gdf)




