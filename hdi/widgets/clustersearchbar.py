import ipywidgets as widgets
from datetime import date, timedelta
from bokeh.io import push_notebook, show

class ClusterSearchBar(object):
    """"""
    def __init__(self, queries, kustodatabase, render):
        today = date.today()
        tomorrow = today + timedelta(days=1)
        self.render = render
        self.links = []
        self.kustodatabase = kustodatabase
        self.queries = queries
        self.clusterDnsNameText = widgets.Text(description="ClusterName:",placeholder="Cluster Dns Name")
        self.searchTimeBeginPicker = widgets.DatePicker(description="Start:", value=today)
        self.searchTimeEndPicker = widgets.DatePicker(description="End:", value=tomorrow)
        self.__interactive = widgets.interactive(
            lambda clusterDnsName, searchTimeBegin, searchTimeEnd: self.search(clusterDnsName, searchTimeBegin, searchTimeEnd), 
            { 'manual':True, 'manual_name':"Search"}, 
            clusterDnsName=self.clusterDnsNameText, 
            searchTimeBegin=self.searchTimeBeginPicker,
            searchTimeEnd=self.searchTimeEndPicker)
        self.ui = widgets.HBox(self.__interactive.children)
    
    def search(self, clusterDnsName, searchTimeBegin=date.today(), searchTimeEnd=date.today()):
        search_kwargs = { 'clusterDnsName': clusterDnsName, 'timeRangeBegin': searchTimeBegin, 'timeRangeEnd': searchTimeEnd}
        results = { 
            query: self.queries[query].build(**search_kwargs).execute(self.kustodatabase).result for query in self.queries 
        }

        self.notify_links(results)
        self.render()
    
    def notify_links(self, results):
        for link in self.links:
            link.update(**results)
            link.build()
    
    def link(self, widget):
        self.links.append(widget)