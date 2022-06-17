from distutils.log import log
import logging
import requests
import base64
import os

logger = logging.getLogger(__name__)

class NexusConfig():
    url: str
    username: str
    password: str


class NexusRepositorConfig():
    def __init__(self, name: str, format: str, type: str, url:str):
        self.name =name,
        self.format = format,
        self.type = type,
        self.url = url,

class SonarNexusType(object):
    
    nexusConfig = NexusConfig()
    def __init__(self, config,reportServices):
        self.config = config
        self.nexusConfig.url = config['nexus']['url']
        self.nexusConfig.username = config['nexus']['username']
        self.nexusConfig.password = config['nexus']['password']
        self.allowedRepos = config['nexus']['allowedRepos']
        self.downloadDict = config['downloadDict']
        self.tracingFile = config['downloadHistory']
        self.notAllowedContentTypes = config['nexus']['notAllowedContentTypes']
        self.reportServices = reportServices
        self.downloadable = 0
        self.batExecutionFile = config['artifactUpload']
        self.adoOrgURI = config['azure']['orgURL']
        self.adoProjectName = config['azure']['project']
        self.feedName = config['azure']['feedName']
        logging.info("loading the config for nexus type")
    
    def tryAuth(self) -> bool:
        data = {
            'username': base64.b64encode(self.nexusConfig.username.encode('ascii')),
            'password': base64.b64encode(self.nexusConfig.password.encode('ascii')),
        }
        postfixURL="ser/rapture/session"
        url = "{0}/{1}".format(self.nexusConfig.url,postfixURL)
        response = requests.post(url, data=data)

        code = response.status_code
        if code == 403 or code == 404 or code == 502:
            logging.error('Authen error or services not available')
            return False
        logging.info('credential valid')
        return True

    def getRepositories(self) -> bool:
        postfixURL = "service/rest/v1/repositories"
        url = "{0}/{1}".format(self.nexusConfig.url,postfixURL)
        auth = (self.nexusConfig.username,self.nexusConfig.password)
        logging.info('calling to services {0}'.format(url))
        response = requests.get(url,auth=auth)
        
        if response.status_code != 200:
            logging.error('calling server error')
            return

        logging.info('calling ok!')
      
        repositories = []
        for item in response.json():
            if item.get('name','n/a') in self.allowedRepos:
                repositories.append(NexusRepositorConfig(
                item.get('name','n/a'),
                item.get('format','n/a'),
                item.get('type','n/a'),
                item.get('url','n/a')))

        logging.info('collection with {0} repositories white list'.format(len(repositories)))
        print('found: {0} repositories white list'.format(len(repositories))) 

        if len(repositories):
            for repo in repositories:
                self.getNexusAtifact(repo)
            print('downloadable with: {0}'.format(self.downloadable))
            return True
        else:
            return False
    
    def getNexusAtifact(self, repository: NexusRepositorConfig):
        continuationToken:str = "abcdrandomeStri"
        repoName = repository.name[0]
        postfixURL = 'service/rest/v1/assets?repository={0}'.format(repoName)
        print('download for repo: {0}'.format(repoName))
        while( continuationToken != "") :
            url = "{0}/{1}".format(self.nexusConfig.url,postfixURL)
            auth = (self.nexusConfig.username, self.nexusConfig.password)
            response = requests.get(url, auth=auth)
            logging.info('request: {0}'.format(url))
            logging.info(response)
            if response.status_code == 200:
                logging.info('calling to {0} 200 code'.format(url))
                result = response.json()
                continuationToken = result.get('continuationToken',"")
                if (continuationToken != ""):
                    postfixURL = 'service/rest/v1/assets?repository={0}&continuationToken={1}'.format(repoName,continuationToken)
                if len(result['items']) == 0:
                    logging.info('repo {0} dont have any items'.format(repoName))
                else:
                    self.downloadAtifact(result['items'])
            else:
                logging.error('calling to {0} error with status code {1}'.format(url, response.status_code))
                continuationToken = ""

    def downloadAtifact(self, assets:any):
        print('running download assets of repo')
        for asset in assets:
            assetFormat = asset.get('path','n/a')
            if assetFormat not in self.notAllowedContentTypes:
                repoName =asset['repository']
                subDict = os.path.join(self.downloadDict,repoName)
                try: 
                    os.mkdir(subDict) 
                except Exception as error: 
                    print(error)  
                try:
                    url = asset['downloadUrl'] 
                    extFile = "nupkg"
                    if asset['format'] == "nuget":
                        extFile = "nupkg"
                    artifactpath = str(asset['path']).replace("/",".")
                    artifactPackageInfor = str(asset['path']).split('/')
                    filePath = str("{0}\\{1}.{2}".format( subDict,artifactpath,extFile ))
                    with open(filePath,"wb") as file:
                        response = requests.get(url)
                        print('downloading for: {0}'.format(filePath))
                        file.write(response.content)
                        print('downloaded : {0}'.format(filePath))
                        self.downloadable = self.downloadable + 1
                        self.reportServices.Reporting('{0} || {1} || {2}'.format(asset['format'],repoName,filePath) , self.tracingFile)
                        executionLine = str('az artifacts universal publish --organization {0} --project="{1}" --scope project --feed {2} --name "{3}" --version {4} --description "{5}" --path {6}').format(self.adoOrgURI, self.adoProjectName, self.feedName, str(artifactPackageInfor[0]).lower(), artifactPackageInfor[1], artifactPackageInfor[0], filePath)
                        self.reportServices.Reporting(executionLine, self.batExecutionFile)
                        print(executionLine)
                        logging.info('downloaded : {0}'.format(file))

                except Exception as error: 
                    print(error)  
            else:
                print('The resources {0} not in allowed content types'. format(asset['path']))
                logging.warning('The resources {0} not in allowed content types'. format(asset['path']))