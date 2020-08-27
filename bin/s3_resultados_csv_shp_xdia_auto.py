#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 17:46:55 2020

@author: colvert
"""

import geopandas as gpd
import os
from datetime import datetime
import confire as cf

path_shp_10min = cf.resultados_dir + "shp_10min/"
path_shp_dia = cf.resultados_dir + "shp_dia/"
path_csv_10min = cf.resultados_dir + "csv_10min/"
path_csv_dia = cf.resultados_dir + "csv_dia/"

def crea_archivo_dia():
    lista_archivos=[]
    for n in os.listdir(path_shp_10min):
        if n.endswith(".shp"):
            lista_archivos.append(n)
    lista_archivos.sort()
    
    fechas = []
    for n in lista_archivos:
        fechas.append(n[9:17])
        
    fechas_unicas = set(fechas)
    fechas_unicas = list(fechas_unicas)
    fechas_unicas.sort()
    fecha = fechas_unicas[-2]
    #dias_prueba = ["121"]
    
    
    date_object = datetime.strptime(fecha,"%Y%m%d")
    gdf_dia = gpd.GeoDataFrame()
    print ("dia: ",date_object)
    for i in lista_archivos:
        if i[9:17] == fecha:
            gdf = gpd.read_file(path_shp_10min + i)
            gdf_dia = gdf_dia.append(gdf)
    gdf_dia["geom"] = gdf_dia["lat"] * gdf_dia["lon"]
    gdf_dia["freq"] = gdf_dia.groupby("geom")["geom"].transform("count")
    gdf_dia = gdf_dia.drop(columns=["geom"])
    gdf_dia["freq_norm"] = (gdf_dia["freq"] * 100) / 144
    gdf_dia.to_file(path_shp_dia + i[:9] + str(date_object.year) + str(date_object.month).zfill(2) + str(date_object.day).zfill(2) + ".shp", driver = 'ESRI Shapefile')
    gdf_dia = gdf_dia.drop(columns=["geometry"])
    gdf_dia.to_csv(path_csv_dia + "GIM10_PC_"+fecha+".csv", index = False)
    
crea_archivo_dia()
