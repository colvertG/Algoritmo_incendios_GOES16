#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: colvert 
"""

import confire as cf
import shutil

#Creando puntos virrs:
import s1_1_crea_puntos_firms as s_cpf
path_puntos_viirs = cf.datos_aux_dir + "vectorial/puntos_viirs/"
path_puntos_viirs_temp = cf.datos_aux_dir + "vectorial/puntos_viirs/temp/"
año_dia = s_cpf.crea_puntos_viirs(path_puntos_viirs,path_puntos_viirs_temp)

#Creando tif de canal 7, 14 y dif, recorte en geoestacionaria:
import s1_2_netcdf_to_tif as s_n2t
path_img_geos = cf.datos_aux_dir + "raster/img_goes_geos/"
path_img_geos_prueba = s_n2t.netcdf_to_tiff(cf.netcdf_dir_aws, path_img_geos, año_dia)

#Creando eventos viirs:
import s1_3_crea_eventos_viirs as s_cev
path_eventos_viirs = cf.datos_aux_dir + "vectorial/eventos_viirs/"
path_eventos_viirs_filtrados = cf.datos_aux_dir + "vectorial/eventos_viirs_filtrados/"
s_cev.crea_eventos_viirs(path_puntos_viirs, path_eventos_viirs, path_eventos_viirs_filtrados, año_dia)

#Creando valores muestreados de C07 y dif:
path_muestras_goes_viirs = cf.datos_aux_dir + "vectorial/muestras_goes_viirs/"
import s1_4_muestras_goes_xdia as s_mgd
s_mgd.muestras_goes_c07(path_eventos_viirs_filtrados, path_img_geos_prueba, path_muestras_goes_viirs, año_dia)
s_mgd.muestras_goes_dif07_14(path_eventos_viirs_filtrados, path_img_geos_prueba, path_muestras_goes_viirs, año_dia)
shutil.rmtree(path_img_geos_prueba, ignore_errors=True)

#Creando los umbrales del dia:
path_umbrales = cf.datos_aux_dir + "vectorial/umbrales/"
import s1_5_crea_umbrales as s_cu
s_cu.crea_umbrales_c07(path_muestras_goes_viirs, path_umbrales, año_dia)
s_cu.crea_umbrales_dif07_14(path_muestras_goes_viirs, path_umbrales, año_dia)