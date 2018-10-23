from beakerx import TableDisplay
from ipywidgets import VBox, HBox
from IPython.display import display
from ipywidgets import link
from traitlets import Instance
from datetime import datetime as datetimestamp
import datetime

def dateTypeToDatetime(value):
    return datetimestamp.fromtimestamp(value / 1000)

class ColumnFilterByTrait(object):
    """Used to specify a trait that filters a column"""
    def __init__(columnname, traitname, isvalid):
        self.columnname = columnname
        self.traitname = traitname
        self.isvalid = isvalid
        
    def filterrow(self, row, widget):
        traitvalue = widget.get_state(self.traitname)[self.traitname]
        return self.isvalid(row[self.columname], traitvalue)

def TimelineWidget(timeline_data, drilldown_data, startmapping, endmapping, setdoubleclick=True):
    timeline = TableDisplay(timeline_data)
    drilldown = TableDisplay(drilldown_data)
    
    timeline.add_traits(
        startTimeRange=Instance(klass=datetimestamp, args=(datetime.MINYEAR, 1, 1, 0, 0, 0)).tag(sync=True),
        endTimeRange=Instance(klass=datetimestamp, args=(datetime.MAXYEAR, 12, 31, 0, 0, 0)).tag(sync=True))
    
    drilldown.add_traits(
        startTimeRange=Instance(klass=datetimestamp, args=(datetime.MINYEAR, 1, 1, 0, 0, 0)).tag(sync=True), 
        endTimeRange=Instance(klass=datetimestamp, args=(datetime.MAXYEAR, 12, 31, 0, 0, 0)).tag(sync=True))
    
    startlink = link((timeline, startmapping[0]), (drilldown, startmapping[1]))
    endlink = link((timeline, endmapping[0]), (drilldown, endmapping[1]))
    
    def filtertimes(row, column, table):
        start = dateTypeToDatetime(table.values[row][0].timestamp)
        end = dateTypeToDatetime(table.values[row][1].timestamp)
        tabledisplay.set_trait(name='startTimeRange', value=start)
        tabledisplay.set_trait(name='endTimeRange', value=end)
    
    if setdoubleclick:
        timeline.setDoubleClickAction(filtertimes)
    
    timeline.addContextMenuItem(filtertimes)
                     
        
        
    