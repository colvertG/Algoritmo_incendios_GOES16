# -*- coding: utf-8 -*-
"""
@author: colvert
"""

from glob import glob
from netCDF4 import Dataset 
from datetime import datetime
import os
from osgeo import gdal,osr
import numpy as np

def createdir(path,name):
    """
    Crea una directorio

    Parameters
    ----------
    path : str
        Ruta donde se creara el directorio
    h : str
        Nombre del directorio

    Returns
    -------
    None.
    """
    
    os.system("mkdir " + path + name)
    
def extractdata(ds):
    """
    Extrae la variable CMI del NETCDF

    Parameters
    ----------
    ds : netCDF4._netCDF4.Dataset
        Dataset de la banda de GOES

    Returns
    -------
    data : numpy.ndarray
        Matriz de datos CMI
    """
    
    data = ds.variables['CMI'][:].data     
    return data

def creaTiffGeos(data,ds,name,path):
    """
    Crea Tif en coordenadas geoestacionarias de GOES-16

    Parameters
    ----------
    data : numpy.ndarray
        Matriz de datos CMI
    ds : netCDF4._netCDF4.Dataset
        Dataset de la banda de GOES.
    name : str
        Nombre del archivo de salida (.tif)
    path : str
        Ruta de salida del archivo (.tif)

    Returns
    -------
    None.
    """
    
    # Limites del Dataset en geoestacionarias
    H = ds.variables['goes_imager_projection'].perspective_point_height
    xmin = ds.variables['x_image_bounds'][0] * H
    xmax = ds.variables['x_image_bounds'][1] * H
    ymin = ds.variables['y_image_bounds'][0] * H
    ymax = ds.variables['y_image_bounds'][1] * H
    
    # Parametros para la creacion del TIFF por medio de GDAL
    nx = data.shape[1]
    ny = data.shape[0]
    xres = (xmax - xmin) / float(ny) # Resolución en X
    yres = (ymax - ymin) / float(nx) # Resolución en Y
    geotransform = (xmin, xres, 0, ymin, 0, yres)
    dst_ds = gdal.GetDriverByName('GTiff').Create(path + name, ny, nx, 1, gdal.GDT_Float32)
    
    # Aplica la geotransformacion y la proyección
    dst_ds.SetGeoTransform(geotransform)    # Coordenadas especificas
    srs = osr.SpatialReference()          # Establece el ensamble
    srs.ImportFromProj4('+proj=geos +h=35786023.0 +ellps=GRS80 +lat_0=0.0 +lon_0=-75.0 +sweep=x +no_defs') # Proeyeccion Goes16
    dst_ds.SetProjection(srs.ExportToWkt()) # Exporta el sistema de coordenadas
    dst_ds.GetRasterBand(1).WriteArray(data)   # Escribe los datos al tif
    dst_ds.FlushCache()                     # Escribe en el disco
    dst_ds = None 
    
def trim_geos(ds,coords):
    """
    Recorta un tif en las coordenadas geoestacionarias proporcionadas

    Parameters
    ----------
    ds : osgeo.gdal.Dataset
        Dataset del la imagen a recortar
    coords : list
        Coordenadas de recorte en geoestacionarias [xmin, ymin, xmax, ymax]

    Returns
    -------
    None.
    """
    
    name = ds.GetDescription().replace(".tif","_geos_mex.tif")
    print ("recortando " + name)
    gdal.Translate(name,ds,options = gdal.TranslateOptions(projWin=coords,noData=np.nan))

def valid_range(nband):
    """
    Devuelve el rango valido de valores permitidos en la banda n.

    Parameters
    ----------
    nband : int
        Número de banda

    Returns
    -------
    float
        Valor mínimo permitido para la banda n.
    float
        Valor máximo permitido para la banda n.
    """
    
    list_min = [0,0,0,0,0,0,197.31,138.05,137.7,126.91,127.69,117.49,89.62,96.19,97.38,92.7]
    list_max = [1.3,1.3,1.3,1.3,1.3,1.3,411.86,311.06,311.08,331.2,341.3,311.06,341.27,341.28,341.28,318.26]
    return list_min[nband-1], list_max[nband-1]

def nodata(data,nband):
    """
    Elimina los valores nulos de una matriz 

    Parameters
    ----------
    data : numpy.ndarray
        Matriz de datos CMI
    vmin : float
        Valor mínimo permitido en la imagen 
    vmax : float
        Valor máximo permitido en la imagen 

    Returns
    -------
    data : numpy.ndarray
        Matriz de datos CMI sin valores anormales. 
    """
    
    vmin, vmax = valid_range(nband)
    data = np.where((data>vmax) | (data<vmin),np.nan,data)
    return data


def netcdf_to_tiff(path_input, path_out, año_dia):
    """
    Crea un recorte en formato Tif para América central en coordenadas 
    geoestacionarias de todos los archivos NetCDF que estén en el directorio 
    de entrada.

    Parameters
    ----------
    path_input : str
        Ruta de entrada, donde se encentren los archivos NetCDF a procesar
    path_out : str
        Ruta de salida general: (.../datos_aux/raster/img_goes_geos)
    año_dia : str
        Año y día juliano de la ejecución

    Returns
    -------
    path_out2 : str
        Ruta de salida especifica: (.../datos_aux/raster/img_goes_geos/YYYY/JJJ)
        
    Notes
    -------
    YYYY: Año
    JJJ: Día juliano
    """
    
    # Descargando imagenes de AWS
    for n in os.listdir(path_input):
    	if n.endswith(".nc"):
    		os.remove(path_input + n)

    os.chdir(path_input)
    os.system("sh downloadGOES16.sh " + año_dia[:4] + " " + año_dia[4:])  
    
    # Lista los archivis NetCDF
    lista_netcdf = glob(path_input + "*CMI*")
    lista_netcdf.sort()
    
    # Crea directorio de salida
    dtobj = datetime.strptime(año_dia, "%Y%j")
    createdir(path_out, str(dtobj.year))
    createdir(path_out + str(dtobj.year)+"/", str(dtobj.timetuple().tm_yday).zfill(3))
    path_out2 = path_out + str(dtobj.year) + "/" + str(dtobj.timetuple().tm_yday).zfill(3) + "/"
    
    # Lista banda 7
    lista_img_c07 = []
    for n in lista_netcdf:  
        if n.find("OR_ABI-L2-CMIPF-M6C07_G16_s" + año_dia) != -1:
            lista_img_c07.append(n)
    
    # Crea tif en geoestacioaria full disk
    for c07 in lista_img_c07: 
            ds07 = Dataset(c07)
            try:
                ds14 = Dataset(glob(path_input+"*C14*"+c07.split("/")[-1][25:38]+"*"+".nc")[0])
                data07 = extractdata(ds07)
                data14 = extractdata(ds14)
                data07 = nodata(data07,7)
                data14 = nodata(data14,14)
                dataDif = data07 - data14
                
                creaTiffGeos(data07,ds07,c07.split("/")[-1][:-3] + ".tif",path_out2)
                creaTiffGeos(dataDif,ds14,(c07.split("/")[-1][:-3] + ".tif").replace("C07","DIFC07-C14"),path_out2)
            except:
                continue
        
    # Recorte de mexico del Tif
    VenMex_geos = [-3700000.0,3396435.0,1200000.0,750000.0]
    for n in os.listdir(path_out2):
        ds_geos = gdal.Open(path_out2 + n) 
        trim_geos(ds_geos,VenMex_geos)
        os.remove(path_out2 + n) # Elimina el tif en full disk
    
    # Elimina basura del directorio
    for n in os.listdir(path_out2):
        if n.endswith(".xml"):
            os.remove(path_out2 + n)
            
    return path_out2

    # Vaciando la carpeta temporal de AWS
    for n in os.listdir(path_input):
    	if n.endswith(".nc"):
            os.remove(path_input + n)