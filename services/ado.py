import cmd
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
        print('Running for {0} commands'.format(len(commands)))
        count = 0
        maxCPUallowed = 8
        cpuCores = self.config['cpuCores']
        if cpuCores > maxCPUallowed:
            cpuCores = maxCPUallowed
        poolWorks = []
        while (len(commands) != 0):
            try:
                index = 0
                if str(commands[index]) is not None or str(commands[index]) != "":
                    print('Pending for: {} commands'.format(len(commands)))
                    work = (Process(target=self.runPublishArtifacts,  args=(count,commands[index],)))
                    work.start()
                    logging.info('start process Name: {0}'.format(work.name))

                    poolWorks.append(work)
                    commands.pop(index)
                    count = count + 1

                    if (len(poolWorks) == cpuCores):
                        for i in poolWorks:
                            i.join()
                        poolWorks = []
            except Exception as er:
                logging.error(er)
                break

        
        print('final publishing to azure devops artifact with {0} packages'.format(count))

    def runPublishArtifacts(self,count, cmd:str):
        print('[{0}] - running command publish for: {1}'.format(count,cmd))
        os.system("{0}".format(cmd))
        self.reportServices.Reporting(str(cmd), self.config['publishHistory'])
        logging.info('exec: {0}'.format(cmd))   
