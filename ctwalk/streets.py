import networkx as nx
import osmnx as ox
import pandas as pd
import geopandas as gpd
import igraph as ig
import numpy as np
import os
from shapely.geometry import Point, LineString
# import statistics
# import math

#####
#AREA STATS FUNCTIONS
##############
def weighted_average(group, value_col, weight_col):
    
    values = pd.to_numeric(group[value_col])
    weights = pd.to_numeric(group[weight_col])
    
    if len(values) and len(weights) and weights.sum() > 0:
        return (values * weights).sum() / weights.sum()
    elif len(values):
        return values.mean()
    else:
        return None
    

def weighted_sum(group, value_col, weight_col):
    
    values = pd.to_numeric(group[value_col])
    weights = pd.to_numeric(group[weight_col])
    
    if len(values) and len(weights) and weights.sum() > 0:
        return (values * weights).sum()
    elif len(values):
        return values.mean()
    else:
        return None
    
    
def val_per_area(areas, area_id, to_aggr, modes, value_col=None, weight_col=None):
    
    cols = list(areas.columns)
    result = areas.copy()
    
    joined = gpd.sjoin(result, to_aggr, how='left', op='intersects')
    
    for mode in modes:

        if mode == 'wavg':      
            result_col = value_col + '_' + mode
            aggr = joined[[area_id, value_col, weight_col]].groupby(area_id).apply(lambda group:weighted_average(group, value_col, weight_col))
            df_aggr = aggr.to_frame(name=result_col)
            
        elif mode == 'wsum':
            result_col = value_col + '_' + mode
            aggr = joined[[area_id, value_col, weight_col]].groupby(area_id).apply(lambda group:weighted_sum(group, value_col, weight_col))
            df_aggr = aggr.to_frame(name=result_col)

        elif mode == 'mean':  
            result_col = value_col + '_' + mode
            df_aggr = joined[[area_id, value_col]].groupby(area_id).mean(value_col)
            df_aggr = df_aggr.rename(columns={value_col: result_col})

        elif mode == 'median':
            result_col = value_col + '_' + mode
            df_aggr = joined[[area_id, value_col]].groupby(area_id).median(value_col)
            df_aggr = df_aggr.rename(columns={value_col: result_col})

        elif mode == 'min':
            result_col = value_col + '_' + mode
            df_aggr = joined[[area_id, value_col]].groupby(area_id).min(value_col)
            df_aggr = df_aggr.rename(columns={value_col: result_col})

        elif mode == 'max':
            result_col = value_col + '_' + mode
            df_aggr = joined[[area_id, value_col]].groupby(area_id).max(value_col)
            df_aggr = df_aggr.rename(columns={value_col: result_col})

        elif mode == 'sum':
            result_col = value_col + '_' + mode
            df_aggr = joined[[area_id, value_col]].groupby(area_id).sum(value_col)
            df_aggr = df_aggr.rename(columns={value_col: result_col})
            
        elif mode == 'count':          
            result_col = '_' + mode
            df_aggr = pd.DataFrame(joined.groupby(area_id).agg(['count'])['index_right']['count'])
            df_aggr = df_aggr.rename(columns={'count': result_col})
            
        elif mode == 'bool':
            result_col = '_' + mode
            df_aggr = pd.DataFrame(joined.groupby(area_id).agg(['count'])['index_right']['count'])
            df_aggr = df_aggr.astype('bool')
            df_aggr = df_aggr.rename(columns={'count': result_col})
            
        if not result_col in cols:
            cols.append(result_col)
            
        if result_col in result.columns:
            result = result.drop(columns=[result_col])
        
        result = result.merge(df_aggr[result_col], how='left', on=area_id).drop_duplicates(subset=[area_id])
    
    result = result[cols].copy()

    return result  



#####################################################################################
# METRICS #####################################################################################
#####################################################################################
def compute_node_closeness(G_nx, weight='length'):
    # create networkx graph
    osmids = list(G_nx.nodes)
    G_nx = nx.relabel.convert_node_labels_to_integers(G_nx)

    # give each node its original osmid as attribute since we relabeled them
    osmid_values = {k:v for k, v in zip(G_nx.nodes, osmids)}
    nx.set_node_attributes(G_nx, osmid_values, 'osmid')

    print("Convert to igraph ...")
    # convert networkx graph to igraph
    G_ig = ig.Graph(directed=True)
    G_ig.add_vertices(G_nx.nodes)
    G_ig.add_edges(G_nx.edges())
    G_ig.vs['osmid'] = osmids
    G_ig.es[weight] = list(nx.get_edge_attributes(G_nx, weight).values())
    assert len(G_nx.nodes()) == G_ig.vcount()
    assert len(G_nx.edges()) == G_ig.ecount()
    
    print("Calculating closeness ...")
    closeness1 = G_ig.closeness(vertices=None, mode='ALL', cutoff=None, weights=weight, normalized=True)
    
    print("Convert to dataframe closeness ...")
    gdf_nodes = ox.utils_graph.graph_to_gdfs(G_nx, nodes=True, edges=False, node_geometry=True, fill_edge_geometry=False)
    df_nodes = pd.DataFrame({'osmid': G_ig.vs["osmid"], 'node_closeness':closeness1})
    gdf_nodes = gdf_nodes.reset_index(drop=True)
    gdf_res = pd.merge(gdf_nodes, df_nodes, left_on='osmid', right_on='osmid', how='left')

    return gdf_res
    
    
def compute_edge_betweenness(G_nx, weight='length'):
    # create networkx graph
    osmids = list(G_nx.edges)
    G_nx = nx.relabel.convert_node_labels_to_integers(G_nx)
    osmid_values = {k:v for k, v in zip(G_nx.edges, osmids)}

    # # give each node its original osmid as attribute since we relabeled them
    nx.set_edge_attributes(G_nx, osmid_values, 'osmid')
    print("Convert to igraph ...")
    # convert networkx graph to igraph
    G_ig = ig.Graph(directed=True)
    G_ig.add_vertices(G_nx.nodes)
    G_ig.add_edges(G_nx.edges())
    G_ig.es['osmid'] = osmids
    G_ig.es[weight] = list(nx.get_edge_attributes(G_nx, weight).values())
    assert len(G_nx.nodes()) == G_ig.vcount()
    assert len(G_nx.edges()) == G_ig.ecount()
    ###############################################
    # Calculating betweenness ###############################################
    ###############################################
    print("Calculating betweenness ...")
    betweenness = G_ig.edge_betweenness(directed=True, cutoff=None, weights=weight)
    print("Convert to dataframe betweenness ...")
    gdf_edges = ox.utils_graph.graph_to_gdfs(G_nx, nodes=False, edges=True, node_geometry=False, fill_edge_geometry=True)
    df_edges = pd.DataFrame({'osmid': G_ig.es["osmid"], 'edge_betweenness':betweenness})
    gdf_edges = gdf_edges.reset_index(drop=True)
    gdf_res = pd.merge(gdf_edges, df_edges, left_on='osmid', right_on='osmid', how='left')
    return gdf_res


def compute_edge_sinuosity_per_row(row):
    x, y = row.geometry.coords.xy
    start_pt = Point(x[0], y[0])
    end_pt = Point(x[-1], y[-1])
    straight_line = LineString((start_pt, end_pt))
    if straight_line.length:
        return row.geometry.length / straight_line.length
    else:
        return None

    
def compute_edge_sinuosity(edges):
    edges['edge_sinuosity'] = edges.apply(lambda row: compute_edge_sinuosity_per_row(row), axis=1)
    return edges
    
    
def compute_edge_average_polygon_width(
        edges, polygons_with_widths, output_col,
        width_col='avg_width', length_col='total_seg_length', radius=10):
    # take file with polygons of interest (e.g., sidewalks, bike paths) as input
    # aggregate widths into an average per street segment (weighted by segment length)
    
    if output_col in edges.columns:
        edges.drop(columns=[output_col], inplace=True)

    edges['original_geometry'] = edges.geometry
    edges['geometry'] = edges.buffer(radius)

    edges['index'] = edges.index
    mode = ['wavg']
    edges_enriched = area_stats.val_per_area(
        edges, 'index', polygons_with_widths, modes=mode, 
        value_col=width_col, weight_col=length_col)
    
    edges_enriched['geometry'] = edges_enriched['original_geometry']
    
    edges_enriched.rename(columns={'avg_width_wavg' : output_col}, inplace=True)    
    edges_enriched.drop(columns=['original_geometry', 'index'], inplace=True)
    
    return edges_enriched
    


###################################### 
# collect and store streets per city #
######################################
def get_streets_per_cities(cities, buffer_dist=0, network_type='drive', output_folder='.', 
                          intersection_clos=False, street_betw=False, street_sin=False, retain_all=True,
                          return_raw_data=False):
    # network_type
    # drive: get drivable public streets (but not service roads)
    # drive_service: get drivable public streets including service roads
    # walk: get all streets and paths that pedestrians can use (this network type ignores one-way
    # directionality by always connecting adjacent nodes with reciprocal directed edges)
    # bike: get all streets and paths that cyclists can use
    # all: download all (non-private) OpenStreetMap streets and paths
    # all_private: download all OpenStreetMap streets and paths, including private-access
    
    to_return = {}
    
    for city in cities:
        
        print(city)
        output_folder = output_folder + '/' + city
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)
        place_name = city  # Zwijndrecht, Gent

        G = ox.graph_from_place(place_name, network_type=network_type, buffer_dist=buffer_dist, retain_all=retain_all)
        place = ox.geocode_to_gdf(place_name)

        # store the street network if no enrichment is needed, return raw street network data if desired
        if not intersection_clos and not street_betw and not street_sin:
            output_file = os.path.join(output_folder, '{}_street_network.csv'.format(place_name.lower()))
            edges = ox.utils_graph.graph_to_gdfs(G, nodes=False, edges=True, node_geometry=False, fill_edge_geometry=True)
            edges.to_csv(output_file)

            output_file = os.path.join(output_folder, '{}_intersections.csv'.format(place_name.lower()))
            inter = ox.utils_graph.graph_to_gdfs(G, nodes=True, edges=False, node_geometry=False, fill_edge_geometry=True)
            inter.to_csv(output_file)
            
            if return_raw_data:
                to_return[city] = {
                    'graph': G, 
                    'edges': edges, 
                    'nodes': inter}

        # if Intersections - Nodes store closeness per intersection
        if intersection_clos:
            nodes = compute_node_closeness(G)
            nodes_clipped = gpd.clip(nodes, place)
            output_file = os.path.join(output_folder, '{}_intersections.csv'.format(place_name.lower()))
            nodes.to_csv(output_file)
            print("nodes done")
        
        # Streets - Edges
        if street_betw:
            edges = compute_edge_betweenness(G)
            print("edges betweenness done")
        
        if street_betw and street_sin:
            edges['edge_sinuosity'] = edges.apply(lambda row: compute_edge_sinuosity(row), axis=1)

        if street_sin and not street_betw:
            edges = ox.utils_graph.graph_to_gdfs(G, nodes=False, edges=True, node_geometry=False, fill_edge_geometry=True)
            edges['edge_sinuosity'] = edges.apply(lambda row: compute_edge_sinuosity(row), axis=1)
        
        #edge closeness centrality: convert graph to a line graph so edges become nodes and vice versa
        #edges = nx.closeness_centrality(nx.line_graph(G))

        if street_betw or street_sin:
            edges_clipped = gpd.clip(edges, place)
            output_file = os.path.join(output_folder, '{}_enriched_streets_'.format(place_name.lower()) + network_type +'.csv')
            edges_clipped.to_csv(output_file)

        if return_raw_data:
            return(to_return)

def get_streets_per_bbox(north, south, east, west, network_type='drive', output_folder='.', 
                        intersection_clos=False, street_betw=False, street_sin=False, retain_all=True):
    # network_type
    # drive: get drivable public streets (but not service roads)
    # drive_service: get drivable public streets including service roads
    # walk: get all streets and paths that pedestrians can use (this network type ignores one-way
    # directionality by always connecting adjacent nodes with reciprocal directed edges)
    # bike: get all streets and paths that cyclists can use
    # all: download all (non-private) OpenStreetMap streets and paths
    # all_private: download all OpenStreetMap streets and paths, including private-access 
    place_name = "_".join([str(north), str(south),str(east), str(west)])
    output_folder = output_folder + '/' + "_" + place_name
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    G = ox.graph_from_bbox(north, south, east, west, network_type=network_type, retain_all=retain_all)

    # store the street network if no enrichment is needed
    if not intersection_clos and not street_betw and not street_sin:
        output_file = os.path.join(output_folder, '{}_street_network.csv'.format(place_name.lower()))
        edges = ox.utils_graph.graph_to_gdfs(G, nodes=False, edges=True, node_geometry=False, fill_edge_geometry=True)
        edges.to_csv(output_file)

        output_file = os.path.join(output_folder, '{}_intersections.csv'.format(place_name.lower()))
        inter = ox.utils_graph.graph_to_gdfs(G, nodes=True, edges=False, node_geometry=False, fill_edge_geometry=True)
        inter.to_csv(output_file)

    # if Intersections - Nodes store closeness per intersection
    if intersection_clos:
        nodes = compute_node_closeness(G)
        output_file = os.path.join(output_folder, '{}_intersections.csv'.format(place_name.lower()))
        nodes.to_csv(output_file)
        print("nodes done")
        
    # Streets - Edges
    if street_betw:
        edges = compute_edge_betweenness(G)
        print("edges betweenness done")
    
    if street_betw and street_sin:
        edges['edge_sinuosity'] = edges.apply(lambda row: compute_edge_sinuosity(row), axis=1)

    if street_sin and not street_betw:
        edges = ox.utils_graph.graph_to_gdfs(G, nodes=False, edges=True, node_geometry=False, fill_edge_geometry=True)
        edges['edge_sinuosity'] = edges.apply(lambda row: compute_edge_sinuosity(row), axis=1)
    
    #edge closeness centrality: convert graph to a line graph so edges become nodes and vice versa
    #edges = nx.closeness_centrality(nx.line_graph(G))

    if street_betw or street_sin:
        output_file = os.path.join(output_folder, '{}_enriched_streets_'.format(place_name.lower()) + network_type +'.csv')
        edges.to_csv(output_file)