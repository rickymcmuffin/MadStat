from geopandas import GeoDataFrame
import main
from importlib import reload


def init():
    reload(main)
    return main.get_data()

def do_test(gdf):
    reload(main)
    main.doplot(gdf)

def do_print(gdf):
    reload(main)
    main.printdata(gdf)


if __name__ == '__main__':
    gdf = init()
    do_print(gdf)


