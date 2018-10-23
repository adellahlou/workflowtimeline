from bokeh.palettes import brewer
from bokeh.models.widgets import DateFormatter, TableColumn
from util import datautils

def get_color_map(keys):
    colormapkey = len(keys) if len(keys) > 3 else 3

    if len(keys) > 11:
        raise ValueError("Received {} keys, more than 11 colors available.".format(len(keys)))
    
    colors = brewer["Spectral"][colormapkey]
    return { keys[i] : colors[i] for i in range(len(keys)) }
    
def add_color_column(data, categorycol, include=[], override=None, colorcolname='Color'):
    keys = datautils.get_categories(data, categorycol, include) if override is None else override
    colormap = get_color_map(keys)
    data[colorcolname] = [colormap[x] for x in data[categorycol]]
    return data

def table_columns_from_df(df, minwidth=30, maxwidth=180):
    charToPix = 6
    tcs = []
    
    for col in df.columns:
        dt = df.dtypes[col]
        maxlen = min(df[col].str.len().max() if dt == object else minwidth, maxwidth)
        colwidth = maxlen * charToPix
        if dt == '<M8[ns]':
            tcs.append(TableColumn(field=col, title=col, width=colwidth, formatter=DateFormatter(format='%F %T.%N')))
        else:
            tcs.append(TableColumn(field=col, width=colwidth, title=col))
    return tcs