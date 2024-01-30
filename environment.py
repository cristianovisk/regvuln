import os
import configparser
import coloredlogs, logging

exit_flag = 0
global var_env_global

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename=os.environ.get('RG_DEBUG_FILE'), filemode='a', level=logging.DEBUG)
coloredlogs.install()

list_env = [
    "RG_REGISTRY_DNS",
    "RG_REGISTRY_URL",
    "RG_REGISTRY_PORT"
    "RG_REGISTRY_CATALOG",
    "RG_REGISTRY_USER",
    "RG_REGISTRY_PASSWORD",
    "RG_SCANTIME_DAEMON",
    "RG_SCANTIME_DELAY_SEC",
    "RG_SCANTIME_TIME_TO_SCAN",
    "RG_DEBUG_FILE",
    "RG_REPORT_OUTPUT_FOLDER",
    "RG_DOCKER_CRED_FILE",
    "RG_DOCKER_CACHE",
    "RG_DEFECTDOJO_ENABLED",
    "RG_DEFECTDOJO_URL",
    "RG_DEFECTDOJO_API_KEY",
    "RG_DEFECTDOJO_PRODUCT_NAME",
    "RG_DEFECTDOJO_PRODUCT_TYPE",
    "RG_DEFECTDOJO_ENV"
]

def check_env_var(variable):
    try:
        rep = os.environ[variable]
        return True
    except:
        return False


if os.path.exists('.config.ini') is False:
    env = {
        "RG_REGISTRY_DNS": "",
        "RG_REGISTRY_URL": "",
        "RG_REGISTRY_PORT": 80,
        "RG_REGISTRY_CATALOG": "/v2/_catalog",
        "RG_REGISTRY_USER": "user",
        "RG_REGISTRY_PASSWORD": "password",
        "RG_SCANTIME_DAEMON": "1800",
        "RG_SCANTIME_DELAY_SEC": "3600",
        "RG_SCANTIME_TIME_TO_SCAN": "24",
        "RG_DEBUG_FILE": "regvuln.log",
        "RG_REPORT_OUTPUT_FOLDER": "./reports",
        "RG_DOCKER_CRED_FILE": "$HOME/.docker/config.json",
        "RG_DOCKER_CACHE": "false",
        "RG_DEFECTDOJO_ENABLED": "false",
        "RG_DEFECTDOJO_URL": "",
        "RG_DEFECTDOJO_API_KEY": "",
        "RG_DEFECTDOJO_PRODUCT_NAME": "",
        "RG_DEFECTDOJO_PRODUCT_TYPE": "",
        "RG_DEFECTDOJO_ENV": ""
    }

    for var_env in list_env:
        if check_env_var(var_env) == True:
            tmp = {
                "%s" %var_env: os.environ.get(var_env)
            }
            env.update(tmp)

    for var_env in list_env:
        if env[var_env] == "":
            if var_env.split("_",2)[1] == "DEFECTDOJO" and env['RG_DEFECTDOJO_ENABLED'] == "false":
                logging.debug("Variavel %s vazia" %var_env)
            else:
                logging.critical("Variavel %s vazia, favor definir para rodar" %var_env)
                exit_flag = 1

    if exit_flag == 1:
        exit()
    else:
        var_env_global = env

elif os.path.exists('.config.ini') is True:
        config = configparser.ConfigParser()
        config.sections()
        config.read('.config.ini')
        
        env = {
            "RG_REGISTRY_DNS": config['REGISTRY']['dns'],
            "RG_REGISTRY_URL": config['REGISTRY']['url'],
            "RG_REGISTRY_PORT": config['REGISTRY']['port'],
            "RG_REGISTRY_CATALOG": config['REGISTRY']['catalog'],
            "RG_REGISTRY_USER": config['REGISTRY']['user'],
            "RG_REGISTRY_PASSWORD": config['REGISTRY']['password'],
            "RG_SCANTIME_DAEMON": config['SCANTIME']['wait_time_daemon'],
            "RG_SCANTIME_DELAY_SEC": config['SCANTIME']['delay_in_seconds'],
            "RG_SCANTIME_TIME_TO_SCAN": config['SCANTIME']['timetoscan'],
            "RG_DEBUG_FILE": config['DEBUG']['log_file_path'],
            "RG_REPORT_OUTPUT_FOLDER": config['REPORT']['output_folder'],
            "RG_DOCKER_CRED_FILE": config['DOCKER']['cfg_cred'],
            "RG_DOCKER_CACHE": config['DOCKER']['cache_images'],
            "RG_DEFECTDOJO_ENABLED": config['DEFECT_DOJO']['enabled'],
            "RG_DEFECTDOJO_URL": config['DEFECT_DOJO']['url'],
            "RG_DEFECTDOJO_API_KEY": config['DEFECT_DOJO']['api_key'],
            "RG_DEFECTDOJO_PRODUCT_NAME": config['DEFECT_DOJO']['product_name'],
            "RG_DEFECTDOJO_PRODUCT_TYPE": config['DEFECT_DOJO']['product_type'],
            "RG_DEFECTDOJO_ENV": config['DEFECT_DOJO']['environment']
        }

        for var_env in list_env:
            if env[var_env] == "":
                if var_env.split("_",2)[1] == "DEFECTDOJO" and env['RG_DEFECTDOJO_ENABLED'] == "false":
                    logging.debug("Variavel %s vazia" %var_env)
                else:
                    logging.critical("Variavel %s vazia, favor definir para rodar" %var_env)
                    exit_flag = 1

            if exit_flag == 1:
                exit()
            else:
                var_env_global = env