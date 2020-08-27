#!/usr/bin/env python3
# coding: utf-8

# # Ejercicio 02 - preparacion de los datos VIIRS 
# En 08/ago/2019 empezamos a adaptar el procedimiento para los datos viirs para despues probar la metodologia para validacion.

# Importacion de librerias

import glob, os
import geopandas as gpd
import pandas as pd
import datetime as dt
from shapely.geometry.polygon import Polygon
from shapely.geometry.multipolygon import MultiPolygon

def explode2(indataframe):
    intdf = indataframe
    outdf = gpd.GeoDataFrame(columns=intdf.columns, crs=intdf.crs)
    for idx, row in intdf.iterrows():
        if type(row.geometry) == Polygon:
            outdf = outdf.append(row,ignore_index=True)
        if type(row.geometry) == MultiPolygon:
            multdf = gpd.GeoDataFrame(columns=intdf.columns, crs=intdf.crs)
            recs = len(row.geometry)
            multdf = multdf.append([row]*recs,ignore_index=True)
            for geom in range(recs):
                multdf.loc[geom,'geometry'] = row.geometry[geom]
            outdf = outdf.append(multdf,ignore_index=True)
    return outdf

# direcion de los datos de entrada
# /Users/fabianomorelli/ownCloud/notebooks/ipython_notebooks/procesamiento_goes16_mx/salidas_operativas/shapefiles/puntos_viirs/viirs_20190508.shp

def crea_eventos_viirs(path_entrada, path_salida1, path_salida2, año_dia):

    fecha_shp = dt.datetime.strptime(str(año_dia), "%Y%j")
    print(os.path.join(path_entrada , "V_FIRMS_{}/V_FIRMS_{}.shp".format(fecha_shp.strftime("%Y%m%d"),fecha_shp.strftime("%Y%m%d") )))
    
    lista_ficheiros = glob.glob(os.path.join(path_entrada , "V_FIRMS_{}/V_FIRMS_{}.shp".format(fecha_shp.strftime("%Y%m%d"),fecha_shp.strftime("%Y%m%d") )))
    lista_ficheiros.sort()
    print (lista_ficheiros)
    
    df_salida = gpd.read_file(lista_ficheiros[0], parse_dates=[[5,6]])
    
    df_salida["fecha"] = pd.to_datetime(df_salida.ACQ_DATE +" "+ df_salida.ACQ_TIME)
    
    
    colunas_borar = df_salida.columns[0:13]
    
    df_puntos = df_salida.copy()
    
    df_salida.drop(colunas_borar, axis=1, inplace=True)
    df_salida["geom_pix"] = df_salida.geometry.buffer(0.0025, cap_style=3)
    df_salida.set_geometry(col="geom_pix", inplace=True, drop=True)
    df_salida["fecha"] = df_salida.fecha.astype(str)
    df_salida = df_salida.dissolve("fecha")
    df_salida.reset_index(inplace=True)
    df_salida = explode2(df_salida)
    df_salida["areakm2"] = df_salida.geometry.to_crs(epsg=6362).area/1000000
    
    nombre_salida = os.path.join(path_salida1 , "viirs_dsv_hora_{}.shp".format(año_dia))
    
    df_salida.to_file(nombre_salida)
    
    # # Prepara la salida del evento del dia
    df_salida["dia"] = pd.to_datetime(df_salida.fecha).dt.day
    df_salida = df_salida.dissolve(df_salida.dia)
    df_salida.drop(["fecha", "dia"], axis=1, inplace=True)
    df_salida.reset_index(inplace=True)
    df_salida = explode2(df_salida)
    df_salida["areakm2"] = df_salida.geometry.to_crs(epsg=6362).area/1000000
    
    
    # # Hace la mescla con puntos
    # agora efetivamente o cruzamento espacial que ira filtrar apenas os focos contidos no poligono
    puntos = gpd.sjoin(df_puntos, df_salida, how='inner', op='within')
    
    # voce pode utilizar outros metodos no parametro how para definir o retorno
    # por exemplo, se utilizar how='left' vai retornar todos os focos e colocar atributos
    # do shapefile brasil apenas naqueles que estiverem contidos no polígono
    
    df_summary = puntos[["index_right", "fecha"]].copy()
    df_summary.rename(columns={"index_right":"evnt_id"}, inplace=True)
    df_summary["hora"] = df_summary.fecha.dt.hour
    df_summary.reset_index(inplace=True, drop=True)
    df_summary2 = pd.DataFrame(df_summary.groupby(["evnt_id"])["hora"].unique())
    df_summary2.reset_index(inplace=True)
    df_summary2["npuntos"] = pd.DataFrame(df_summary.groupby(["evnt_id"])["hora"].count())
    df_summary2["first"] = pd.DataFrame(df_summary.groupby(["evnt_id"])["hora"].first())-1
    df_summary2["last"] = pd.DataFrame(df_summary.groupby(["evnt_id"])["hora"].last())+1
    df_summary2["nhoras"] = df_summary2["last"] - df_summary2["first"]
    
    evnt_ref = pd.concat([df_salida, df_summary2], axis=1)
    evnt_ref = evnt_ref[(evnt_ref.nhoras > 2) & (evnt_ref.npuntos > 2) & (evnt_ref.areakm2 >= 1 )]
    evnt_ref.drop(["hora"], axis=1, inplace=True)
    
    nombre_salida = os.path.join(path_salida2 , "evnt_viirs_ref_{}.shp".format(año_dia))
    evnt_ref.to_file(nombre_salida)
    
    print("final del proceso!")
