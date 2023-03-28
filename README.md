<p align="center">
<img src="https://github.com/cristianovisk/regvuln/blob/main/images/logo.svg" alt="RegVuln" border="0">
</p>

![Pipeline Status](https://github.com/cristianovisk/regvuln/actions/workflows/publish.yml/badge.svg)
![Pipeline Status](https://github.com/cristianovisk/regvuln/actions/workflows/release.yml/badge.svg)
[![GitHub release](https://img.shields.io/github/release/cristianovisk/regvuln)](https://github.com/cristianovisk/regvuln/releases/latest)
![GitHub all releases](https://img.shields.io/github/downloads/cristianovisk/regvuln/total)
# RegVuln - Scanner Registry AppSec

📜 Este scanner analisa um servidor registry com imagens de containers Docker/OCI, e analisa TAG a TAG as vulnerabilidades existentes nelas usando Trivy da AquaSec.

💡 Ao ser executado o mesmo analisa o registry destino e analisa todas as imagens enviando-as a uma API Post previamente configurada no `.config.ini` ou salva os arquivos JSON no diretorio de reports também configurado no `.config.ini`

## 🛠 Instalação

**Observação:**
Faz-se necessário baixar o Trivy confirme documentação: https://aquasecurity.github.io/trivy/latest/getting-started/installation/

Linux:

```sh
sudo apt install python3 python3-pip git curl -y
curl https://get.docker.com | sh
git clone https://github.com/cristianovisk/regvuln
cd regvuln
pip3 install -r requirements.txt
cp .config_model.ini .config.ini
sudo apt-get install wget apt-transport-https gnupg lsb-release -y
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
echo deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main | sudo tee -a /etc/apt/sources.list.d/trivy.list
sudo apt update
sudo apt install trivy -y
```


## 📈 Exemplo de uso com .config

Para que a analise ocorra sem problemas, é necessário editar o arquivo `.config.ini` com as variáveis definidas corretamente:

```ini
[REGISTRY]
dns = dns.registry.destiny.com
url = https://dns.registry.destiny.com
catalog = /v2/_catalog
user = user_to_autentication_basic
password = password_to_use

[SCANTIME]
delay_in_seconds = 3600 # Time in seconds to delay scan the images
timetoscan = 1 # ex. (timetoscan * delay_in_seconds) = limit_time_to_reescan_images

[REPORT]
output_folder = ./reports # folder to save reports generated by Trivy

[DOCKER]
cfg_cred = /home/cristiano/.docker/config.json #file that have password Docker registry
cache_images = false # enabled will save all images in cache

[DEFECT_DOJO]
url = https://dns.defectdojo.destiny.com #endpoint URL DEFECTDOJO
enabled = false #if enable or disable with True or False
api_key = KEY_API_DEFECT_DOJO # API Key DEFECT DOJO, get in WEB-GUI
product_name = NAME_REGISTRY # Name the Registry OCI to 
product_type = ENTERPRISE-BU # Name the Enterprise or BU
environment = PROD # optional unused
```

Após a configuração ser feita, basta executar o arquivo `regvuln.py` com o comando:
```sh
python3 regvuln.py --run
```

Todos os arquivos JSON serão salvos por padrão na pasta `./reports` (caso não tenha sido alterado no `.config.ini`), exemplo:
```sh
cristiano@horusec:~/registry_scan_appsec$ ls -ilha ./reports/
total 14M
1836862 drwxrwxr-x 2 cristiano cristiano 4.0K Jul 10 13:49 .
1835204 drwxrwxr-x 5 cristiano cristiano 4.0K Jul 10 19:20 ..
1843734 -rw-rw-r-- 1 cristiano cristiano  16K Jul 10 19:05 docker-registry.ddns.net-app-examlpe-compose_web-latest.json
1843839 -rw-rw-r-- 1 cristiano cristiano 3.1M Jul 10 19:08 docker-registry.ddns.net-bytebank-latest.json
1843853 -rw-rw-r-- 1 cristiano cristiano  34K Jul 10 19:08 docker-registry.ddns.net-dexter-26.json
1843854 -rw-rw-r-- 1 cristiano cristiano  34K Jul 10 19:08 docker-registry.ddns.net-dexter-27.json
1843855 -rw-rw-r-- 1 cristiano cristiano  34K Jul 10 19:08 docker-registry.ddns.net-dexter-29.json
1843856 -rw-rw-r-- 1 cristiano cristiano  34K Jul 10 19:08 docker-registry.ddns.net-dexter-30.json
1843857 -rw-rw-r-- 1 cristiano cristiano  34K Jul 10 19:08 docker-registry.ddns.net-dexter-31.json
1843858 -rw-rw-r-- 1 cristiano cristiano  34K Jul 10 19:08 docker-registry.ddns.net-dexter-32.json
1843859 -rw-rw-r-- 1 cristiano cristiano  34K Jul 10 19:08 docker-registry.ddns.net-dexter-33.json
1843860 -rw-rw-r-- 1 cristiano cristiano  34K Jul 10 19:08 docker-registry.ddns.net-dexter-34.json
1843861 -rw-rw-r-- 1 cristiano cristiano  34K Jul 10 19:08 docker-registry.ddns.net-dexter-35.json
1843862 -rw-rw-r-- 1 cristiano cristiano  34K Jul 10 19:08 docker-registry.ddns.net-dexter-36.json
1843863 -rw-rw-r-- 1 cristiano cristiano  34K Jul 10 19:08 docker-registry.ddns.net-dexter-37.json
1843864 -rw-rw-r-- 1 cristiano cristiano  34K Jul 10 19:09 docker-registry.ddns.net-dexter-38.json
1843865 -rw-rw-r-- 1 cristiano cristiano  34K Jul 10 19:09 docker-registry.ddns.net-dexter-41.json
1843866 -rw-rw-r-- 1 cristiano cristiano  34K Jul 10 19:09 docker-registry.ddns.net-dexter-43.json
1843867 -rw-rw-r-- 1 cristiano cristiano  34K Jul 10 19:09 docker-registry.ddns.net-dexter-44.json
1843868 -rw-rw-r-- 1 cristiano cristiano  34K Jul 10 19:09 docker-registry.ddns.net-dexter-45.json
1843869 -rw-rw-r-- 1 cristiano cristiano  34K Jul 10 19:09 docker-registry.ddns.net-dexter-46.json
1843870 -rw-rw-r-- 1 cristiano cristiano  34K Jul 10 19:09 docker-registry.ddns.net-dexter-47.json
1843871 -rw-rw-r-- 1 cristiano cristiano  34K Jul 10 19:09 docker-registry.ddns.net-dexter-48.json
1843872 -rw-rw-r-- 1 cristiano cristiano  34K Jul 10 19:09 docker-registry.ddns.net-dexter-49.json
1843873 -rw-rw-r-- 1 cristiano cristiano  34K Jul 10 19:09 docker-registry.ddns.net-dexter-50.json
1843874 -rw-rw-r-- 1 cristiano cristiano  34K Jul 10 19:09 docker-registry.ddns.net-dexter-52.json
1843875 -rw-rw-r-- 1 cristiano cristiano  34K Jul 10 19:09 docker-registry.ddns.net-dexter-53.json
1843841 -rw-rw-r-- 1 cristiano cristiano 8.4K Jul 10 19:08 docker-registry.ddns.net-dexter-54.json
1843831 -rw-rw-r-- 1 cristiano cristiano 8.4K Jul 10 19:08 docker-registry.ddns.net-dexter-55.json
1843842 -rw-rw-r-- 1 cristiano cristiano 8.4K Jul 10 19:08 docker-registry.ddns.net-dexter-57.json
1843876 -rw-rw-r-- 1 cristiano cristiano  34K Jul 10 19:09 docker-registry.ddns.net-dexter-59.json
1843834 -rw-rw-r-- 1 cristiano cristiano 8.4K Jul 10 19:08 docker-registry.ddns.net-dexter-60.json
1843843 -rw-rw-r-- 1 cristiano cristiano 8.4K Jul 10 19:08 docker-registry.ddns.net-dexter-62.json
1843846 -rw-rw-r-- 1 cristiano cristiano 8.4K Jul 10 19:08 docker-registry.ddns.net-dexter-63.json
1843847 -rw-rw-r-- 1 cristiano cristiano 8.4K Jul 10 19:08 docker-registry.ddns.net-dexter-64.json
1843844 -rw-rw-r-- 1 cristiano cristiano 8.4K Jul 10 19:08 docker-registry.ddns.net-dexter-65.json
1843848 -rw-rw-r-- 1 cristiano cristiano 8.4K Jul 10 19:08 docker-registry.ddns.net-dexter-67.json
1843850 -rw-rw-r-- 1 cristiano cristiano 8.4K Jul 10 19:08 docker-registry.ddns.net-dexter-68.json
1843851 -rw-rw-r-- 1 cristiano cristiano 8.4K Jul 10 19:08 docker-registry.ddns.net-dexter-69.json
1843852 -rw-rw-r-- 1 cristiano cristiano 8.4K Jul 10 19:08 docker-registry.ddns.net-dexter-70.json
1843877 -rw-rw-r-- 1 cristiano cristiano  26K Jul 10 19:09 docker-registry.ddns.net-horusec-analytic-v2.18.0.json
1843878 -rw-rw-r-- 1 cristiano cristiano  26K Jul 10 19:09 docker-registry.ddns.net-horusec-api-v2.18.0.json
1843879 -rw-rw-r-- 1 cristiano cristiano  26K Jul 10 19:09 docker-registry.ddns.net-horusec-auth-v2.18.0.json
1843880 -rw-rw-r-- 1 cristiano cristiano  25K Jul 10 19:09 docker-registry.ddns.net-horusec-core-v2.18.0.json
1843881 -rw-rw-r-- 1 cristiano cristiano 304K Jul 10 19:09 docker-registry.ddns.net-horusec-generic-v1.1.0.json
1843882 -rw-rw-r-- 1 cristiano cristiano  95K Jul 10 19:09 docker-registry.ddns.net-horusec-js-v1.2.0.json
1843884 -rw-rw-r-- 1 cristiano cristiano 103K Jul 10 19:09 docker-registry.ddns.net-horusec-manager-v2.18.0.json
1843886 -rw-rw-r-- 1 cristiano cristiano  25K Jul 10 19:09 docker-registry.ddns.net-horusec-messages-v2.18.0.json
1843887 -rw-rw-r-- 1 cristiano cristiano  34K Jul 10 19:09 docker-registry.ddns.net-horusec-migrations-local.json
1843888 -rw-rw-r-- 1 cristiano cristiano 106K Jul 10 19:09 docker-registry.ddns.net-horusec-php-v1.0.1.json
1844949 -rw-rw-r-- 1 cristiano cristiano 194K Jul 10 19:09 docker-registry.ddns.net-horusec-python-v1.0.0.json
1844950 -rw-rw-r-- 1 cristiano cristiano  26K Jul 10 19:09 docker-registry.ddns.net-horusec-vulnerability-v2.18.0.json
1844951 -rw-rw-r-- 1 cristiano cristiano  25K Jul 10 19:09 docker-registry.ddns.net-horusec-webhook-v2.18.0.json
1844952 -rw-rw-r-- 1 cristiano cristiano 347K Jul 10 19:09 docker-registry.ddns.net-nginx-latest.json
1846340 -rw-rw-r-- 1 cristiano cristiano 8.1M Jul 10 19:09 docker-registry.ddns.net-sida-latest.json
1846525 -rw-rw-r-- 1 cristiano cristiano  90K Jul 10 19:10 docker-registry.ddns.net-ubuntu-18.04.json
1846478 -rw-rw-r-- 1 cristiano cristiano  56K Jul 10 19:10 docker-registry.ddns.net-ubuntu-20.04.json
1846341 -rw-rw-r-- 1 cristiano cristiano  51K Jul 10 19:10 docker-registry.ddns.net-ubuntu-latest.json
```

Os dados também são centralizados em um banco SQLite por nome `registry.db` que é gerado no primeiro momento da execução do `regvuln.py`.

## 📈 Exemplo de uso com variáveis de ambiente em Docker

O exemplo abaixo será usado caso o RegVuln esteja com o modo Defect Dojo desabilitado.

```bash
docker run --rm -e RG_REGISTRY_DNS="ecr.amazonurl.com" \
                -e RG_REGISTRY_URL="http://ecr.amazonurl.com" \
                -v /var/run/docker.sock:/var/run/docker.sock \
                -v $PWD:/opt/regvuln/reports \
                -it cristianovisk/regvuln:latest
```

Já o exemplo abaixo mostra a configuração completa mínima necessária para usar com integração com Defect Dojo.

```bash
docker run --rm -e RG_REGISTRY_DNS="ecr.amazonurl.com" \
				-e RG_REGISTRY_URL="http://ecr.amazonurl.com" \
				-e RG_DEFECTDOJO_ENABLED=true \
				-v /var/run/docker.sock:/var/run/docker.sock \
				-it cristianovisk/regvuln:latest
```

A saída será a solicitação das variáveis obrigatórias para a integração funcionar:

```log
2022-10-23 16:35:09 3c31c7c2a275 root[1] CRITICAL Variavel RG_DEFECTDOJO_URL vazia, favor definir para rodar
2022-10-23 16:35:09 3c31c7c2a275 root[1] CRITICAL Variavel RG_DEFECTDOJO_API_KEY vazia, favor definir para rodar
2022-10-23 16:35:09 3c31c7c2a275 root[1] CRITICAL Variavel RG_DEFECTDOJO_PRODUCT_NAME vazia, favor definir para rodar
2022-10-23 16:35:09 3c31c7c2a275 root[1] CRITICAL Variavel RG_DEFECTDOJO_PRODUCT_TYPE vazia, favor definir para rodar
2022-10-23 16:35:09 3c31c7c2a275 root[1] CRITICAL Variavel RG_DEFECTDOJO_ENV vazia, favor definir para rodar
```

Basta definir conforme exemplo abaixo e irá funcionar:

```bash
docker run --rm -e RG_REGISTRY_DNS="ecr.amazonurl.com" \
				-e RG_REGISTRY_URL="http://ecr.amazonurl.com" \
				-e RG_DEFECTDOJO_ENABLED=true \
                -e RG_DEFECTDOJO_URL="https://defectdojo.url.com" \
                -e RG_DEFECTDOJO_API_KEY="chave_de_api_5dc58d5d6s9x" \
                -e RG_DEFECTDOJO_PRODUCT_NAME="REGISTRY_PROD_1" \
                -e RG_DEFECTDOJO_PRODUCT_TYPE="EMPRESA" \
                -e RG_DEFECTDOJO_ENV="Production" \
				-v /var/run/docker.sock:/var/run/docker.sock \
				-it cristianovisk/regvuln:latest
```

## 💻 Configuração de CRON

Basta configurar as variáveis abaixo, e realizar o calculo, 3600 = 1 hora e timetoscan = 2 , significa que o scan será refeito em imagens já analisadas em 2 horas, e wait_time_daemon = 1800 significa que o RegVuln lerá novamente o Registry atrás de imagens novas a cada meia hora.
```shell
[SCANTIME]
wait_time_daemon = 1800
delay_in_seconds = 3600
timetoscan = 1
```

Para que a configuração tenha efeito como uma cron, basta executar com o argumento `--daemon`.


## 📋 Sobre mim

Cristiano Henrique dos Santos – [Portfólio](https://cristianovisk.github.io) – cristianovisk@gmail.com

Distribuído sob a licença Apache 2.0. Veja `LICENSE` para mais informações.

## 🚀 Contribuição
 ```sh
 # EM BREVE
 ```