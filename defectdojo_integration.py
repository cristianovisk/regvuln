import requests
import configparser
import json
import binascii
import os
import os.path
import time
import urllib3
import environment
from error import handlingError
import coloredlogs, logging
from mgn_database import insertProdType
from mgn_database import insertNewProd
from mgn_database import checkIDProduct
from mgn_database import checkIDProductType
from mgn_database import checkIDEngagement
from mgn_database import checkIDEndpoint
from mgn_database import insertNewEngagement
from mgn_database import insertNewEndpoint
from mgn_database import updateTagIfUploadedScanDefectDojo
from mgn_database import checkIfUploadedScanDefectDojo
from datetime import date
from datetime import datetime

config = configparser.ConfigParser()
config.sections()
config.read('.config.ini')

def uploadToDefectDojo(filename, eng_name, scan_type, sha256, is_new_import, IDEndpoint):
    multipart_form_data = {
        'file': (filename, open(filename, 'rb')),
        'scan_type': (None, scan_type),
        'product_name': (None, environment.var_env_global['RG_DEFECTDOJO_PRODUCT_NAME']),
        'engagement_name': (None, eng_name),
        'tags': (None, sha256),
        'endpoint_to_add': (None, IDEndpoint),
        'environment': (None, environment.var_env_global['RG_DEFECTDOJO_ENV']),
        # optional, used for `import-scan`
        'product_type_name': (None, environment.var_env_global['RG_DEFECTDOJO_PRODUCT_TYPE']),

        # optional, used for `reimport-scan`
        'test_title': (None, eng_name),
    }
    uri = '/api/v2/import-scan/'
    # uri = '/api/v2/import-scan/' if is_new_import == True else '/api/v2/reimport-scan/'
    if is_new_import == True:
        uri = '/api/v2/import-scan/'
    elif is_new_import == False:
        uri = '/api/v2/reimport-scan/'
    defect_dojo_domain = environment.var_env_global['RG_DEFECTDOJO_URL']
    if uri == '/api/v2/import-scan/':
        logging.info("DEFECT_DOJO - Importando relatorio %s" %(filename))
    if uri == '/api/v2/reimport-scan/':
        logging.info("DEFECT_DOJO - Re-importando relatorio %s" %(filename))
    response = requests.post(
        defect_dojo_domain + uri,
        files=multipart_form_data,
        headers={
            'Authorization': 'Token %s' %environment.var_env_global['RG_DEFECTDOJO_API_KEY'],
        }
    )
    
    # Debug Only
    handlingError(response.content, response.status_code)
def request_api(uri, method, body, content_type=None):
    config = configparser.ConfigParser()
    config.sections()
    config.read('.config.ini')
    if method == 'GET':
        url = '%s/api/v2/%s' %(environment.var_env_global['RG_DEFECTDOJO_URL'],uri)
        headers = {'content-type': 'application/json',
                'Authorization': 'Token %s' %(environment.var_env_global['RG_DEFECTDOJO_API_KEY'])}
        r = requests.get(url, headers=headers, verify=True) # set verify to False if ssl cert is self-signed
        # Debug Only
        handlingError(r.content, r.status_code)
        result = r.json()
        return result
    elif method == 'POST':
        url = '%s/api/v2/%s' %(environment.var_env_global['RG_DEFECTDOJO_URL'],uri)
        headers = {'content-type': 'application/json',
                'Authorization': 'Token %s' %(environment.var_env_global['RG_DEFECTDOJO_API_KEY'])}
        r = requests.post(url, headers=headers, data = body, verify=True) # set verify to False if ssl cert is self-signed
        handlingError(r.content, r.status_code)
        result = r.json()
        return result

def gen_product_type(name, description):
    data_product = {}
    data_product['name'] = name
    data_product['description'] = description
    data_product['critical_product'] = True
    data_product['key_product'] = True
    json_product = json.dumps(data_product, indent = 3)
    result = request_api("product_types/", "POST", json_product)
    if result['name'][0] == "product_ type with this name already exists.":
        logging.info('REGVULN - Tipo de Produto ja existente (%s).' %name)
    else:
        insertProdType(result['id'], result['name'])

def gen_new_product(name, description, prod_type):
    data_product = {}
    data_product['name'] = name
    data_product['description'] = description
    data_product['prod_type'] = prod_type

    json_product = json.dumps(data_product, indent = 3)

    result = request_api("products/", "POST", json_product)
    if result['name'][0] == "product with this name already exists.":
        logging.info('REGVULN - Produto ja existente. (%s)' %name)
    else:
        insertNewProd(result['id'], result['name'])

def gen_new_engagement(sha256, name, reg_name, idprod):
    flag = False
    data_eng = {}
    data_eng['tags'] = [ 'container', '%s' %(reg_name) ]
    data_eng['name'] = name
    data_eng['description'] = name
    data_eng['product'] = idprod
    data_eng['target_start'] = str(date.today())
    data_eng['target_end'] = str(date.today())
    data_eng['engagement_type'] = 'CI/CD'
    data_eng['commit_hash'] = sha256
    data_eng['deduplication_on_engagement'] = True
    data_eng['status'] = "Completed"

    json_eng = json.dumps(data_eng, indent = 3)
    check_exist = request_api('engagements/', "GET", json_eng)
    for num in range(0,len(check_exist['results'])):
        if check_exist['results'][num]['name'] == name:
            flag = True

    if flag != True:
        logging.warning("REGVULN - Nao encontrado Engagement, cadastrando. (%s)" %name)
        eng_req = request_api('engagements/', "POST", json_eng)
        insertNewEngagement(eng_req['id'], eng_req['name'])

def gen_new_endpoint(idprod):
    data_end = {}
    data_end['host'] = environment.var_env_global['RG_REGISTRY_DNS'].split(":", 1)[0]
    data_end['protocol'] = environment.var_env_global['RG_REGISTRY_URL'].split(":", 1)[0]
    try:
        data_end['port'] = environment.var_env_global['RG_REGISTRY_DNS'].split(":", 1)[1]
    except:
        if data_end['protocol'] == 'http':
            data_end['port'] = 80
        elif data_end['protocol'] == 'https':
            data_end['port'] = 443

    data_end['product'] = idprod

    json_end = json.dumps(data_end, indent = 3)
    check_exist = request_api('endpoints/', 'POST', json_end)
    try:
        if check_exist['non_field_errors'][0] == 'It appears as though an endpoint with this data already exists for this product.':
            logging.info('REGVULN - Endpoint ja existe. (%s)' %data_end['host'])
    except:
        insertNewEndpoint(check_exist['id'],check_exist['product'],check_exist['host'],check_exist['protocol'],check_exist['port'])

def sendReportDefectDojo(image, tag, name, reg_name, uploadFlagDojo, json_file, sha256, flag):
    if environment.var_env_global['RG_DEFECTDOJO_ENABLED'] == 'true' or environment.var_env_global['RG_DEFECTDOJO_ENABLED'] == 'True':
        if flag == 1:
            populate_database_defectdojo()
            gen_product_type(environment.var_env_global['RG_DEFECTDOJO_PRODUCT_TYPE'], "Analisado automaticamente via API")
            gen_new_product(environment.var_env_global['RG_DEFECTDOJO_PRODUCT_NAME'], "Analisado automaticamente via API", checkIDProductType(environment.var_env_global['RG_DEFECTDOJO_PRODUCT_TYPE']))
            gen_new_endpoint(checkIDProduct(environment.var_env_global['RG_DEFECTDOJO_PRODUCT_NAME']))
        gen_new_engagement(sha256.split(":", 1)[1], "%s:%s" %(image,tag), reg_name, checkIDProduct(environment.var_env_global['RG_DEFECTDOJO_PRODUCT_NAME']))
        IDEndpoint = checkIDEndpoint(environment.var_env_global['RG_REGISTRY_DNS'].split(":", 1)[0],environment.var_env_global['RG_REGISTRY_URL'].split(":", 1)[0],int(environment.var_env_global['RG_REGISTRY_DNS'].split(":", 1)[1]),checkIDProduct(environment.var_env_global['RG_DEFECTDOJO_PRODUCT_NAME']))
        uploadToDefectDojo(json_file, "%s:%s" %(image,tag), 'Trivy Scan', sha256.split(":", 1)[1],uploadFlagDojo, IDEndpoint)
        updateTagIfUploadedScanDefectDojo(image,tag,sha256)
    elif environment.var_env_global['RG_DEFECTDOJO_ENABLED'] == 'false' or environment.var_env_global['RG_DEFECTDOJO_ENABLED'] == 'False':
        logging.debug('Envio DefectDojo desabilitado')
        return False

def populate_database_defectdojo():
    id = int
    rPT = request_api('product_types/', 'GET', '')
    for num in range(0,rPT['count']):
        try:
            id = checkIDProductType(rPT['results'][num]['name'])
            logging.debug('REGVULN - Tipo Produto de ID %i ja adicionado em banco' %id)
        except:
            insertProdType(rPT['results'][num]['id'],rPT['results'][num]['name'])
            logging.debug('REGVULN - Tipo Produto de ID %i adicionado em banco' %rPT['results'][num]['id'])

    rP = request_api('products/', 'GET', '')
    for num in range(0,rP['count']):
        try:
            id = checkIDProduct(rP['results'][num]['name'])
            logging.debug('REGVULN - Produto de ID %i ja adicionado em banco' %id)
        except:
            insertNewProd(rP['results'][num]['id'],rP['results'][num]['name'])
            logging.debug('REGVULN - Produto de ID %i adicionado em banco' %rP['results'][num]['id'])

    rEG = request_api('engagements/', 'GET', '')
    for num in range(0,rEG['count']):
        try:
            id = checkIDEngagement(rEG['results'][num]['name'])
            logging.debug('REGVULN - Engagement de ID %i ja adicionado em banco' %id)
        except:
            insertNewEngagement(rEG['results'][num]['id'],rEG['results'][num]['name'])
            logging.debug('REGVULN - Engagement de ID %i adicionado em banco' %rEG['results'][num]['id'])
    
    rED = request_api('endpoints/', 'GET', '')
    for num in range(0,rED['count']):
        try:
            id = checkIDEndpoint(rED['results'][num]['host'],rED['results'][num]['protocol'],rED['results'][num]['port'],rED['results'][num]['product'])
            logging.debug('REGVULN - Endpoint de ID %i ja adicionado em banco' %id)
        except:
            insertNewEndpoint(rED['results'][num]['id'],rED['results'][num]['product'],rED['results'][num]['host'],rED['results'][num]['protocol'],rED['results'][num]['port'])
            logging.debug('REGVULN - Endpoint de ID %i adicionado em banco' %rED['results'][num]['id'])
