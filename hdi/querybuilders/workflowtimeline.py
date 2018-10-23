from kusto import Query

class WorkflowTimeline(Query):
    """Builds workflow activity timeline queries"""
    
    default_columns = ['StartedOnTimestamp', 'EndedOnTimeStamp', 'Duration', 'ActivityId',
       'ClusterDnsName', 'Workflow', 'Activity', 'ActivityStatus', 'Result',
       'Details', 'Class', 'Role']
    name = 'workflowtimeline'
    template_string = """LogEntry 
| where ClusterDnsName ==  "{0}" and PreciseTimeStamp >= datetime({1}) and PreciseTimeStamp <= datetime({2})
| join kind= anti (
   DeploymentApiRequestEvent | where ResourceName == "{0}" and PreciseTimeStamp <= datetime({2}) and Method == "GET"  
) on ActivityId 
| sort by PreciseTimeStamp asc
| project PreciseTimeStamp, TraceLevel, ActivityId, Class, Component, Details, Role, EventId, ClusterDnsName
| parse kind = regex flags = i Details with "Workflow " Workflow:string "WorkFlow " WorkflowStatus:string "([.]| )" Activity:string "(Activity )" ActivityStatus:string "[.]( *Result: )?"  Result:string "$"
| where isnull(Workflow)  == false and isempty(Workflow) == false
| sort by Workflow, Activity, PreciseTimeStamp asc
| extend rn=row_number(1, prev(Activity) != Activity or prev(Workflow) != Workflow),  prevActivityStatus = prev(ActivityStatus, 1), prevResult = prev(Result, 1), prevPreciseTimeStamp = prev(PreciseTimeStamp, 1)
| extend rnsum=row_cumsum(rn, prev(Activity) != Activity or prev(Workflow) != Workflow)
| where rnsum == 3
| project-away rn, rnsum 
| project-rename StartedOnTimestamp=prevPreciseTimeStamp, EndedOnTimeStamp=PreciseTimeStamp
| project StartedOnTimestamp, EndedOnTimeStamp, Duration=EndedOnTimeStamp - StartedOnTimestamp, ActivityId, ClusterDnsName, Workflow, Activity, ActivityStatus, Result, Details, Class, Role
| order by StartedOnTimestamp asc"""
    
    @classmethod
    def build(cls, clusterDnsName, timeRangeBegin, timeRangeEnd):
        clusterDnsName = clusterDnsName if clusterDnsName and (not clusterDnsName.isspace()) else '8u3c4982u3498uy2398u4982'
        return cls.template_string.format(clusterDnsName, timeRangeBegin, timeRangeEnd)
    
    @classmethod
    def postprocess(cls, result):
        if len(result.columns) == 0:
            result = result.reindex(columns=cls.default_columns)
        else:
            result.loc[result['Result'].str.isspace(), 'Result'] = 'Unknown'
            
        return result