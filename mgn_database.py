import time
import sqlite3
import environment
import os
from datetime import datetime

def createDB():
    try:
        os.mkdir(environment.var_env_global['RG_REPORT_OUTPUT_FOLDER'])
    except:
        pass
    conn = sqlite3.connect('%s/registry.db' %environment.var_env_global['RG_REPORT_OUTPUT_FOLDER'])
    
    # definindo um cursor
    cursor = conn.cursor()

    # criando a tabela (schema)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            tag TEXT NOT NULL,
            size INTEGER NOT NULL,
            timestamp INTEGER NOT NULL,
            sha256 TEXT NOT NULL,
            json BLOB,
            defect_uploaded TEXT
    );
    """)
    conn.commit()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hash_json_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            hash TEXT NOT NULL
    );
    """)
    conn.commit()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS defect_prod_type (
            id INTEGER NOT NULL,
            name TEXT NOT NULL
    );
    """)
    conn.commit()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS defect_product (
            id INTEGER NOT NULL,
            name TEXT NOT NULL
    );
    """)
    conn.commit()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS defect_engagement (
            id INTEGER NOT NULL,
            name TEXT NOT NULL
    );
    """)
    conn.commit()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS defect_endpoint (
            id INTEGER NOT NULL,
            name TEXT NOT NULL,
            protocol TEXT NOT NULL,
            port INTEGER NOT NULL,
            prod_id INTEGER NOT NULL
    );
    """)
    conn.commit()
    conn.close()

def insertNewHashFileToCompare(filename, hashfile):
    conn = sqlite3.connect('%s/registry.db' %environment.var_env_global['RG_REPORT_OUTPUT_FOLDER'])
    # definindo um cursor
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO hash_json_files (filename, hash) VALUES ('%s', '%s')""" %(filename,hashfile))
    query = cursor.fetchall()
    conn.commit()
    conn.close()

def checkHashFileToCompare(filename,hashfile):
    result = []
    conn = sqlite3.connect('%s/registry.db' %environment.var_env_global['RG_REPORT_OUTPUT_FOLDER'])
    # definindo um cursor
    cursor = conn.cursor()
    cursor.execute("""SELECT hash FROM hash_json_files WHERE filename = '%s' AND hash = '%s'""" %(filename,hashfile))
    query = cursor.fetchall()
    try:
        result = query[0][0]
    except:
        result = 0
    conn.commit()
    conn.close()
    return result

def insertProdType(idprod, name):
    conn = sqlite3.connect('%s/registry.db' %environment.var_env_global['RG_REPORT_OUTPUT_FOLDER'])
    # definindo um cursor
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO defect_prod_type (id, name) VALUES (%s, '%s')""" %(idprod,name))
    query = cursor.fetchall()
    conn.commit()
    conn.close()

def insertNewProd(idprod, name):
    conn = sqlite3.connect('%s/registry.db' %environment.var_env_global['RG_REPORT_OUTPUT_FOLDER'])
    # definindo um cursor
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO defect_product (id, name) VALUES (%s, '%s')""" %(idprod,name))
    query = cursor.fetchall()
    conn.commit()
    conn.close()

def insertNewEngagement(idprod, name):
    conn = sqlite3.connect('%s/registry.db' %environment.var_env_global['RG_REPORT_OUTPUT_FOLDER'])
    # definindo um cursor
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO defect_engagement (id, name) VALUES (%s, '%s')""" %(idprod,name))
    query = cursor.fetchall()
    conn.commit()
    conn.close()

def insertNewEndpoint(idend, prod_id, host, protocol, port):
    conn = sqlite3.connect('%s/registry.db' %environment.var_env_global['RG_REPORT_OUTPUT_FOLDER'])
    # definindo um cursor
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO defect_endpoint (id, name, protocol, port, prod_id) VALUES (%s, '%s', '%s', %i, %i)""" %(idend,host,protocol,port,prod_id))
    query = cursor.fetchall()
    conn.commit()
    conn.close()

def checkIDProductType(name):
    result = []
    conn = sqlite3.connect('%s/registry.db' %environment.var_env_global['RG_REPORT_OUTPUT_FOLDER'])
    # definindo um cursor
    cursor = conn.cursor()
    cursor.execute("""SELECT id FROM defect_prod_type WHERE name = '%s'""" %(name))
    query = cursor.fetchall()
    result = query[0][0]
    conn.commit()
    conn.close()
    return result

def checkIDProduct(name):
    result = []
    conn = sqlite3.connect('%s/registry.db' %environment.var_env_global['RG_REPORT_OUTPUT_FOLDER'])
    # definindo um cursor
    cursor = conn.cursor()
    cursor.execute("""SELECT id FROM defect_product WHERE name = '%s'""" %(name))
    query = cursor.fetchall()
    result = query[0][0]
    conn.commit()
    conn.close()
    return result

def checkIfUploadedScanDefectDojo(name, tag, sha256):
    result = []
    conn = sqlite3.connect('%s/registry.db' %environment.var_env_global['RG_REPORT_OUTPUT_FOLDER'])
    # definindo um cursor
    cursor = conn.cursor()
    cursor.execute("""SELECT defect_uploaded FROM images WHERE name = '%s' AND tag = '%s' AND sha256 = '%s'""" %(name, tag, sha256))
    query = cursor.fetchall()
    result = query[0][0]
    conn.commit()
    conn.close()
    return result

def updateTagIfUploadedScanDefectDojo(name,tag,sha256):
    conn = sqlite3.connect('%s/registry.db' %environment.var_env_global['RG_REPORT_OUTPUT_FOLDER'])
    # definindo um cursor
    cursor = conn.cursor()
    cursor.execute("""UPDATE images SET defect_uploaded = '%s' WHERE name = '%s' AND tag = '%s' AND sha256 = '%s'""" %("False",name,tag,sha256))
    query = cursor.fetchall()
    # print(name,tag,sha256,query)
    if len(query) == 1:
        return True
    conn.commit()
    conn.close()

def checkIDEngagement(name):
    result = []
    conn = sqlite3.connect('%s/registry.db' %environment.var_env_global['RG_REPORT_OUTPUT_FOLDER'])
    # definindo um cursor
    cursor = conn.cursor()
    cursor.execute("""SELECT id FROM defect_engagement WHERE name = '%s'""" %(name))
    query = cursor.fetchall()
    result = query[0][0]
    conn.commit()
    conn.close()
    return result

def checkIDEndpoint(host,protocol,port,prod_id):
    time.sleep(2)
    result = []
    conn = sqlite3.connect('%s/registry.db' %environment.var_env_global['RG_REPORT_OUTPUT_FOLDER'])
    # definindo um cursor
    cursor = conn.cursor()
    cursor.execute("""SELECT id FROM defect_endpoint WHERE name = '%s' AND protocol = '%s' AND port = %i AND prod_id = %i""" %(host,protocol,int(port),int(prod_id)))
    query = cursor.fetchall()
    result = query[0][0]
    conn.commit()
    conn.close()
    return result

def returnAllHashs():
    result = []
    conn = sqlite3.connect('%s/registry.db' %environment.var_env_global['RG_REPORT_OUTPUT_FOLDER'])
    # definindo um cursor
    cursor = conn.cursor()
    cursor.execute("""SELECT DISTINCT REPLACE(sha256,"sha256:","") as HASH FROM images""")
    query = cursor.fetchall()
    conn.commit()
    conn.close()
    for res in query:
        result.append(res[0])
    return result

def checkIfImageExist(name,tag,sha256):
    conn = sqlite3.connect('%s/registry.db' %environment.var_env_global['RG_REPORT_OUTPUT_FOLDER'])
    # definindo um cursor
    cursor = conn.cursor()
    cursor.execute("""SELECT name, tag, sha256 FROM images WHERE name = '%s' AND tag = '%s' AND sha256 = '%s'""" %(name,tag,sha256))
    query = cursor.fetchall()
    conn.commit()
    conn.close()
    if len(query) == 1:
        if query[0][0] == name and query[0][1] == tag and query[0][2] == sha256:
            return True
        else:
            return False
    else:
        return False

def checkIfImageNeedScan(name,tag,limit,sha256):
    conn = sqlite3.connect('%s/registry.db' %environment.var_env_global['RG_REPORT_OUTPUT_FOLDER'])
    # definindo um cursor
    cursor = conn.cursor()
    cursor.execute("""SELECT timestamp FROM images WHERE name = '%s' AND tag = '%s' AND sha256 = '%s'""" %(name,tag,sha256))
    query = cursor.fetchall()
    past_time = int(datetime.timestamp(datetime.now())) - query[0][0]
    if len(query) == 1 and past_time >= limit:
        return True
    else:
        return False

    conn.commit()
    conn.close()

def updateTimestampImage(name,tag,sha256):
    conn = sqlite3.connect('%s/registry.db' %environment.var_env_global['RG_REPORT_OUTPUT_FOLDER'])
    # definindo um cursor
    cursor = conn.cursor()
    cursor.execute("""UPDATE images SET timestamp = '%i' WHERE name = '%s' AND tag = '%s' AND sha256 = '%s'""" %(int(datetime.timestamp(datetime.now())),name,tag,sha256))
    query = cursor.fetchall()
    if len(query) == 1:
        return True
    conn.commit()
    conn.close()

def updateJsonScan(name,tag,sha256,json_bin):
    conn = sqlite3.connect('%s/registry.db' %environment.var_env_global['RG_REPORT_OUTPUT_FOLDER'])
    # definindo um cursor
    cursor = conn.cursor()
    insertBlob = """UPDATE images SET json = ? WHERE name = ? AND tag = ? AND sha256 = ?"""
    #cursor.execute("""UPDATE images SET json = '%i' WHERE name = '%s' AND tag = '%s' AND sha256 = '%s'""" %(int(datetime.timestamp(datetime.now())),name,tag,sha256))
    tuple_insert = (json_bin, name, tag, sha256)
    cursor.execute(insertBlob, tuple_insert)
    query = cursor.fetchall()
    if len(query) == 1:
        return True
    conn.commit()
    conn.close()

def insertImage(imgname, imgtag, size, timestamp, hash):
    conn = sqlite3.connect('%s/registry.db' %environment.var_env_global['RG_REPORT_OUTPUT_FOLDER'])
    # definindo um cursor
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO images (name, tag, size, timestamp, sha256, defect_uploaded) VALUES ('%s', '%s', '%i', '%i', '%s', 'True')""" %(imgname, imgtag, size, timestamp, hash))
    #cursor.execute("""INSERT INTO images (name, tag, layers) VALUES ('teste', 'teste', 'teste')""")
    conn.commit()
    conn.close()

def removeImage(hash):
    conn = sqlite3.connect('%s/registry.db' %environment.var_env_global['RG_REPORT_OUTPUT_FOLDER'])
    # definindo um cursor
    cursor = conn.cursor()
    cursor.execute("""DELETE FROM images WHERE sha256 = '%s'""" %(hash))
    conn.commit()
    conn.close()

createDB()
