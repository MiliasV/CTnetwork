import numpy as np
import scipy
import fiona
import statistics
import math
import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString, shape, mapping, Point, MultiPoint, MultiLineString, Polygon, MultiPolygon
from shapely.ops import cascaded_union, linemerge, nearest_points
from centerline.geometry import Centerline
from statistics import mean


def my_centerlines(row):
    try:
        return Centerline(row.geometry)
    except:
        print('skipping one row because of error making centerline')
        
        
def remove_short_lines(line):
    if line.type == 'MultiLineString':
        passing_lines = []
        for i, linestring in enumerate(line):
            other_lines = MultiLineString([x for j, x in enumerate(line) if j != i])
            p0 = Point(linestring.coords[0])
            p1 = Point(linestring.coords[-1])
            is_deadend = False
            if p0.disjoint(other_lines): is_deadend = True
            if p1.disjoint(other_lines): is_deadend = True
            if not is_deadend or linestring.length > 5:                
                passing_lines.append(linestring)
        return MultiLineString(passing_lines)
    if line.type == 'LineString':
        return line
    
    
def linestring_to_segments(linestring):
    return [LineString([linestring.coords[i], linestring.coords[i+1]]) for i in range(len(linestring.coords) - 1)]


def get_segments(line):
    line_segments = []
    if line.type == 'MultiLineString':        
        for linestring in line.geoms:            
            line_segments.extend(linestring_to_segments(linestring))
    if line.type == 'LineString':        
        line_segments.extend(linestring_to_segments(line))
    return line_segments


def interpolate_by_distance(linestring):
    distance = 1
    all_points = []
    count = round(linestring.length / distance) + 1    
    if count == 1:
        all_points.append(linestring.interpolate(linestring.length / 2))    
    else:
        for i in range(count):
            all_points.append(linestring.interpolate(distance * i))    
    return all_points

def interpolate(line):    
    if line.type == 'MultiLineString':        
        all_points = []        
        for linestring in line:
            all_points.extend(interpolate_by_distance(linestring))        
        return MultiPoint(all_points)            
    if line.type == 'LineString':
        return MultiPoint(interpolate_by_distance(line))
    
    
def polygon_to_multilinestring(polygon):
    return MultiLineString([polygon.exterior] + [line for line in polygon.interiors])
    

def get_avg_distances(row):    
    avg_distances = []    
    sidewalk_lines = polygon_to_multilinestring(row.geometry)    
    for segment in row.segments:        
        points = interpolate(segment)        
        distances = []        
        for point in points:
            p1, p2 = nearest_points(sidewalk_lines, point)
            distances.append(p1.distance(p2))            
        avg_distances.append(sum(distances) / len(distances))        
    return avg_distances


def get_weighted_avg_width(values, weights):
    total = 0
    if len(values):
        for i in range(len(values)):
            total = total + values[i] * weights[i]
        weighted_avg = total / sum(weights)
        return weighted_avg
    else:
        return 0
    
    
def get_polygon_width(gdf):    
    gdf['centerlines'] = gdf.apply(lambda row: my_centerlines(row), axis=1)
    gdf = gdf[gdf['centerlines'].notna()]
    gdf = gdf.set_geometry('centerlines')
    gdf['centerlines'] = gdf['centerlines'].apply(linemerge)
    gdf['centerlines'] = gdf['centerlines'].apply(remove_short_lines)
    gdf['centerlines'] = gdf['centerlines'].apply(lambda row: row.simplify(1, preserve_topology=True))
    gdf['segments'] = gdf['centerlines'].apply(get_segments)
    gdf['avg_distances'] = gdf.apply(lambda row: get_avg_distances(row), axis=1)
    gdf = gdf.set_geometry('geometry')
    
    data = {'avg_width': [], 'min_width': [], 'max_width': [], 'total_seg_length': []}
    for i, row in gdf.iterrows():
        row_lengths = []
        for segment in gpd.GeoSeries(row.segments):
            row_lengths.append(segment.length)
        if row.avg_distances:
            data['avg_width'].append(2 * get_weighted_avg_width(row.avg_distances, row_lengths))
            data['min_width'].append(2 * min(row.avg_distances))
            data['max_width'].append(2 * max(row.avg_distances))
            data['total_seg_length'].append(sum(row_lengths))
        else:
            data['avg_width'].append(0)
            data['min_width'].append(0)
            data['max_width'].append(0)
            data['total_seg_length'].append(0)

    gdf['avg_width'] = data['avg_width']
    gdf['min_width'] = data['min_width']
    gdf['max_width'] = data['max_width']
    gdf['total_seg_length'] = data['total_seg_length']
    
    return gdf