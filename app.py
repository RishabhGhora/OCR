import datetime
import dash
from dash.dependencies import Input, Output, State
from dash_extensions import Download
import dash_core_components as dcc
import dash_html_components as html

import io
import base64
from PIL import Image
import numpy as np
from matplotlib import pyplot as plt

from OCR import get_text
from PIL import Image
import os

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, title='README.ME', external_stylesheets=external_stylesheets, suppress_callback_exceptions=True, prevent_initial_callbacks=True)

app.layout = html.Div([

    ### code for the HEADER
    html.Div([
        html.H1(
            "README.ME",
            id='title-header',
            style={
                'textAlign': 'center'
            }
        ), html.H5(
            "A CS 6220 Project",
            style={
                'textAlign': 'center'
            }
        ), html.P(
            "Creators: Mohak Chadha, Edward Chiao, Rishabh Ghora, Thor Keller, Priyansh Srivastava",
            style={
                'textAlign': 'center'
            }
        )
    ],  style={
            'textAlign': 'center',
            'padding-top': 15,
            'padding-bottom': 15
        }),
    ### end code for the HEADER
  
    html.Div([
        dcc.Upload(
            id='upload-image',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select File')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
        },
        # Allow multiple files to be uploaded
        multiple=False
    ), dcc.Loading(
            id="loading-1",
            type="circle",
            children=html.Div(id="output-image-upload")
    )], style={
        'text-align': 'center',
        'margin-left': '20%',
        'margin-right': '20%',
        'padding-top': 0
    }),
])


def parse_contents(contents, filename, date):
    b64_img = contents.split(',')[1]
    decoded = base64.b64decode(b64_img)
    buffer = io.BytesIO(decoded)
    im = Image.open(buffer)
    arr = np.asarray(im)
    text = get_text(arr)
    contents = resize_input(im)
    return html.Div([
        html.H5('Original Filename: ' + filename, id='filename', key=filename),
        # HTML images accept base64 encoded strings in the same format
        # that is supplied by the upload
        html.Img(src=contents, style={'padding-top': '1%'}),
        html.Br(),html.Br(),
        html.H5("Detected Text: " + text, id='txt', key=text, style={'padding-top': '-50px'}),
        html.Div([html.Button("Download .txt File", id="btn"), Download(id="download")]),
        html.Hr(),
    ], style={
        'text-align': 'center',
    })

# if input image is too big to fit on screen, will resize the display only — doesn't interfere with OCR process
def resize_input(im):
    resized_im = im
    if im.size[0] > 1000:
        ratio = im.size[0] / 1000
        resized_im = im.resize((round(im.size[0] / ratio), round(im.size[1] / ratio)))
    return resized_im

@app.callback(Output('output-image-upload', 'children'),
              [Input('upload-image', 'contents')],
              [State('upload-image', 'filename'),
               State('upload-image', 'last_modified')])
def update_output(contents, filename, date):
    if contents is not None:
        children = [parse_contents(contents, filename, date)]
        return children

@app.callback(Output("download", "data"), [Input("btn", "n_clicks")], State("txt", "key"), State('filename', 'key'),)
def download_text(n_clicks, text, filename):
    return dict(content=text, filename=filename+'.txt')

if __name__ == '__main__':
    app.run_server(debug=True)