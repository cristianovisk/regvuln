#!/usr/bin/env python3
import json
import os, sys, stat
import base64
import os.path
import requests
import configparser
import coloredlogs, logging
import shutil
import time
import hashlib
import docker
import pwd
import environment
from operator import eq
from datetime import datetime
from time import sleep
from art import tprint
from error import handlingError
from sheet2dict import Worksheet
from mgn_database import createDB
from mgn_database import insertImage
from mgn_database import checkIfImageExist
from mgn_database import checkIfImageNeedScan
from mgn_database import updateTimestampImage
from mgn_database import updateJsonScan
from mgn_database import returnAllHashs
from mgn_database import removeImage
from mgn_database import checkIfUploadedScanDefectDojo
from mgn_database import insertNewHashFileToCompare
from mgn_database import checkHashFileToCompare
from defectdojo_integration import populate_database_defectdojo
from defectdojo_integration import sendReportDefectDojo



def generate_config():
    src = '.config_model.ini'
    dst = '.config.ini'
    logging.info('REVULN - Gerando %s com base em %s.\nBasta editar o %s com base no ambiente que será analisado.' %(dst,src,dst))
    if os.path.exists(src) is True:
        shutil.copyfile(src, dst)
        
# if os.path.exists('.config.ini') is True:
#     config = configparser.ConfigParser()
#     config.sections()
#     config.read('.config.ini')
#     logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename=environment.var_env_global['RG_DEBUG_FILE'], filemode='a', level=logging.DEBUG)
#     coloredlogs.install()
# elif os.path.exists('.config.ini') is False:
#     logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
#     coloredlogs.install()
#     logging.critical('REGVULN - Favor criar o arquivo .config.ini baseado no .config_model.ini.\n\nGerando...')
#     #generate_config()
#     exit()

user_current=str(pwd.getpwuid(os.getuid())[0])
all_hashs = []
limit = int(environment.var_env_global['RG_SCANTIME_DELAY_SEC'])*int(environment.var_env_global['RG_SCANTIME_TIME_TO_SCAN'])


def main():
    flag = 0
    for rep in requestAPI(environment.var_env_global['RG_REGISTRY_CATALOG'])['repositories']:
        image = rep
        tags = requestAPI('/v2/%s/tags/list' %(image))
        for tag in tags['tags']:
            flag += 1
            digest = requestAPI('/v2/%s/manifests/%s' %(image,tag))
            try:
                sha256 = digest.get('config').get('digest')
            except:
                if sha256 == None:
                    sha256 = digest.get('manifests')[0].get('digest')
            try:
                size = digest.get('config').get('size')
            except:            
                if size == None:
                    size = digest.get('manifests')[0].get('size')
            # except:
            #     logging.critical("REGVULN - Digest HASH da imagem %s:%s nao encontrada. Favor realizar upload novamente da imagem no Registry, para que o erro seja corrigido." %(image,tag))

            all_hashs.append(sha256)
            timestamp_image = int(datetime.timestamp(datetime.now()))
            if checkIfImageExist(image,tag,sha256) == False:
                insertImage(image,tag,size,timestamp_image,sha256)
                DockerPull(environment.var_env_global['RG_REGISTRY_DNS'],image,tag)
                TrivyScan(environment.var_env_global['RG_REGISTRY_DNS'],image,tag,sha256,flag)
            elif checkIfImageNeedScan(image,tag,limit,sha256) == True:
                logging.info('REGVULN - Analisando novamente imagem %s:%s' %(image,tag))
                DockerPull(environment.var_env_global['RG_REGISTRY_DNS'],image,tag)
                TrivyScan(environment.var_env_global['RG_REGISTRY_DNS'],image,tag,sha256,flag)

def checkTrivy():
    trivy = os.path.exists(os.system("which trivy > /dev/null 2>&1"))
    if trivy is True:
        logging.info('REGVULN - Trivy instalado')
        return True
    else:
        logging.critical('REGVULN - Favor instalar o Trivy em:\nhttps://github.com/aquasecurity/trivy/releases/latest/')
        exit()

def checkCredDocker():
    cfgfile = environment.var_env_global['RG_DOCKER_CRED_FILE'].replace('$HOME', os.getenv('HOME'))
    cfgdocker = os.path.exists(cfgfile)
    cred = '%s:%s' %(environment.var_env_global['RG_REGISTRY_USER'],environment.var_env_global['RG_REGISTRY_PASSWORD'])
    credb64 = str(base64.b64encode(bytes(cred, 'utf-8'))).split("'", 2)[1]
    if cfgdocker is True:
        f = open(cfgfile, 'r')
        try:
            cfgjson = json.loads(f.read())
            f.close()
        except:
            logging.warning("Arquivo de configuracao Docker JSON invalido: %s\n\nRecriando..." %(cfgfile))
            open(cfgfile, "a").close()
            cfgjson = {'auths': {environment.var_env_global['RG_REGISTRY_DNS']: {'auth': credb64}}}
            with open(cfgfile, "w") as f:
                f.write(str(cfgjson).replace("'",'"'))
                f.close()
        try:
            if len(cfgjson['auths'][environment.var_env_global['RG_REGISTRY_DNS']]) == 1:
                if cfgjson['auths'][environment.var_env_global['RG_REGISTRY_DNS']]['auth'] == credb64:
                    logging.info("REGVULN - Credenciais de login Docker salvas batem com a informada.")
                else:
                    logging.warning("REGVULN - Credenciais de login Docker salvas NAO batem com a informada. Atualizando...")
                    item = {environment.var_env_global['RG_REGISTRY_DNS']: {'auth': credb64}}
                    cfgjson['auths'].update(item)
                    with open(cfgfile, 'a') as f:
                        f.truncate()
                        f.close()
                    with open(cfgfile, 'w') as f:
                        f.write(str(cfgjson).replace("'",'"'))
                        f.close()
        except:
            item = {environment.var_env_global['RG_REGISTRY_DNS']: {'auth': credb64}}
            cfgjson['auths'].update(item)
            with open(cfgfile, 'a') as f:
                f.truncate()
                f.close()
            with open(cfgfile, 'w') as f:
                f.write(str(cfgjson).replace("'",'"'))
                f.close()
    else:
        userhome = os.path.expanduser('~')
        try:
            os.mkdir('%s/.docker' %(userhome))
        except:
            None
        os.chmod('%s/.docker' %(userhome), stat.S_IRWXU)
        open(cfgfile, "a").close()
        os.chmod(cfgfile, stat.S_IRWXU)
        cfgjson = {'auths': {environment.var_env_global['RG_REGISTRY_DNS']: {'auth': credb64}}}
        with open(cfgfile, "w") as f:
            f.write(str(cfgjson).replace("'",'"'))
            f.close()

def checkDocker():
    dockerSock = os.path.exists('/var/run/docker.sock')
    checkCredDocker()
    if dockerSock is False:
        logging.critical('DOCKER - Não identificado comunicação com o Daemon Docker (/var/run/docker.sock)')
        exit()

def requestAPI(path):
    headers = {
                'accept': 'application/vnd.docker.distribution.manifest.v2+json'
               }
    r = requests.get(url = '%s%s' %(environment.var_env_global['RG_REGISTRY_URL'],path), auth=(environment.var_env_global['RG_REGISTRY_USER'], environment.var_env_global['RG_REGISTRY_PASSWORD']), verify=False, headers=headers)
    handlingError(r.content, r.status_code)
    if r.status_code == 404:
        headers = {
                'accept': 'application/vnd.oci.image.index.v1+json'
               }
        r = requests.get(url = '%s%s' %(environment.var_env_global['RG_REGISTRY_URL'],path), auth=(environment.var_env_global['RG_REGISTRY_USER'], environment.var_env_global['RG_REGISTRY_PASSWORD']), verify=False, headers=headers)
        handlingError(r.content, r.status_code)
        print(json.dumps(r.json(), indent=4))
        
    result = r.json()
    return result

def checkCredRegistry():
    r = requests.get(url = '%s%s' %(environment.var_env_global['RG_REGISTRY_URL'],environment.var_env_global['RG_REGISTRY_CATALOG']), auth=(environment.var_env_global['RG_REGISTRY_USER'], environment.var_env_global['RG_REGISTRY_PASSWORD']), verify=False, headers={'accept': 'application/vnd.docker.distribution.manifest.v2+json'})
    handlingError(r.content, r.status_code)
    status = int(r.status_code)
    if status == 401:
        logging.error("REGVULN - Credenciais informadas sao invalidas:\nUser: %s\nPass: ***********\n\nFavor informar credenciais validas." %(environment.var_env_global['RG_REGISTRY_USER']))
        exit()
    elif status == 200:
        return True
    else:
        logging.error("REGVULN - Erro ao comunicar com registry: HTTP %i" %(status))

def convertToBinaryData(filename):
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData

def Difference(li1, li2):
    return list(set(li1) - set(li2)) + list(set(li2) - set(li1))

def DockerPull(dns,image,tag):
    if environment.var_env_global['RG_DOCKER_CACHE'] == 'True' or environment.var_env_global['RG_DOCKER_CACHE'] == 'true':
        if user_current != 'root':
            logging.warning('Não é possivel executar como %s, favor re-executar o script como ROOT, funcao de Cache habilitada.' %(user_current))
            exit()
        client = docker.Client(base_url='unix://var/run/docker.sock', version='auto')
        logging.info('DOCKER - Baixando imagem OCI %s/%s:%s' %(dns,image,tag))
        image = client.pull("%s/%s:%s" %(dns,image,tag))

def TrivyScan(dns,image,tag,sha256,flag):
    try:
        os.mkdir(environment.var_env_global['RG_REPORT_OUTPUT_FOLDER'])
    except:
        logging.debug('REGVULN - Pasta de report destino, já existe %s' %environment.var_env_global['RG_REPORT_OUTPUT_FOLDER'])
    json_file = ('%s/%s-%s-%s.json' %(environment.var_env_global['RG_REPORT_OUTPUT_FOLDER'],dns.replace(":", "-"),image.replace("/", "-"),tag))
    image_name = ("%s/%s:%s" %(dns,image,tag))

    logging.info("TRIVY - Analisando %s" %image_name)
    os.system('trivy image -f json -o %s %s' %(json_file,image_name))

    logging.info("TRIVY - Gerando JSON: %s" %json_file)
    json_bin = convertToBinaryData(json_file)
    hashfile = hashlib.sha256(json_bin).hexdigest()

    hashCompare = checkHashFileToCompare(json_file, hashfile)
    if hashfile != hashCompare:
        updateJsonScan(image,tag,sha256,json_bin)
        updateTimestampImage(image,tag,sha256)
        insertNewHashFileToCompare(json_file, hashfile)
        uploadFlagDojo = checkIfUploadedScanDefectDojo(image,tag,sha256)
        sendReportDefectDojo(image,tag,image_name, environment.var_env_global['RG_REGISTRY_DNS'], uploadFlagDojo, json_file, sha256, flag)
    elif hashfile == hashCompare:
        updateTimestampImage(image,tag,sha256)
        logging.info('REGVULN - IMAGEM %s não retornou alteração nas vulnerabilidades.' %image_name)

def checkMaintenance(all_hashs):
    dbhashes = returnAllHashs()
    list_hashs = []
    for hash in all_hashs:
        chash = hash.split(':', 1)[1]
        list_hashs.append(chash)
    list_hashs = list(set(list_hashs))
    dbhashes = list(set(dbhashes))
    dbhashes.sort()
    list_hashs.sort()
    diff = Difference(list_hashs, dbhashes)
    if len(diff) != 0:
        for hash_image in diff:
            logging.warning('Removendo Imagem %s' %(hash_image))
            os.system('docker rmi -f %s > /dev/null 2>&1' %(hash_image))
            removeImage('sha256:%s' %(hash_image))
    else:
        logging.info("REGVULN - Registry atualizado localmente...")

def splashScreen():
    tprint('{*} REGVULN', font="random")
    print("--------Ferramenta para analise de vulnerabilidade Registryes Docker--------")

def helpScreen():
    splashScreen()
    print('* Faz-se necessário editar o arquivo .config.ini ou definir as variáveis de ambiente caso esteja em modo container')
    print('\n\n- Opções\n')
    print("--daemon \t\t- Usado para rodar o processo em modo Daemon (util para servico continuo)")
    print("--run \t\t\t- Rodar o processo de análise Ad-hoc")
    print("--populate-db \t\t- Consulta os dados do DefectDojo via API e popula o SQLite local para evitar erros")
    print("--help \t\t\t- Mostrar esta tela")
    print("--version \t\t- Mostrar versão do RegVuln")
    
def readArgs():
    try:
        arg=sys.argv[1]
    except:
        helpScreen()
    for arg in sys.argv:
        if arg == '--help':
            helpScreen()
        if arg == '--generate-config':
            generate_config()
        if arg == '--daemon':
            daemonMode()
        if arg == '--version':
            version()
        if arg == '--run':
            splashScreen()
            logging.info('REGVULN - Ad-hoc análise iniciada...')
            createDB()
            checkCredRegistry()
            checkTrivy()
            checkDocker()
            main()
            checkMaintenance(all_hashs)

        if arg == '--populate-db':
            if environment.var_env_global['RG_DEFECTDOJO_ENABLED'] == 'true' or environment.var_env_global['RG_DEFECTDOJO_ENABLED'] == 'True':
                logging.info("REGVULN - Iniciando criação do banco de dados local")
                try:
                    logging.info("REGVULN - Consultando API %s e populando banco de dados..." %environment.var_env_global['RG_DEFECTDOJO_URL'])
                    populate_database_defectdojo()
                    logging.info("REGVULN - Banco de dados criado")
                except:
                    logging.error("REGVULN - Erro ao criar banco de dados, favor checar comunicação com API e permissões de criação de arquivos no diretorio atual.")
            else:
                logging.error('REGVULN - Integração com DefectDojo desabilitada.')

def version():
    print('v1.0.2')

def daemonMode():
    splashScreen()
    logging.info('REGVULN - Ad-hoc análise iniciada...')
    logging.warning('---------- DAEMON MODE ON ----------')
    createDB()
    checkCredRegistry()
    checkTrivy()
    checkDocker()
    while True:
        main()
        checkMaintenance(all_hashs)
        logging.warning('REGVULN - Tempo de espera %i minutos' %(int(environment.var_env_global['RG_SCANTIME_DAEMON'])/60))
        time.sleep(int(environment.var_env_global['RG_SCANTIME_DAEMON']))
        
readArgs()
