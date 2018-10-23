from azure.kusto.data.request import KustoClient
from kusto.queriesmixinfactory import QueriesMixinFactory
import inspect

class ClientFactory:
    """Creates a client to a Kusto server with query builders mixed in."""
    
    @classmethod
    def create(cls, server, querybuilders, login=False):        
        if server is None:
            raise ValueError("Failed to create client, no server provided.")
        
        client = KustoClient(server)
        client = cls.__inject_queries(client, querybuilders)
        
        # force the user to authenticate before returning
        if login:
            client.execute(cls.kustoDatabase, ".show version")
        return client
    
    @classmethod
    def __inject_queries(cls, obj, querybuilders):
        return QueriesMixinFactory.extend(obj, querybuilders)