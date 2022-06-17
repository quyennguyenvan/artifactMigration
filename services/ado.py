from multiprocessing import Pool, Process
import os
import logging

logger = logging.getLogger(__name__)

class ADOArtifacts(object):

    def __init__(self, config, reportServices):
        self.config = config
        self.reportServices = reportServices
        logging.info("loading ado services")
    
    def publishArtifacts(self):
        print('Starting publish artifacts')
        file = open(self.config['artifactUpload'],'r')
        commands = file.readlines()
        count = 0
        cpuCores = self.config['cpuCores'] - 1
        while (count < len(commands)):
            try:
                poolWorks = []
                for i in range(0,cpuCores):
                    if str(commands[count+i]) is not None or str(commands[count+i]) != "":
                        poolWorks.append((Process(target=self.runPublishArtifacts,  args=(commands[count+i],))))
                for i in poolWorks:
                    i.start()
                    logging.info('start process Name: {0}'.format(i.name))
                for i in poolWorks:
                    i.join()
                    logging.info('join process Name: {0}'.format(i.name))

                count = count + cpuCores
            except Exception as er:
                logging.error(er)
                print(er)
                break
        print('final publishing to azure devops artifact with {0} packages'.format(count))

    def smap(self,f):
        return f()

    def runPublishArtifacts(self, cmd:str):
        print('[*] - running command publish for: {0}'.format(cmd))
        os.system("{0}".format(cmd))
        logging.info('exec: {0}'.format(cmd))   

