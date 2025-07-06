#!/usr/bin/python3
"""
 cuckoo2csv
 Exporta los resultados de analisis Cuckoo a fichero CSV.

"""
import json
import glob
import csv
import sys
import os
import argparse

def getDatos(file):
    """    
    Parameters
    ----------
    file : fichero "analysys.json" de Cuckoo

    Returns
    -------
    v : diccionario con los valores encontrados

    """
    
    data = json.load(file)
    # Creamos diccionario vacío. Según el caso, solo se rellanarán algunos valores.
    v = {'id':'','fecha':'','fnamesubmitted':'','fnameanalysis':'','type':'','scorecuckoo':''
         ,'scoretotal':'','families':'','tags':'','virustotal':''}
    
    v['id'] = data['id']        
    v['fecha'] = data["created_on"]["__isodt__"]         
    
    # Analisis finalizados con éxito
    if  data['state'] == 'finished':
        # Obtener nombre de fichero submitido / analizado y su tipo        
        if data['category'] == 'file':
            v['fnamesubmitted'] = data['submitted']['filename']
            v['fnameanalysis'] = data["target"]['filename']
            v['type'] = data['target']['media_type']
        else: #url
            v['fnamesubmitted'] = data['submitted']['url']
            v['type'] = 'url'
            
        # Puntuacion en el analisis dinamico
        v['scorecuckoo'] = data['tasks'][0]['score']
        # Puntuacion total (se tiene en cuenta los resultados de VirusTotal)
        v['scoretotal'] = data['score']
        v['families'] = ','.join(data['families'])
        v['tags'] = ','.join(data['tags'])
        # Comprobar si la muestra se ha encontrado en virustotal. Esto se obtiene del archivo pre.json
        try:
            with open(f.replace('analysis.json', 'pre.json'), 'r') as file:
                datapre = json.load(file)
                if 'virustotal' in datapre and len(datapre['virustotal']) > 0:
                    v['virustotal'] = 'Y'
                else:
                    v['virustotal'] = 'N'
        except:
            pass
    # Si hubo un error durante el analisis        
    if data['state'] == 'fatal_error':
        v['fnamesubmitted'] = data['submitted']['filename']            
        if data['category'] == 'file':            
            v['fnamesubmitted'] = data['submitted']['filename']                
        else:
            v['fnamesubmitted'] = data['submitted']['url']                
        v['fnameanalysis'] = data['errors']['fatal'][0]['error']
    
    return v


if __name__ == "__main__":
    # fichero de salida por defecto
    fsalida = 'cuckooreport-out.csv'
    
    # Manejo de parámetros.  Se permite -h (ayuda, por defecto), -o (fichero de salida)
    # y -p (directorio de analisis)
    parser = argparse.ArgumentParser(
                    prog=os.path.basename(__file__),
                    description='Extrae a un fichero CSV los resultados de análisis de Cuckoo3')
    parser.add_argument("-o", "--out", type=str,
                        help="Fichero de salida. Por defecto cuckooreport-out.csv")
    parser.add_argument("-p", "--path", type=str, 
                        help="Directorio con los resultados de análisis. \
                        Si se omite directorio actual")   
    args = parser.parse_args()

    if args.out:   
        fsalida = args.out
    
    # Directorio con los analisis. Por defecto, el actual
    path =  os.getcwd().replace('\\', '/') + '/'

    if args.path:   
        path = args.path + '/'
        
    if fsalida == os.path.basename(__file__):
        print('Fichero de salida incorrecto: ', fsalida)
        exit()
    
    print('Directorio de analisis:', path)
    
    # Obtener todos los archivos "analysis.json" en el directorio
    files = glob.glob(path + '**/analysis.json', recursive=True)    
        
    if len(files) == 0:
        print('No se encontraron ficheros de análisis')
        sys.exit()
        
    datos= [] # lista que contiene todos los analisis extraidos
    
    for f in files:
        with open(f, 'r') as file:
            datos.append(getDatos(file))
    
    # Obtenemos cabeceras a partir del primer elemento de la lista
    fieldnames = datos[0].keys()
    
    # Escribir fichero CSV
    with open(fsalida, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=';'
                                , quoting=csv.QUOTE_NONNUMERIC, quotechar = '"')
        writer.writeheader()  
        writer.writerows(datos)  

    print('Creado fichero:', fsalida)
    print('Exportados',  len(files), 'analisis')