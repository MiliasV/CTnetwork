import osmnx as ox
import pandas as pd
import geopandas as gpd
import requests
import os
import osm2geojson
import time


def get_osm_data(tag_query, extent, area_type):

    osm_crs = 'EPSG:4326'
    url = "http://overpass-api.de/api/interpreter"

    my_crs = extent.crs
    if extent.crs != osm_crs:
        extent = extent.to_crs(osm_crs)

    if area_type == 'bbox':
        bbox = extent.total_bounds
        area = '{1},{0},{3},{2}'.format(bbox[0], bbox[1], bbox[2], bbox[3])
    elif area_type == 'convexhull':
        xy = extent.convex_hull.geometry[0].exterior.coords.xy
        osm_poly = 'poly:"'
        for i, (lat, lon) in enumerate(zip(xy[1], xy[0])):
            osm_poly = osm_poly + '{} {} '.format(lat, lon)
        area = osm_poly[:-1] + '"'
    else:
        raise ValueError('Unknown type {}: please use [bbox] or [convexhull]'.format(area_type))
        return None

    data_request = """
        [out:json];
        (
            node{0}({1});
            way{0}({1});
            relation{0}({1});
        );
        out geom;
        >;
        out skel qt;
    """.format(tag_query, area)

    n=5
    for i in range(n):
        response = requests.get(url, params={'data': data_request})

        if response.ok:

            geojson = osm2geojson.json2geojson(response.json())

            if geojson['features']:
                gdf = gpd.GeoDataFrame.from_features(geojson)
                gdf = gdf[gdf['tags'].notna()]      # to avoid including both ways and their waypoints
                gdf.crs = osm_crs
                return gdf.to_crs(my_crs)            # CRS of our input dataset
            else:
                return gpd.GeoDataFrame()            # empty dataframe

        elif response.status_code == 429 or response.status_code == 504:
            if i < n-1:
                print('Response {}\nWaiting {}sec, and trying again max {} more times'.format(response, (i+1)*30, n-i-1))
                time.sleep((i+1)*30)
            else:
                raise ValueError('No valid response to OSM query after trying {} times'.format(n))
                return None

        else:
            raise ValueError('Response {}\nAborting'.format(response))
            return None


def get_osm_places_per_city(city=None, output_folder='.', epsg=28992, buffer_m=0, query=''):
    output_folder = output_folder + '/' + city
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    area_type = 'convexhull'
    extent = ox.geocode_to_gdf(city)
    extent = ox.geocode_to_gdf(city).to_crs('epsg:'+ str(epsg))
    extent = extent.buffer(buffer_m, join_style=2)
    gdf_res = get_osm_data(tag_query=query, extent=extent, area_type=area_type)
    output_file = os.path.join(output_folder, '{}_osm_places.csv'.format(city.lower()))
    gdf_res.to_csv(output_file)
    return

def get_osm_places_within_buffer(tags, geocoordinates, radius):   
    url = "http://overpass-api.de/api/interpreter"
    query = """ 
    [out:json];
    (
        node[{tag}](around:{rad}, {geo});
        way[{tag}](around:{rad}, {geo});
        relation[{tag}](around:{rad}, {geo});
    );
    out geom;
    >;
    out skel qt;
    """.format(tag = tags, rad=radius, geo = geocoordinates)
    response =  requests.get(url, params={'data': query})
    if response.ok:
        geojson = osm2geojson.json2geojson(response.json())
        if geojson['features']:
            gdf = gpd.GeoDataFrame.from_features(geojson)
            return gdf           # CRS of our input dataset
        else:
            return gpd.GeoDataFrame()            # empty dataframe

    elif response.status_code == 429 or response.status_code == 504:
        if i < n-1:
            print('Response {}\nWaiting {}sec, and trying again max {} more times'.format(response, (i+1)*30, n-i-1))
            time.sleep((i+1)*30)
        else:
            raise ValueError('No valid response to OSM query after trying {} times'.format(n))
            return None

    else:
        raise ValueError('Response {}\nAborting'.format(response))
        return None