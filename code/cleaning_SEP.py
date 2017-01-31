#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import json
import requests
import psycopg2
import jellyfish as jl


#conecta a una base de datos, regresa el cursor
def connect_database(dbname,u,p):
    #cleaning SEP files to integreate to Directory
    con=None
    try:
        con=psycopg2.connect(database=dbname, user=u, password=u)
       # cur = con.cursor()
        #cur.execute('SELECT nombre,primer_apellido,segundo_apellido from directorio limit 5;')          
        return con    
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e    
        sys.exit(1)
    return 0
    
#consulta la tabla de directorio y llama al scraping de SEP            
def SEP_download(con):
    cursor=con.cursor()
    cursor.execute('SELECT id,nombre,primer_apellido,segundo_apellido from directorio where id>117001')
    rows=cursor.fetchall()
    c=0
    for row in rows:
        
        print row[0],row[1],row[2]
        escuela_json=scrap_name(str(row[1]),str(row[2]),str(row[3]))
        #r0=[row[1].upper().decode(encoding='UTF-8',errors='strict'),row[2].upper().decode(encoding='UTF-8',errors='strict'),row[3].upper().decode(encoding='UTF-8',errors='strict')]
        
        try:
            a= json.loads(escuela_json)
            c=c+1
            if 'docs' in  a and len(a["docs"])>0:
                for item in a["docs"]:
                    r=[]                
                    r1=[item['nombre'].upper().decode(encoding='UTF-8',errors='strict'),item['paterno'].upper().decode(encoding='UTF-8',errors='strict'),item['materno'].upper().decode(encoding='UTF-8',errors='strict')]
                    print len(item)
                    if 'numCedula' in item.keys() and 'titulo' in item.keys() and 'institucion'  in item.keys() and 'anioRegistro' in item.keys() and 'score' in item.keys():
                        print item['numCedula'],item['titulo'],item['institucion'],item['anioRegistro'],item['score']
                        query="INSERT INTO  SEP VALUES ('"+str(row[0])+"','"+str(item['numCedula'])+"','"+str(item['titulo'])+"','"+str(item['institucion'].replace("'", ""))+"','"+str(item['anioRegistro'])+"','"+str(item['score'])+"');"
                        print query#print valida_data(r0,r1)
                        cursor.execute(query)
                        #unicode(row['PrimerApellido'],'utf8')
                        ##s=str(item[key])
                        #r.append(s.encode('utf8'))

                        #comparar los nombres, orden 
                    #print r                
            if c==1000:
                con.commit()
                c=0
        except ValueError:  # includes simplejson.decoder.JSONDecodeError
            print 'Decoding JSON has failed'
            pass
    con.commit()
             
#scraping SEP, devuelve un json
def valida_data(datos1,datos2):
    #convierte a UTF-8
    if jl.jaro_winkler(datos1[0],datos2[0])>0.60 and jl.jaro_winkler(datos1[1],datos2[1])>0.97 and jl.jaro_winkler(datos1[2],datos2[2])>0.97:
        return True
    else:
        return False
    #Comprar nombres y orden
    
    
def scrap_name(primerNombre,PrimerApellido, SegundoApellido):
    url = "http://search.sep.gob.mx/solr/cedulasCore/select?fl=%2A%2Cscore&q=" + primerNombre +  "+" + PrimerApellido + "+" + SegundoApellido + "&start=0&rows=1&facet=true&indent=on&wt=json"
    #print url
    try:
        r = requests.get(url)	
        js = requests.get(url).json()
        
        if "response" not in js:
            jj="[]"
        else:    
            jj=json.dumps(js["response"],encoding="utf-8")
    
        return jj        
    except requests.exceptions.ConnectionError as e:
        print "no se pudo conectar he"
        pass

    
def start():
    database="dir"
    user="postgres"
    password="postgres"
    con=connect_database(database,user,password)
    
    SEP_download(con)
    

start()













