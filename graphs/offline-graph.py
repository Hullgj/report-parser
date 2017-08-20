import plotly
plotly.tools.set_credentials_file(username='HullGJ', api_key='qSjlZkceE0YLBhs0v22A')

# import plotly
from plotly.graph_objs import Scatter, Layout

plotly.offline.plot({
    "data": [Scatter(x=[1, 2, 3, 4], y=[4, 3, 2, 1])],
    "layout": Layout(title="hello world")
}, filename = 'output/offline-graph.html')