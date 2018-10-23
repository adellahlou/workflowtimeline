from kusto import ClientFactory, Query
from . import querybuilders
import inspect

class HdiClientFactory(ClientFactory):
    """Creates a client to the HDInsight Kusto server"""
    kustoDatabase = "HDInsight"
    kustoServers = { 
        "prod": "https://hdinsight.kusto.windows.net", 
        "test" : "https://hdinsight.kusto.windows.net"
    }
    
    @classmethod
    def create(cls, environment, login=True):
        server = cls.kustoServers[environment]
        
        if server is None:
            raise ValueError("Failed to create client, given unsupported environment: {0}".format(environment))
        
        return super().create(server, cls.get_querybuilders())

    @classmethod
    def get_querybuilders(cls):        
        builders = [m[1] for m in inspect.getmembers(querybuilders, inspect.isclass)]
        return [b for b in builders if b != Query]