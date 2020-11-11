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

from cgt import get_cgt_text
from ns import get_ns_text
from pdf import get_pdf_text

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True, prevent_initial_callbacks=True)

app.layout = html.Div([
    dcc.Dropdown(
        id='selection-dropdown',
        options=[
            {'label': 'Meme', 'value': 'Meme'},
            {'label': 'Natural Setting', 'value': 'Natural Setting'},
            {'label': 'PDF', 'value': 'PDF'}
        ],
        value='Meme'
    ),
    html.Div(id='dd-output-container', key='Meme'),
    dcc.RadioItems(id='radio-button', value='All text'),
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
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=False
    ),
    html.Div(id='output-image-upload'),
])


def parse_contents(contents, filename, date, img_type, pdf_choice):
    b64_img = contents.split(',')[1]
    np.save('sign-1', b64_img)    
    decoded = base64.b64decode(b64_img)
    buffer = io.BytesIO(decoded)
    im = Image.open(buffer)
    arr = np.asarray(im)
    #np.save('store-1.npy',arr)
    if img_type == 'Meme':
        text = get_cgt_text(arr)
    elif img_type == 'Natural Setting':
        text = get_ns_text(arr)
    else:
        text = get_pdf_text(arr, pdf_choice)
    return html.Div([
        html.H5('Original filename: ' + filename, id='filename', key=filename),
        # HTML images accept base64 encoded strings in the same format
        # that is supplied by the upload
        html.Img(src=contents),
        html.Div("Detexted text: " + text, id='txt', key=text),
        html.Div([html.Button("Download", id="btn"), Download(id="download")]),
        html.Hr(),
    ])

@app.callback(
    dash.dependencies.Output('dd-output-container', 'children'),
    [dash.dependencies.Input('selection-dropdown', 'value')])
def update_output(value):
    if value == 'Meme':
        return html.Div('This setting is best used for computer generated text on noisy or plain backgrounds', id='dd-output-container', key='Meme')
    elif value == 'Natural Setting':
        return html.Div('This setting is best used for text in the wild or natural settings', id='dd-output-container', key='Natural Setting')
    else:
        return html.Div([html.Div('This setting is best used for plain documents with black text on white backgrounds such as book screenshots or receipts', id='dd-output-container', key='PDF'),
                        dcc.RadioItems(
                            options=[
                            {'label': 'All text', 'value': 'all text'},
                            {'label': 'Dates only', 'value': 'dates'},
                            {'label': 'Monetary amounts only', 'value': 'money'}
                            ],
                            value='all text',
                            id='radio-button'
                        )]) 

@app.callback(Output('output-image-upload', 'children'),
              [Input('upload-image', 'contents')],
              [State('upload-image', 'filename'),
               State('upload-image', 'last_modified'),
               State('dd-output-container', 'key'),
               State('radio-button', 'value')])
def update_output(contents, filename, date, img_type, pdf_choice):
    if contents is not None:
        children = [parse_contents(contents, filename, date, img_type, pdf_choice)]
        return children

@app.callback(Output("download", "data"), [Input("btn", "n_clicks")], State("txt", "key"), State('filename', 'key'),)
def download_text(n_clicks, text, filename):
    return dict(content=text, filename=filename+'.txt')

if __name__ == '__main__':
    app.run_server(debug=True)