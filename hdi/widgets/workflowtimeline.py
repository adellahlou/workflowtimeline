from types import SimpleNamespace

from widgets import TimelineWidget, utils as widgetutils
from util import datautils

from bokeh.models.tools import BoxSelectTool, BoxZoomTool, HoverTool, ResetTool, SaveTool, TapTool, WheelZoomTool

class WorkflowTimeline(object):
    """"""

    DefaultActivityResults = ['Skipped', 'Succeeded', 'Unknown', 'Failed']

    def __init__(self, timelinedf, drilldowndf):
        self.workflowtimeline = timelinedf
        self.recentlogs = drilldowndf
        self.timelinewidget = None

    def build(self):
        self.timelinewidget = TimelineWidget(
            timelinedf=WorkflowTimeline.normalize_timelinedf(self.workflowtimeline),
            drilldowndf=self.recentlogs,
            columnmap={
                'timeline_start_ts' : 'StartedOnTimestamp',
                'timeline_end_ts' : 'EndedOnTimeStamp',
                'timeline_category' : 'Event',
                'timeline_color': 'ResultColor',
                'scrubber_category': 'Workflow',
                'scrubber_color' : 'WorkflowColor',
                'drilldown_ts' : 'PreciseTimeStamp',
                'result': 'Result',
            },
            figurekwargs=SimpleNamespace(
                scrubber={
                    'tools' : WorkflowTimeline.__create_tools(),
                    'toolbar_location' : 'below',
                    'toolbar_sticky' : False,
                    'title' : 'Workflow Activity Results',
                    'x_axis_label' : 'Time elapsed (H:M:S)',
                    'plot_height' : 120
                },
                timeline={
                    'tools' : WorkflowTimeline.__create_tools(mode='hline'),
                    'toolbar_location' : 'below',
                    'title' : 'Workflow Activity Timeline',
                    'x_axis_label' : 'Time elapsed (H:M:S)',
                    'toolbar_sticky' : False,
                },
                drilltable={
                    'fit_columns': False,
                    'height': 600,
                    'width': 1600
                }
            )
        )

        self.timelinewidget.build()
    
    def update(self, workflowtimeline, recentlogs, **kwargs):
        self.workflowtimeline = workflowtimeline
        self.recentlogs = recentlogs

        if self.timelinewidget is None:
            self.build()
        else:
            self.timelinewidget.update(
                timelinedf=WorkflowTimeline.normalize_timelinedf(self.workflowtimeline),
                drilldowndf=self.recentlogs)
    
    def get_widgets(self):
        if self.timelinewidget:
            return self.timelinewidget.get_widgets()
        
        return None

    @classmethod
    def normalize_timelinedf(cls, originaldf):
        durationStrCol = 'DurationStr'
        startedOnStrCol = 'StartedOnTimestampStr'
        endedOnStrCol = 'EndedOnTimeStampStr'
        eventCol = 'Event'
        resultColorCol = 'ResultColor'
        workflowColorCol = 'WorkflowColor'

        timelinedf = originaldf.copy(deep=True)
        if(len(timelinedf) == 0):
            timelinedf[durationStrCol] = ""
            timelinedf[startedOnStrCol] = ""
            timelinedf[endedOnStrCol] = ""
            timelinedf[eventCol] = ""
            timelinedf[resultColorCol] = ""
            timelinedf[workflowColorCol] = ""
            return timelinedf

        activity_desiredmaxwidth = timelinedf['Activity'].str.len().quantile(0.60)
            
        timelinedf[durationStrCol] = timelinedf['Duration'].astype(str)
        timelinedf[startedOnStrCol] = timelinedf['StartedOnTimestamp'].astype(str)
        timelinedf[endedOnStrCol] = timelinedf['EndedOnTimeStamp'].astype(str)
        timelinedf[eventCol] = timelinedf['Workflow'] + " | " + timelinedf['Activity'].apply(lambda s: datautils.normalize_str_width(s, activity_desiredmaxwidth))
        timelinedf = widgetutils.add_color_column(timelinedf, 'Result', override=WorkflowTimeline.DefaultActivityResults, colorcolname=resultColorCol)
        timelinedf = widgetutils.add_color_column(timelinedf, 'Workflow', colorcolname=workflowColorCol)
        timelinedf = timelinedf.sort_values(by=['StartedOnTimestamp', 'EndedOnTimeStamp'], ascending=False)
        return timelinedf
    
    @classmethod
    def __create_tools(cls, **hoverkwargs):
        return [
            TapTool(),
            BoxSelectTool(dimensions='width'),
            BoxSelectTool(dimensions='height'),
            BoxSelectTool(),
            WheelZoomTool(),
            BoxZoomTool(),
            ResetTool(),
            SaveTool(),
            HoverTool(
                tooltips=[
                    ('workflow', '@Workflow'),
                    ('activity', '@Activity'),
                    ('result',   '@Result'),
                    ('duration', '@DurationStr'),
                    ('started',  '@StartedOnTimestampStr'),
                    ('ended',    '@EndedOnTimeStampStr')],
                formatters= {
                    'started' : 'printf',
                    'ended'   : 'printf'
                },
                show_arrow=True,
                **hoverkwargs)]