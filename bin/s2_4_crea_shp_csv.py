#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 16:21:16 2020

@author: liliamd
"""
import numpy as np 
from osgeo import gdal
import geopandas as gpd
from glob import glob
from shapely.geometry import Point
import pandas as pd
import os

def loc_estado(x,y,shp_div_est):
    geometry = [Point(x, y)]
    df = gpd.GeoDataFrame(geometry=geometry)
    #print "tin"
    pointInPolys = gpd.tools.sjoin(df, shp_div_est, how='left',op="within")
    #print "tin"
    #print pointInPolys["NOM_ENT"][0]
    return pointInPolys["ENTIDAD"].values[0]

def loc_pais(x,y,shp_div_pais):
    geometry = [Point(x, y)]
    df = gpd.GeoDataFrame(geometry=geometry)
    pointInPolys = gpd.tools.sjoin(df, shp_div_pais, how='left',op="within")
    #print pointInPolys["NAME_ES"][0]
    return pointInPolys["NAME_ES"].values[0]

def loc_anp(x,y,shape_anp):
    geometry = [Point(x, y)]
    df = gpd.GeoDataFrame(geometry=geometry)
    pointInPolys = gpd.tools.sjoin(df, shape_anp, how='left',op="within")
    #print "tan"
    #print pointInPolys["ID_ANP"].values[0]
    return pointInPolys["ID_ANP"].values[0]

def name_lc(lc):
    if lc == 1:
        name_lc = "Evergreen Needleleaf Forests"
    elif lc == 2:
        name_lc = "Evergreen Broadleaf Forests"
    elif lc == 3:
        name_lc = "Deciduous Needleleaf Forests"
    elif lc == 4:
        name_lc = "Deciduous Broadleaf Forests"
    elif lc == 5:
        name_lc = "Mixed Forests"
    elif lc == 6:
        name_lc = "Closed Shrublands"
    elif lc == 7:
        name_lc = "Open Shrubland"
    elif lc == 8:
        name_lc = "Woody Savannas"
    elif lc == 9:
        name_lc = "Savannas"
    elif lc == 10:
        name_lc = "Grasslands"
    elif lc == 11:
        name_lc = "Permanent Wetlands"
    elif lc == 12:
        name_lc = "Croplands"
    elif lc == 13:
        name_lc = "Urban and Built-up Lands"
    elif lc == 14:
        name_lc = "Cropland/Natural Vegetation Mosaics"    
    elif lc == 15:
        name_lc = "Permanent Snow and Ice"
    elif lc == 16:
        name_lc = "Barren"
    elif lc == 17:
        name_lc = "Water Bodies"
    return name_lc

def crea_csv_shp_24hrs(path_csv_10min, path_shp_10min, path_csv_24hrs, path_shp_24hrs):
    lista_archivos=[]
    for n in os.listdir(path_shp_10min):
        if n.endswith(".shp"):
            lista_archivos.append(n)
            
    lista_archivos.sort()
    
    gdf_dia = gpd.GeoDataFrame()
    for n in np.arange(1,144):
        print (lista_archivos[-n])
        gdf = gpd.read_file(path_shp_10min + lista_archivos[-n])
        gdf_dia = gdf_dia.append(gdf)
        
    gdf_dia["geom"] = gdf_dia["lat"] * gdf_dia["lon"]
    gdf_dia["freq"] = gdf_dia.groupby("geom")["geom"].transform("count")
    gdf_dia = gdf_dia.drop(columns=["geom"])
    gdf_dia["freq_norm"] = (gdf_dia["freq"] * 100) / 144
    gdf_dia.to_file(path_shp_24hrs + "GIM10_PC_24hrs.shp", driver = 'ESRI Shapefile')
    gdf_dia = gdf_dia.drop(columns=["geometry"])
    gdf_dia.to_csv(path_csv_24hrs + "GIM10_PC_24hrs"+".csv", index = False)

def crea_shp_csv(dataPC, fecha_dtobj, path_pc_tif, path_prueba, path_div_pol_est, path_div_pol_pais, path_anp, path_land_cover, path_csv_10min, path_shp_10min, path_csv_24hrs, path_shp_24hrs):
    
    num_incendios = np.count_nonzero(dataPC == 1)
    if num_incendios > 0:
        #ds = gdal.Open(path_pc_tif + "GIM10_PC_" + fecha_dtobj.strftime("%Y%m%d%H%M")+".tif")
        #os.remove(path_pc_tif + "GIM10_PC_" + fecha_dtobj.strftime("%Y%m%d%H%M")+".tif")
        (filas,columnas) = np.where(dataPC == 1)
    
 
        ds = gdal.Open(glob(path_prueba+"*CMI*C07*"+".tif")[0])  
        dataC07 = ds.ReadAsArray()
        ds = gdal.Open(glob(path_prueba+"*CMI*C14*"+".tif")[0])  
        dataC14 = ds.ReadAsArray()

        shp_div_est  = gpd.read_file(path_div_pol_est + 'destdv1gw.shp')
        shp_div_pais  = gpd.read_file(path_div_pol_pais + 'ne_10m_admin_0_countries_geo.shp')
        shp_anp  = gpd.read_file(path_anp + '182ANP_Geo_WGS84_Julio04_2019_geo.shp')
        
        ds = gdal.Open(path_land_cover + 'Land_Cover_MCD12Q1_IGBP_geo.tif')
        dataCOVER = ds.ReadAsArray()
        
        (upper_left_x, x_size, x_rotation, upper_left_y, y_rotation, y_size) = ds.GetGeoTransform()
        
        df = pd.DataFrame(columns = ['lon','lat','Satelite','BT_c07','BT_c14','dif_c07-c14','Fecha','Hora','Land_Cover','Estado','Pais','ANP'])
        
        for f,c in zip(filas,columnas):
            lat = f * y_size + upper_left_y + (y_size / 2)
            lon = c * x_size + upper_left_x + (x_size / 2)
    
            estado = loc_estado(lon,lat,shp_div_est)
            pais = loc_pais(lon,lat,shp_div_pais)
            anp = loc_anp(lon,lat,shp_anp)

            dif7_14 = dataC07 - dataC14
            
            pp7 = dataC07[f,c]
            pp14 = dataC14[f,c]
            ppr = dif7_14[f,c]
            lc = dataCOVER[f,c]
            lc_name = name_lc(lc)
    
            pp7 = float('%.2f' %pp7)
            pp14 = float('%.2f' %pp14)
            ppr = float('%.2f' %ppr)
    
            df = df.append({'lon':lon, 'lat':lat, 'Satelite':"Goes-16", 'BT_c07':pp7, 'BT_c14':pp14, 'dif_c07-c14':ppr, 'Fecha':fecha_dtobj.strftime("%Y-%m-%d"), 'Hora':fecha_dtobj.strftime("%H:%M"), 'Land_Cover':lc_name, 'Estado':estado, 'Pais':pais, 'ANP':anp},ignore_index=True)
        
        df.to_csv(path_csv_10min + "GIM10_PC_" + fecha_dtobj.strftime("%Y%m%d%H%M") + ".csv", index = False)
        
        df['geometry'] = df.apply(lambda row: Point(row.lon, row.lat), axis=1)
        gdf = gpd.GeoDataFrame(df, geometry='geometry')
        gdf.crs = "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"
        gdf.to_file(path_shp_10min + "GIM10_PC_" + fecha_dtobj.strftime("%Y%m%d%H%M") + ".shp", driver='ESRI Shapefile')
        crea_csv_shp_24hrs(path_csv_10min, path_shp_10min, path_csv_24hrs, path_shp_24hrs)