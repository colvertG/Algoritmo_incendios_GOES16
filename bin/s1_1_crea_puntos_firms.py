# -*- coding: utf-8 -*-
"""
@author: colvert
"""

import os
from datetime import datetime
import requests
import zipfile
import geopandas as gpd

def crea_puntos_viirs(path_out,path_temp):
    """
    Descarga producto FIRMS VIIRS 375m / S-NPP, recorte de Centroamérica de las 
    ultimas 24hrs, descomprime los datos y filtra los puntos del último día 
    para generar el producto FIRMS de un único día, crea un shp con estos datos 
    con el nombre V_FIRMS_YYYYMMDD.shp
    
    Parameters
    ----------
    path_out : str
        Directorio donde guardara los resultados
    path_temp : str
        Directorio temporal donde guarda los datos descargados sin procesar

    Returns
    -------
    año_dia : str
        Año y día juliano de la ejecución, ejemplo 2020135
    """
    
    name_file_zip = "SUOMI_VIIRS_C2_Central_America_24h.zip"
    name_file_shp = "SUOMI_VIIRS_C2_Central_America_24h.shp"
    
    #Descarga los datos en una carpeta temporal:
    url = 'https://firms.modaps.eosdis.nasa.gov/data/active_fire/suomi-npp-viirs-c2/shapes/zips/SUOMI_VIIRS_C2_Central_America_24h.zip'
    myfile = requests.get(url)    
    open(path_temp + name_file_zip, 'wb').write(myfile.content)
    myfile.close()
    
    #Descompresión del zip:
    zf = zipfile.ZipFile(path_temp + name_file_zip, "r")
    for i in zf.namelist():
        zf.extract(i, path = path_temp)
    zf.close()
    
    #Lectura del shp en un gdf y encontrar la fecha:
    gdf_viirs = gpd.read_file(path_temp + name_file_shp, parse_dates=[[5,6]])
    fecha_prueba = gdf_viirs['ACQ_DATE'].iloc[-1]
    
    #Limpia los datos:
    for index, row in gdf_viirs.iterrows():
        if row["ACQ_DATE"] != fecha_prueba:
            gdf_viirs.drop(index, inplace=True)
    
    #Obteniendo número de día del año con datatime.tm_yday:
    dtobj = datetime.strptime(fecha_prueba, "%Y-%m-%d")
    tt = dtobj.timetuple()
    num_dia = str(tt.tm_yday)
    num_dia = num_dia.zfill(3) 
    año_dia = fecha_prueba[:4] + num_dia
    
    #Borrando los archivos temporales
    for n in os.listdir(path_temp):
        os.remove(path_temp+n)
            
    #Creando el archivo FIRMS del dia
    gdf_viirs.crs= "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"
    gdf_viirs.to_file(path_out + "V_FIRMS_" + fecha_prueba[:4] + fecha_prueba[5:7] + fecha_prueba[-2:], driver='ESRI Shapefile')
    
    print ("Puntos viirs creados para la fecha: ",dtobj," numero de dia: ",num_dia)
    return año_dia