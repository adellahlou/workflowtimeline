import datetime
from datetime import datetime
from types import SimpleNamespace

from bokeh.layouts import widgetbox, column, row, layout
from bokeh.core.properties import Array
from bokeh.models import ColumnDataSource, CustomJS, FactorRange, ColumnData, Legend, GroupFilter, CDSView, LegendItem
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.models.tools import BoxSelectTool, RangeTool, PanTool, HoverTool, ResetTool, SaveTool, WheelZoomTool 
from bokeh.models.widgets import DataTable
from bokeh.plotting import figure

from . import utils
import numpy as np

class TimelineWidget(object):
    """Class with three components to visualize a timeline and drill down. 

    scrubber - A high level overview of event result over time.
    timeline - A view that shows execution in chronological order in a timeline.
    drilltable - Displays logs from events selected from timeline.
    """

    def __init__(self, timelinedf, drilldowndf, columnmap, figurekwargs):
        """
            Args:
                timelinedf (pandas.DataFrame):
                drilldowndf (pandas.DataFrame):
                columnmap (dict):
                figurekwargs (obj):
        """
        self.timelinesource = SimpleNamespace(data={})
        self.drillsource_static = SimpleNamespace(data={})
        self.timelinedf = timelinedf
        self.drilldowndf = drilldowndf
        self.columnmap = columnmap
        self.figurekwargs = figurekwargs

    def build(self):
        cls = TimelineWidget

        drillsource, self.drillsource_static, self.drilltable = cls.__create_drilltable(self.drilldowndf, self.figurekwargs.drilltable)
        timelinecallback = cls.__create_timeline_callback(drillsource, self.drillsource_static, self.drilldowndf.columns, self.columnmap)
        self.timelinesource, self.timeline = cls.__create_timeline(self.timelinedf, timelinecallback, self.columnmap, self.figurekwargs.timeline)
        self.scrubber = cls.__create_scrubber(self.timelinedf, self.timelinesource, self.columnmap, self.figurekwargs.scrubber)

        self.widgets = [self.scrubber, self.timeline, self.drilltable]
        return self
    
    def rebuild(self):
        TimelineWidget.__populate_scrubber(self.scrubber, self.timelinedf, self.timelinesource, self.columnmap)
    
    def update(self, timelinedf, drilldowndf):
        self.timelinedf = timelinedf
        self.drilldowndf = drilldowndf
        
        #for col in timelinedf.columns:
        #    self.timelinesource.data[col] = timelinedf[col].values
        #
        #for col in drilldowndf.columns:
        #    self.drillsource_static.data[col] = drilldowndf[col].values
        # 
        #self.rebuild()

    def get_widgets(self):
        return self.widgets

    @classmethod
    def __create_drilltable(cls, drilldowndf, figurekwargs):
        drillsource = ColumnDataSource(dict(**{col : [] for col in drilldowndf.columns }))
        drillsource_static = ColumnDataSource(drilldowndf)
        drilltable= DataTable(columns=utils.table_columns_from_df(drilldowndf), source=drillsource, **figurekwargs)
        return (drillsource, drillsource_static, drilltable)
    
    @classmethod
    def __create_scrubber(cls, scrubberdf, scrubbersource, columnmap, figurekwargs):
        scrubber = figure(y_range=[], x_axis_type='datetime', **figurekwargs)
        scrubber.xaxis.formatter = DatetimeTickFormatter(hourmin=['%H:%M'], minsec=['%H:%M:%S'])
        return cls.__populate_scrubber(scrubber, scrubberdf, scrubbersource, columnmap)

    @classmethod
    def __populate_scrubber(cls, scrubber, scrubberdf, scrubbersource, columnmap):
        categorycol = columnmap['scrubber_category']
        resultcol = columnmap['result']
        colorcol = columnmap['scrubber_color']
        timecol = columnmap['timeline_start_ts']

        results = scrubberdf[resultcol].unique()
        scrubber.y_range.update(factors=results)
        
        categories = scrubberdf[categorycol].unique()
        scrubber_legends_items =[]
        for category in categories:
            view = CDSView(source=scrubbersource, filters=[GroupFilter(column_name=categorycol, group=category)])
            renderer = scrubber.circle(x=timecol, y=resultcol, size=12, source=scrubbersource, view=view, color=colorcol)
            scrubber_legends_items.append(LegendItem(label=category, renderers=[renderer]))
        
        legend = Legend(items=scrubber_legends_items)
        legend.click_policy = 'hide'
        scrubber.add_layout(legend, 'left')
        return scrubber
    
    @classmethod
    def __create_timeline(cls, timelinedf, callback, columnmap, figurekwargs):
        leftcol = columnmap['timeline_start_ts']
        rightcol = columnmap['timeline_end_ts']
        categorycol = columnmap['timeline_category']
        resultcol = columnmap['result']
        colorcol = columnmap['timeline_color']

        timelinesource = ColumnDataSource(timelinedf)
        timeline = figure(y_range=timelinedf[categorycol], x_axis_type='datetime', **figurekwargs)
        timeline.xaxis.formatter = DatetimeTickFormatter(hourmin=['%H:%M'], minsec=['%H:%M:%S'])
        timeline.yaxis.axis_label_text_font = 'Consolas'

        results = timelinedf[resultcol].unique()

        for result in results:
            view = CDSView(source=timelinesource, filters=[GroupFilter(column_name=resultcol, group=result)])
            p = timeline.hbar(
                left=leftcol,
                right=rightcol,
                y=categorycol,
                source=timelinesource, 
                view=view,
                color=colorcol,
                legend=result,
                height=0.6)
        
        timelinesource.callback = callback
        timeline.legend.click_policy = 'hide'
        return (timelinesource, timeline)
    
    @classmethod
    def __create_timeline_callback(cls, drillsource, drillsource_static, drillcolumns, columnmap):
        code ="""
            var todate = function(ts) {{ return new Date(new Number(ts)); }};
            var inds = cb_obj.selected.indices;
            var tdata = cb_obj.data; 
            var staticdata = sourcestatic.data;

            var minTime = Number.MAX_VALUE;
            var maxTime = Number.MIN_VALUE;
            for(var i = 0; i <= inds.length; i++) {{
                var ri = inds[i];
                var st = tdata['{timeline_start_ts}'][ri];
                var et = tdata['{timeline_end_ts}'][ri];

                if(et > maxTime)
                    maxTime = et;

                if(st < minTime)
                    minTime = st;
            }}

            for(var i = 0; i < columns.length; i++){{
                source.data[columns[i]] = [];
            }}

            for(var i = 0; i < staticdata['{drilldown_ts}'].length; i++){{
                var ts = staticdata['{drilldown_ts}'][i];
                if(ts > maxTime || ts < minTime)
                    continue;

                for(var j = 0; j < columns.length; j++){{
                    var col = columns[j];
                    var value = staticdata[col][i];
                    source.data[col].push(value);
                }}
            }}

            source.change.emit();
        """.format(**columnmap)
        return CustomJS(args=dict(source=drillsource, sourcestatic=drillsource_static, columns=drillcolumns), code=code)