import os
import logging


logger = logging.getLogger(__name__)

class ADOArtifacts(object):

    def __init__(self, config, reportServices):
        self.config = config
        self.reportServices = reportServices
        logging.info("loading ado services")
    
    def publishArtifacts(self):
        file = open(self.config['artifactUpload'],'r')
        commands = file.readlines()
        count = 1
        for cmd in commands:
            if len(cmd) > 50:
                try:
                    print('[{0}] - running command publish for {1}'.format(count,cmd))
                    os.system("{0}".format(cmd))
                    logging.info('exec: {0}'.format(cmd))
                    count = count + 1
                except Exception as e:
                    logging.error(e)
        
        print('final publishing to azure devops artifact with {0} packages'.format(count))