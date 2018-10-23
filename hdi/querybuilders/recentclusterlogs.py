from kusto import Query

class RecentLogs(Query):
    """Builds recent cluster logs queries"""
    
    default_columns = ['PreciseTimeStamp', 'TraceLevel', 'ActivityId', 'Class', 'Details',
       'Component', 'Role', 'EventId', 'ClusterDnsName']
    name = 'recentlogs'
    template_string = """LogEntry 
| where ClusterDnsName == "{0}" and PreciseTimeStamp >= datetime({1}) and PreciseTimeStamp <= datetime({2})
| join kind= anti (
   DeploymentApiRequestEvent | where ResourceName startswith "{0}" and PreciseTimeStamp < datetime({2}) and Method == "GET"  
) on ActivityId 
| project PreciseTimeStamp, TraceLevel, ActivityId, Class, Details, Component, Role, EventId, ClusterDnsName
| sort by PreciseTimeStamp asc"""
    
    @classmethod
    def build(cls, clusterDnsName, timeRangeBegin, timeRangeEnd):
        clusterDnsName = clusterDnsName if clusterDnsName and (not clusterDnsName.isspace()) else '8u3c4982u3498uy2398u4982'
        return cls.template_string.format(clusterDnsName, timeRangeBegin, timeRangeEnd)

    @classmethod
    def postprocess(cls, result):
        if len(result.columns) == 0:
            result = result.reindex(columns=cls.default_columns)

        return result