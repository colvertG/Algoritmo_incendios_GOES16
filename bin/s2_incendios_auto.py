#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 18:16:42 2019

@author: becario
"""
import confire as cf
import shutil

#preparando imagenes en geograficas:
path_img_geo = cf.datos_aux_dir + "raster/img_goes_geo/"
import s2_1_prepara_imagenes_geo as s_pig
fecha_dtobj, path_prueba = s_pig.prepara_img_geo(cf.netcdf_dir,path_img_geo)
print (fecha_dtobj)
print (path_prueba)

#Obteniendo umbrales, maximo de 10 dias:
path_umbrales = cf.datos_aux_dir + "vectorial/umbrales/"
import s2_2_extrae_umbral_10dias_max as s_eu10m
u07,udif = s_eu10m.umbral_10dias_max(fecha_dtobj, path_umbrales)

#pixel potencial y prueba de contexto, PC detectados, asi como el archivo txt de numero de incendios detectados
path_masc_agua = cf.datos_aux_dir + "raster/masc_agua/"
path_masc_des = cf.datos_aux_dir + "raster/masc_des/"
path_masc_urb = cf.datos_aux_dir + "raster/masc_urb/"
path_pc_tif = cf.resultados_dir + "pc_tif_10min/"
path_num_pc = cf.resultados_dir + "registro_num_pc/"
import s2_3_pp_y_pc as s_pppc
dataPC = s_pppc.pp_pc(path_masc_agua, path_masc_des, path_masc_urb, path_prueba, u07, udif, fecha_dtobj, path_pc_tif, path_num_pc)


#crea shp y csv:
path_div_pol_est = cf.datos_aux_dir + "vectorial/div_pol_est/"
path_div_pol_pais = cf.datos_aux_dir + "vectorial/div_pol_pais/"
path_anp = cf.datos_aux_dir + "vectorial/anp/"
path_land_cover = cf.datos_aux_dir + "raster/land_cover/"
path_csv_10min = cf.resultados_dir + "csv_10min/"
path_shp_10min = cf.resultados_dir + "shp_10min/"
path_csv_24hrs = cf.resultados_dir + "csv_24hrs/"
path_shp_24hrs = cf.resultados_dir + "shp_24hrs/"
import s2_4_crea_shp_csv as s_csc
s_csc.crea_shp_csv(dataPC, fecha_dtobj, path_pc_tif, path_prueba, path_div_pol_est, path_div_pol_pais, path_anp, path_land_cover, path_csv_10min, path_shp_10min,path_csv_24hrs,path_shp_24hrs)
shutil.rmtree(path_prueba, ignore_errors=True)
