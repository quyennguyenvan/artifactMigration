import logging
import json
import os
import subprocess

from container import Configs,SonarTypeNexusServices

logging.basicConfig(format='%(asctime)s %(process)d %(levelname)s %(name)s %(message)s', level=logging.INFO,filename="log.txt")
logger = logging.getLogger(__name__)
logger.info('Logger init ... OK')


if __name__ == "__main__":
    appConfig = json.load(open("configs.json"))

    os.system("az devops login --organization {0}".format(appConfig['azure']['orgURL']))

    Configs.config.override(appConfig)

    _sonaTypeServices = SonarTypeNexusServices.sonarType()
    
    if  _sonaTypeServices.tryAuth():
        isDone =  _sonaTypeServices.getRepositories()
        if isDone:
           subprocess.call([r'{0}'.format(appConfig['artifactUpload'])])
        else:
            print('cash app. quit')       
    else:
        logging.info('crash app. quit')
        print('terminate with status NOT OK')