#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 14:58:20 2020

@author: liliamd
"""
from osgeo import gdal,osr
import numpy as np
from glob import glob

def flattener(lst):
    """
    ==========================================================================================
    Función para aplanar una lista de listas o matriz a una lista sencilla
    ==========================================================================================
    """
    return [item for sublist in lst for item in sublist]

def prueba_contexto(dataPP,dataC07,dif7_14):
    print ("Inicia prueba de contexto")
    pos = np.where(dataPP == 1)   #posiciones de los PP
    filas = pos[0]
    columnas = pos[1]

    for t in zip(filas,columnas):
        pp7 = dataC07[t[0],t[1]]
        ppr = dif7_14[t[0],t[1]]

        k = 7     #tamaño del kernel, 3 o 5 (3x3 o 5x5 o 7x7)
        if k == 3:
            r=1
            s=2
        elif k == 5:
            r=2
            s=3
        elif k ==7:
            r = 3
            s = 4
            
        rec7 = dataC07[t[0]-r:t[0]+s, t[1]-r:t[1]+s]
        recr = dif7_14[t[0]-r:t[0]+s, t[1]-r:t[1]+s]
       
        rec7_2 = flattener(rec7)
        recr_2 = flattener(recr)
        
        rec7_3 = []
        recr_3 = []
        
        for n in rec7_2:
            if n != 0:
                rec7_3.append(n)

        for n in recr_2:
            if n != 0:
                recr_3.append(n)
    
        mean7 = np.mean(rec7_3)
        meanr = np.mean(recr_3)
        
        std7 = np.std(rec7_3)
        stdr = np.std(recr_3)

        if (pp7 > (mean7 + 2.5*std7)) and (ppr > (meanr + 2.5*stdr)):
            dataPP[t] = 1
            #print "  como ",pp7, " es mayor a ",mean1+2*std1,"se queda"
        else:
            dataPP[t] = 0
            #print "  como ",pp7, " es menor a ",mean1+2*std1,"se elimino"
    return dataPP

def creaTifflatlon(data ,ds ,tdato, tifNom):
    """
    ==========================================================================================
    Función que crea un TIFF temporal para la manipulación más sencilla de los datos, este
    TIFF contiene todos los datos de la variable en su proyección original
    ==========================================================================================
    """
    #print ('Creando tif...')

    # Parametros para la creacion del TIFF por medio de GDAL
    nx = data.shape[1]
    ny = data.shape[0]
    geotransform = ds.GetGeoTransform()
    if tdato == "Byte":
        dst_ds = gdal.GetDriverByName('GTiff').Create(tifNom+'.tif', nx, ny, 1, gdal.GDT_Byte)
    elif tdato == "Float32":
        dst_ds = gdal.GetDriverByName('GTiff').Create(tifNom+'.tif', nx, ny, 1, gdal.GDT_Float32)
    # Aplica la geotransformacion y la proyección

    dst_ds.SetGeoTransform(geotransform)    # Coordenadas especificas
    srs = osr.SpatialReference()            # Establece el ensamble
    srs.ImportFromProj4("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs") # Proeyeccion Goes16
    dst_ds.SetProjection(srs.ExportToWkt()) # Exporta el sistema de coordenadas
    dst_ds.GetRasterBand(1).WriteArray(data)   # Escribe la banda al raster
    dst_ds.FlushCache()                     # Escribe en el disco
    dst_ds = None
    
def pp_pc(path_masc_agua, path_masc_des, path_masc_urb, path_prueba, u07, udif, fecha_dtobj, path_pc_tif, path_num_pc):
    
    ds = gdal.Open(path_masc_agua+'Mask_Agua.tif')
    dataAGUA = ds.ReadAsArray()
    ds = gdal.Open(path_masc_des+'Mask_Des.tif')
    dataDES = ds.ReadAsArray()
    ds = gdal.Open(path_masc_urb+'Mask_Urb.tif')
    dataURB = ds.ReadAsArray()
    
    dsC07 = gdal.Open(glob(path_prueba+"*CMI*C07*"+".tif")[0])  
    dataC07 = dsC07.ReadAsArray()
    dsC14 = gdal.Open(glob(path_prueba+"*CMI*C14*"+".tif")[0])  
    dataC14 = dsC14.ReadAsArray()
    
    #banda 7 reclasificada
    dataC07_r = np.where(dataC07 > u07, 1, 0)

    #diferencia de bandas
    dif7_14 = dataC07 - dataC14
    
    #diferencia reclasificada
    dif7_14_r = np.where(dif7_14 > udif,1, 0)

    dataPP = dataC07_r * dif7_14_r * dataAGUA * dataURB * dataDES
    
    count = np.count_nonzero(dataPP == 1)
    print ('Incendios antes de PC ', fecha_dtobj, ':',count)
    
    dataPC = prueba_contexto(dataPP,dataC07,dif7_14)
    
    count1 = np.count_nonzero(dataPP == 1)
    print ('Incendios despues de PC ', fecha_dtobj, ':',count1)
    
    #crea los tif en 1 y 0 pero se desahabilito por que no es necesario y ocupa mucho espacio
    #creaTifflatlon(dataPC,dsC07,"Byte",path_pc_tif + "GIM10_PC_" + fecha_dtobj.strftime("%Y%m%d%H%M"))
    
    f1 = open(path_num_pc+"numero_pc_"+fecha_dtobj.strftime("%Y%m%d")+".txt",'a')
    f1.write('%s \t' %fecha_dtobj.strftime("%Y-%m-%d %H:%M"))
    f1.write('%s \t' %u07)
    f1.write('%s \t' %udif)
    f1.write('%s \t' %count)
    f1.write('%s \n' %count1)
    f1.close()

    return dataPC