#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 14:37:04 2020

@author: liliamd
"""
import csv
import os 

def umbral_10dias_max(fecha_dtobj, path_umbrales):
    hora_dec = str(round((fecha_dtobj.hour + fecha_dtobj.minute/60),2))
    print (hora_dec)
    
    archivos_umbrales_c07 = []
    archivos_umbrales_dif = []
    
    
    for n in os.listdir(path_umbrales):
        if "ch07" in n:
            archivos_umbrales_c07.append(n)
        if "dif" in n:
            archivos_umbrales_dif.append(n)
            
    archivos_umbrales_c07.sort()
    archivos_umbrales_dif.sort()
    
    archivos_umbrales_c07 = archivos_umbrales_c07[-10:]
    archivos_umbrales_dif = archivos_umbrales_dif[-10:]
    print (archivos_umbrales_c07)
    print (archivos_umbrales_dif)
    
    umbrales_c07 = {}
    umbrales_dif = {}
    
    with open(path_umbrales+n, 'r') as csvFile:
        reader = csv.reader(csvFile)
        for row in reader:
            umbrales_c07[row[0]] = []
            umbrales_dif[row[0]] = []
    
    for n in archivos_umbrales_c07:
        with open(path_umbrales+n, 'r') as csvFile:
            reader = csv.reader(csvFile)
            for row in reader:
                
                umbrales_c07[row[0]].append(row[1])
                
    for n in archivos_umbrales_dif:
        with open(path_umbrales+n, 'r') as csvFile:
            reader = csv.reader(csvFile)
            
            for row in reader:
                
                umbrales_dif[row[0]].append(row[1])
                
    umbrales_c07 = [float(i) for i in umbrales_c07[hora_dec]]
    umbrales_dif = [float(i) for i in umbrales_dif[hora_dec]]
    
    
    u07 = max(umbrales_c07)
    udif = max(umbrales_dif)
    print ("umbral  7: ",u07)
    print ("umbral dif: ",udif)
    return u07, udif
    