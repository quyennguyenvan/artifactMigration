from dependency_injector import containers, providers
from dependency_injector.wiring import Provide


from services.nexus import SonarNexusType
from services.tracing import Report
from services.ado import ADOArtifacts
#load config
class Configs (containers.DeclarativeContainer):
    config = providers.Configuration('config')

class ReportDataServices(containers.DeclarativeContainer):
    reportServices = providers.Singleton(Report, Configs.config)

class SonarTypeNexusServices(containers.DeclarativeContainer):
    sonarType = providers.Singleton(SonarNexusType,Configs.config, reportServices = ReportDataServices.reportServices)

class ADOArtifactsServices(containers.DeclarativeContainer):
    adoArtifact = providers.Singleton(ADOArtifacts,Configs.config, reportServices = ReportDataServices.reportServices)