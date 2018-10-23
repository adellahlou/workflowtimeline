from util.mixinfactory import MixinFactory
#from azure.kusto.data.helpers import dataframe_from_result_table as df_from_kusto
from collections import namedtuple
from types import SimpleNamespace

class UnbuiltQueryError(Exception):
    pass

class QueriesMixinFactory(object):
    """Creates a QueriesMixin from a list of queries."""
    @classmethod
    def extend(cls, client, querybuilders):
        class QueriesMixin(object):
            """Adds queries property to client."""
            builders = {}

            def _getqueries(self):
                if not hasattr(self, '_queries'):
                    self._queries = Queries(self, self.builders)
                return self._queries

            queries = property(fget=_getqueries)

        
        class Queries(object):
            def __init__(self, client, builders):
                self.client = client
                self.builders = builders
            
            def __getattr__(self, attribute):
                if attribute not in self.builders:
                    raise AttributeError(attribute)
                    
                return QueryTask(self.client, self.builders[attribute])
        
        class QueryTask(object):
            
            def __init__(self, client, builder):
                self.builder = builder
                self.client = client
            
            def build(self, **kwargs):
                self.query = self.builder.build(**kwargs)
                return self
            
            def execute(self, database):
                if self.query is None:
                    raise UnbuiltQueryError('{0} query task does not have a built query.'.format(self.builder.__name__))                    
                    
                response = self.client.execute(database, self.query)
                results = [t for t in response.primary_results if t.table_name == "PrimaryResult"]
                result = results[0].to_dataframe() if results is not None and len(results) == 1 else None
                result = self.builder.postprocess(result)
                
                return SimpleNamespace(raw=response, result=result)
        
        QueriesMixin.builders = { qb.name : qb for qb in querybuilders } if querybuilders is not None else {}
        return MixinFactory.extend(client, QueriesMixin)