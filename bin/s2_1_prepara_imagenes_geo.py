# -*- coding: utf-8 -*-
"""
Created on Sun Feb 16 23:14:55 2020

@author: colve
"""
from glob import glob
from netCDF4 import Dataset 
from datetime import datetime
import os
from osgeo import gdal,osr
import numpy as np

def createdir(path,h):
    os.system("mkdir " + path + h)
    
def extractdata(ds,type_d):
    if type_d == "banda":
        data = ds.variables[list(ds.variables.keys())[2]][:].data 
    elif type_d == "producto":
        data = ds.variables[list(ds.variables.keys())[13]][:].data 
    return data

def extractbounds(ds):
    H = ds.variables['goes_imager_projection'].perspective_point_height
    xmin = ds.variables['x_image_bounds'][0] * H
    xmax = ds.variables['x_image_bounds'][1] * H
    ymin = ds.variables['y_image_bounds'][0] * H
    ymax = ds.variables['y_image_bounds'][1] * H
    return xmax,xmin,ymax,ymin

def creaTiffGeos(data,ds,path):
    print ('Creando tif...')
    xmax,xmin,ymax,ymin = extractbounds(ds)
    nx = data.shape[1]
    ny = data.shape[0]
    # Parametros para la creacion del TIFF por medio de GDAL
    xres = (xmax - xmin) / float(ny)
    yres = (ymax - ymin) / float(nx)
    geotransform = (xmin, xres, 0, ymin, 0, yres)
    name = ds.filepath().split("/")[-1]
    name = str(name)
    dst_ds = gdal.GetDriverByName('GTiff').Create(path + name.replace(".nc","_geos.tif"), ny, nx, 1, gdal.GDT_Float32)
    # Aplica la geotransformacion y la proyección
    dst_ds.SetGeoTransform(geotransform)    # Coordenadas especificas
    srs = osr.SpatialReference()          # Establece el ensamble
    srs.ImportFromProj4('+proj=geos +h=35786023.0 +ellps=GRS80 +lat_0=0.0 +lon_0=-75.0 +sweep=x +no_defs') # Proeyeccion Goes16
    dst_ds.SetProjection(srs.ExportToWkt()) # Exporta el sistema de coordenadas
    dst_ds.GetRasterBand(1).WriteArray(data)   # Escribe la banda al raster
    dst_ds.FlushCache()                     # Escribe en el disco
    dst_ds = None
    
def rec_geos(ds):
    VenMex = [-4079059.0,3396435.0,-501104.0,1054022.0]
    name = ds.GetDescription().replace(".tif","_mex.tif")
    print ("recortando: ",name)
    gdal.Translate(name,ds,options = gdal.TranslateOptions(projWin=VenMex,noData=np.nan))

def reproj(ds):
    name = ds.GetDescription().replace("geos_mex.tif","geo.tif")
    print ("reproyectando: ",name)
    gdal.Warp(name,ds,options=gdal.WarpOptions(dstSRS="EPSG:4326",yRes=0.018,xRes=0.018,dstNodata=np.nan))
    
def rec_geo(ds,name):
    VenMex = [-118.3,33.6,-80.7,10.1]
    print ("recortando: ",name)
    gdal.Translate(path_prueba + name,ds,options = gdal.TranslateOptions(projWin=VenMex,noData=np.nan))

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
    
def nodata(ds,vmin,vmax):
    data = ds.ReadAsArray()
    data = np.where((data>vmax) | (data<vmin),np.nan,data)
    name = ds.GetDescription().split("/")[-1]
    name = name.replace(".tif","_2km")
    creaTifflatlon(data,ds,"Float32",path_prueba + name)
    return data

def prepara_img_geo(path_netcdf,path_img_geo):

    lista_netcdf = glob(path_netcdf + "*CMI*")
    lista_netcdf.sort()
    año_dia_hora = (lista_netcdf[-1].split("/")[-1])[lista_netcdf[-1].split("/")[-1].find("_s")+2:lista_netcdf[-1].split("/")[-1].find("_s")+13]
    
    dtobj = datetime.strptime(año_dia_hora, "%Y%j%H%M")
    createdir(path_img_geo,str(dtobj.year))
    createdir(path_img_geo+str(dtobj.year)+"/"+str(dtobj.timetuple().tm_yday).zfill(3))
    createdir(path_img_geo+str(dtobj.year)+"/"+str(dtobj.timetuple().tm_yday).zfill(3)+"/"+str(dtobj.hour).zfill(2)+str(dtobj.minute).zfill(2))
    
    global path_prueba
    path_prueba = path_img_geo+str(dtobj.year)+"/"+str(dtobj.timetuple().tm_yday).zfill(3)+"/"+str(dtobj.hour).zfill(2)+str(dtobj.minute).zfill(2)+"/"
    
    ds07 = Dataset(glob(path_netcdf+"*CMI*C07*s"+año_dia_hora+"*"+".nc")[0])
    ds14 = Dataset(glob(path_netcdf+"*CMI*C14*s"+año_dia_hora+"*"+".nc")[0])
    
    data07 = extractdata(ds07,"banda")
    data14 = extractdata(ds14,"banda")
    

    creaTiffGeos(data07,ds07,path_prueba)
    creaTiffGeos(data14,ds14,path_prueba)
    
    for n in os.listdir(path_prueba):
        if n.endswith("geos.tif"):
            ds_geos = gdal.Open(path_prueba + n)
            rec_geos(ds_geos)
            os.remove(path_prueba + n)
    
    for n in os.listdir(path_prueba):
        if n.endswith("geos_mex.tif"):
            ds_geos = gdal.Open(path_prueba + n)
            reproj(ds_geos)
            os.remove(path_prueba + n)
    
    for n in os.listdir(path_prueba):
        if n.endswith("geo.tif"):
            ds_geo = gdal.Open(path_prueba + n)
            name = n.replace(".tif","_mex.tif")
            rec_geo(ds_geo,name)
            os.remove(path_prueba + n)
    
    dsC07 = gdal.Open(glob(path_prueba +  "*CMI*C07*geo_mex.tif")[0])
    dsC14 = gdal.Open(glob(path_prueba +  "*CMI*C14*geo_mex.tif")[0])
    
    nodata(dsC07,197.31,411.86)
    nodata(dsC14,96.19,341.28)
    
    for n in os.listdir(path_prueba):
        if n.endswith("_mex.tif"):
            os.remove(path_prueba+n)
        if n.endswith(".xml"):
            os.remove(path_prueba+n)
            
            
    return dtobj, path_prueba