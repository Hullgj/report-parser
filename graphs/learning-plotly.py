"""Some tutorials for trying out plotly from https://plot.ly/python/"""
import plotly
# plotly.tools.set_credentials_file(username='HullGJ', api_key='qSjlZkceE0YLBhs0v22A')
from plotly.offline import plot
import plotly.graph_objs as go

# Create random data with numpy
import numpy as np

N = 1000
random_x = np.random.rand(N)
random_y = np.random.rand(N)

# Create a trace
trace = go.Scatter(
    x = random_x,
    y = random_y,
    mode = 'markers'
)

data = [trace]

# Plot and save in folder/filename
plot(
    data,
    filename='output/basic-scatter.html'
)