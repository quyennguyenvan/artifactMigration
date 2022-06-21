import logging
import json
import os

from container import Configs,SonarTypeNexusServices,ADOArtifactsServices

logging.basicConfig(format='%(asctime)s %(process)d %(levelname)s %(name)s %(message)s', level=logging.INFO,filename="log.txt")
logger = logging.getLogger(__name__)
logger.info('Logger init ... OK')


if __name__ == "__main__":
    appConfig = json.load(open("configs.json"))

    print("please provice the ADO PAT Token, can ref at {0}".format(appConfig["reflink"]))

    os.system("az devops login --organization {0}".format(appConfig['azure']['orgURL']))

    Configs.config.override(appConfig)

    _sonaTypeServices = SonarTypeNexusServices.sonarType()
    _adoServices = ADOArtifactsServices.adoArtifact()
    
    if  _sonaTypeServices.tryAuth():
        isDone =  _sonaTypeServices.getRepositories()
        if isDone:
            _adoServices.publishArtifacts()
        else:
            print('crash app. quit')       
    else:
        logging.info('crash app. quit - please valid information like account credentials or other config')
        print('terminate with status NOT OK')