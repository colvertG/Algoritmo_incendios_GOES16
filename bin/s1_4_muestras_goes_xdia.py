#!/usr/bin/env python3
# coding: utf-8
# # Proceso automatizado de recoleta de valores del canal 07
# hecho nel dia 14/ago/2019
#

import os
import glob
import geopandas as gpd
import pandas as pd
from rasterstats import zonal_stats

def muestreador_c07(shp_eventos_buffer, gdf_evnt_buffer, file):
    fecha = os.path.basename(file).split("_")[3][1:12]
    data = zonal_stats(shp_eventos_buffer, file, all_touched=True)
    a = gdf_evnt_buffer.join(pd.DataFrame(data, columns=['max']))
    a.rename(columns={"max":"ch7"}, inplace=True)
    a["fecha"] = fecha
    return a[['evnt_id', 'ch7', 'fecha']]
    

def muestreador_dif(shp_eventos_buffer, gdf_evnt_buffer, file):
    fecha = os.path.basename(file).split("_")[3][1:12]
    data = zonal_stats(shp_eventos_buffer, file, all_touched=True)
    a = gdf_evnt_buffer.join(pd.DataFrame(data, columns=['max']))
    a.rename(columns={"max":"dif7_14"}, inplace=True)
    a["fecha"] = fecha
    return a[['evnt_id', 'dif7_14', 'fecha']]

def muestras_goes_c07(path_eventos_viirs_filtrados, path_img_geos, path_muestras, año_dia):
    
    proj_geos = "+proj=geos +h=35786023.0 +ellps=GRS80 +lat_0=0.0 +lon_0=-75.0 +sweep=x +no_defs"
    #proj_geos = "+proj=geos +h=35774290 +a=6378137 +b=6378137 +lon_0=-75 +units=m +nodefs"
    print("inicio del procesamiento para el dia {}".format(año_dia))
    
    shp_eventos_ref = os.path.join(path_eventos_viirs_filtrados, "evnt_viirs_ref_{}.shp".format(año_dia))
    shp_eventos_buffer = os.path.join(path_eventos_viirs_filtrados,"evnt_viirs_1km_{}.shp".format(año_dia))

    
    # ## Creacion de um buffer temporario de 1000m al rededor de los eventos de referencia
    
    gdf_evnt = gpd.read_file(shp_eventos_ref)
    
    # Transforma los eventos a la projeccion GEOS
    a = gdf_evnt.to_crs(crs=proj_geos)
    
    a["geom_pix"] = a.geometry.buffer(1000)
    a.set_geometry(col="geom_pix", inplace=True, drop=True)
    
    a.to_file(shp_eventos_buffer)
    del(a)
    
    # ## Tomar los valores desde las imagenes
    gdf_evnt_buffer = gpd.read_file(shp_eventos_buffer)
    
    # para buscar apenas las imagenes en hora:00
    #lista_img = glob.glob(os.path.join(path_img_goes , "*/OR_ABI-L2-CMIPF-M6C07_G16_s2019129??00*_ccl_mex_2km.tif"))
    
    # para buscar todas las imagenes del dia
    img2buscar = os.path.join(path_img_geos , "OR_ABI-L2-CMIPF-M6C07_G16_s{}*.tif".format(año_dia))
    lista_img = glob.glob(img2buscar)
    
    lista_img.sort()
    

    
    df0 = muestreador_c07(shp_eventos_buffer, gdf_evnt_buffer, lista_img[0])
    for i in range(len(lista_img)):
        df2 = muestreador_c07(shp_eventos_buffer, gdf_evnt_buffer, lista_img[i])
        if i == 0:
            df_salida = df0.copy()
        else:
            df_salida = pd.concat([df_salida, df2], ignore_index=True)
        del(df2)
    del(df0)
        
    
    df_salida.to_csv(os.path.join(path_muestras, "valores_muestreados_ch07_{}.csv".format(año_dia)))
    
    print("final del proceso!")

def muestras_goes_dif07_14(path_eventos_viirs_filtrados, path_img_geos_prueba, path_muestras, año_dia):
    
    print("inicio del procesamiento para el dia {}".format(año_dia))
    
    shp_eventos_buffer = os.path.join(path_eventos_viirs_filtrados, "evnt_viirs_1km_{}.shp".format(año_dia))

    # ## Tomar los valores desde las imagenes
    gdf_evnt_buffer = gpd.read_file(shp_eventos_buffer)
    
    # para buscar apenas las imagenes en hora:00
    #lista_img = glob.glob(os.path.join(path_img_goes , "*/OR_ABI-L2-CMIPF-M6C07_G16_s2019129??00*_ccl_mex_2km.tif"))
    
    # para buscar todas las imagenes del dia   OR_ABI-L2-DIF_C07_C14_G16_s20191281940303.tif
    img2buscar = os.path.join(path_img_geos_prueba , "OR_ABI-L2-CMIPF-M6DIFC07-C14_G16_s{}*.tif".format(año_dia))
    lista_img = glob.glob(img2buscar)
    lista_img.sort()
    
   
    df0 = muestreador_dif(shp_eventos_buffer, gdf_evnt_buffer, lista_img[0])
    for i in range(len(lista_img)):
        
        df2 = muestreador_dif(shp_eventos_buffer, gdf_evnt_buffer, lista_img[i])
        if i == 0:
            df_salida = df0.copy()
        else:
            df_salida = pd.concat([df_salida, df2], ignore_index=True)
        del(df2)
    del(df0)
    
    df_salida.to_csv(os.path.join(path_muestras, "valores_muestreados_dif7_14_{}.csv".format(año_dia)))
    print("final del proceso!")