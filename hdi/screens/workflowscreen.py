from datetime import datetime
from bokeh.io import output_notebook, show
from bokeh.layouts import column
from bokeh.plotting import figure
from IPython.display import Javascript, display

import hdi
import hdi.widgets
import warnings

# setup Jupyter
output_notebook(verbose=False, hide_banner=True)
warnings.filterwarnings('ignore')

# setup Kusto
client = hdi.HdiClientFactory.create("prod")
queries = client.queries
kustoDatabase = "HDInsight"

# setup widgets
wft = hdi.widgets.WorkflowTimeline({}, {})

def __renderfactory(cellnum):
    def render():
        from IPython.display import Javascript
        display(Javascript("""
            Jupyter.notebook.execute_cells([1])
        """))
    
    return render

callback = __renderfactory(1)
searchbar = hdi.widgets.ClusterSearchBar({ 'workflowtimeline': queries.workflowtimeline, 'recentlogs': queries.recentlogs }, kustoDatabase, callback)
searchbar.link(wft)


def showsearchbar():
    global searchbar
    display(searchbar.ui)

def showtimeline():
    global wft
    if wft.get_widgets() is None:
        print("No search performed yet. Please perform a cluster search first.")
    else:
        if len(wft.workflowtimeline):
            print("No results found. Double check clusterDnsName and try a new date range.")
        else:
            show(column(wft.get_widgets(), sizing_mode='scale_width'))