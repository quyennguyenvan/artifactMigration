import json
import logging

class Report(object):

    def __init__(self, config):
        self.config = config


    def Reporting(self,data, pathFile = None):
        reportedFile: str
        if pathFile == None:
            reportedFile = self.config['downloadHistory']
        else:
            reportedFile = pathFile
        with open(reportedFile,'a') as export:
            export.write(data)
            export.write("\n")
            export.close()