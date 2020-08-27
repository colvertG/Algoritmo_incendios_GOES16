#!/usr/bin/env python3
# coding: utf-8
# # Analisis de los datos del canal 07 del dia 09/05/2019
# Script creado en el dia 15/ago/2019

import pandas as pd
import os, glob
import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline


def reduccion_hora_c07(df_entrada, nom_col, evnt_id):
    df_entrada = df_entrada[df_entrada.evnt_id == evnt_id].copy()
    
    df_salida_mean = pd.DataFrame(df_entrada[nom_col].resample('1h').mean())
    df_salida_mean.rename(columns={nom_col:'mean_{}'.format(nom_col)}, inplace=True)
    
    df_salida_max = pd.DataFrame(df_entrada[nom_col].resample('1h').max())
    df_salida_max.rename(columns={nom_col:'max_{}'.format(nom_col)}, inplace=True)
    
    df_salida_min = pd.DataFrame(df_entrada[nom_col].resample('1h').min())
    df_salida_min.rename(columns={nom_col:'min_{}'.format(nom_col)}, inplace=True)
    
    df_salida_std = pd.DataFrame(df_entrada[nom_col].resample('1h').std())
    df_salida_std.rename(columns={nom_col:'std_{}'.format(nom_col)}, inplace=True)
    
    df_salida_1h = df_salida_min.merge(df_salida_mean, on=df_entrada.index.name).merge(df_salida_max, on=df_entrada.index.name).merge(df_salida_std, on=df_entrada.index.name)
    
    df_salida_1h["evnt_id"] = evnt_id
    
    df_salida_1h["umbral"] = df_salida_1h.max_ch7 - df_salida_1h.std_ch7
    
    del(df_salida_mean, df_salida_max, df_salida_min, df_salida_std)
    return df_salida_1h

def reduccion_hora_dif(df_entrada, nom_col, evnt_id):
    df_entrada = df_entrada[df_entrada.evnt_id == evnt_id].copy()
    
    df_salida_mean = pd.DataFrame(df_entrada[nom_col].resample('1h').mean())
    df_salida_mean.rename(columns={nom_col:'mean_{}'.format(nom_col)}, inplace=True)
    
    df_salida_max = pd.DataFrame(df_entrada[nom_col].resample('1h').max())
    df_salida_max.rename(columns={nom_col:'max_{}'.format(nom_col)}, inplace=True)
    
    df_salida_min = pd.DataFrame(df_entrada[nom_col].resample('1h').min())
    df_salida_min.rename(columns={nom_col:'min_{}'.format(nom_col)}, inplace=True)
    
    df_salida_std = pd.DataFrame(df_entrada[nom_col].resample('1h').std())
    df_salida_std.rename(columns={nom_col:'std_{}'.format(nom_col)}, inplace=True)
    
    df_salida_1h = df_salida_min.merge(df_salida_mean, on=df_entrada.index.name).merge(df_salida_max, on=df_entrada.index.name).merge(df_salida_std, on=df_entrada.index.name)
    
    df_salida_1h["evnt_id"] = evnt_id
    
    df_salida_1h["umbral"] = df_salida_1h.mean_dif7_14
    
    del(df_salida_mean, df_salida_max, df_salida_min, df_salida_std)
    return df_salida_1h


    
def crea_umbrales_c07(path_muestras_goes_viirs, path_umbrales, año_dia):
    
    csv_referencia = os.path.join(path_muestras_goes_viirs, "valores_muestreados_ch07_{}.csv".format(año_dia)) # archivo echo desde ejercicio05
 
    lista_csv_ref = glob.glob(csv_referencia)
      
    if len(lista_csv_ref) == 0:
        print("sin datos")
        exit(0)
    
    if len(lista_csv_ref) > 1:
        print("muchos datos")
        exit(0)
    
    if len(lista_csv_ref) == 1:
        print("empeza a correr")
    
    df = pd.read_csv(lista_csv_ref[0])
    df["fecha"] = pd.to_datetime(df.fecha, format='%Y%j%H%M')
    df.set_index(df.fecha, drop=True, inplace=True)
    df.drop(columns="fecha", inplace=True)
    
    lista_eventos = list(df.evnt_id.unique())
    
    # ev_4063_1h = reduccion_hora(df, "ch7", 4063)
    df0 = reduccion_hora_c07(df, "ch7", lista_eventos[0])
    
    for i in range(len(lista_eventos)):
        df2 = reduccion_hora_c07(df, "ch7", lista_eventos[i])
        if i == 0:
            df_salida = df0
        else:
            df_salida = pd.concat([df_salida, df2])
        del(df2)
    del(df0)
    
    grp = df_salida.groupby("fecha")
    
    df_umbral_24h = grp.umbral.describe()
    
    # BORRAR ESTO PORQUE ES PARA 24 CAMBIAMOS 17
    x = pd.date_range('00:00', periods=(24), freq='1h')
    
    # convert para hora en float
    x = np.round(((x.strftime("%H")).astype(int))+ ((x.strftime("%M")).astype(int)/60), 2)
    y = np.array(df_umbral_24h["mean"])
    
    pred_interp = InterpolatedUnivariateSpline(x,y, k=2)
    
    xi = pd.date_range('00:00', periods=(6*24), freq='10min')
    xi = np.round(((xi.strftime("%H")).astype(int))+ ((xi.strftime("%M")).astype(int)/60.0), 2)
    yi = np.round(pred_interp(xi), 2)
    
    errores = 0
    for n in yi:
        if np.isnan(n) == True:
            errores += 1
        
    if errores == 0:
        result = pd.DataFrame(yi, xi)
        result.reset_index(inplace=True)
        result.columns = ["h", "pred"]
        result["fecha"]= ( pd.date_range('00:00', periods=(6*24), freq='10min'))
        result[["h", "pred"]].to_csv(os.path.join(path_umbrales, "umbral_ch07_{}.csv".format(año_dia)),index=False)
    
    print("fin del proceso!")

def crea_umbrales_dif07_14(path_muestras_goes_viirs, path_umbrales, año_dia):
    
    csv_referencia = os.path.join(path_muestras_goes_viirs, "valores_muestreados_dif7_14_{}.csv".format(año_dia)) 
    
    df = pd.read_csv(csv_referencia, names=["evnt_id", "dif7_14", "fecha"], skiprows=1)
    df["fecha"] = pd.to_datetime(df.fecha, format='%Y%j%H%M')
    df.set_index(df.fecha, drop=True, inplace=True)
    df.drop(columns="fecha", inplace=True)
    
    lista_eventos = list(df.evnt_id.unique())
    
    # ev_4063_1h = reduccion_hora(df, "ch7", 4063)
    df0 = reduccion_hora_dif(df, "dif7_14", lista_eventos[0])
    
    for i in range(len(lista_eventos)):
        df2 = reduccion_hora_dif(df, "dif7_14", lista_eventos[i])
        if i == 0:
            df_salida = df0
        else:
            df_salida = pd.concat([df_salida, df2])
        del(df2)
    del(df0)
    
    grp = df_salida.groupby("fecha")
    
    df_umbral_24h = grp.umbral.describe()
    
    # TEMPORAL CAMBIAR A 24 PROBAMOS CON 17
    x = pd.date_range('00:00', periods=(24), freq='1h')
    # convert para hora en float
    x = np.round(((x.strftime("%H")).astype(int))+ ((x.strftime("%M")).astype(int)/60), 2)
    y = np.array(df_umbral_24h["mean"])
    
    pred_interp = InterpolatedUnivariateSpline(x,y, k=2)
    
    xi = pd.date_range('00:00', periods=(6*24), freq='10min')
    xi = np.round(((xi.strftime("%H")).astype(int))+ ((xi.strftime("%M")).astype(int)/60.0), 2)
    yi = np.round(pred_interp(xi), 2)
    
    errores = 0
    for n in yi:
        if np.isnan(n) == True:
            errores += 1
        
    if errores == 0:
        result = pd.DataFrame(yi, xi)
        result.reset_index(inplace=True)
        result.columns = ["h", "pred"]
        result["fecha"]= ( pd.date_range('00:00', periods=(6*24), freq='10min'))
        result[["h", "pred"]].to_csv(path_umbrales + "umbral_dif7_14_{}.csv".format(año_dia),index=False)
    
    print("fin del proceso!")
