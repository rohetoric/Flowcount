import base64
import datetime
import io

import pandas as pd
import operator
import matplotlib.pyplot as plt

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.graph_objects as go

import pandas as pd


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop Master Report or ',
            html.A('Select Master Report')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px',
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-data-upload'),
])





#Function to get the count of the flows
def flow_table(df):

    #Remove null recipe blocks from the dataframe
    df_recipe = df['RecipeFlow'].dropna()

    df_a = df_recipe.str.split(" -> ")

    count_key = {}

    for items in df_a[:100]:
        if len(items) == 1:
            count_key[items[0]] = count_key.get(items[0],0)+1
        else:
            a = 0
            b = 1
            while 1:
                count_key[" -> ".join([items[a],items[b]])] = count_key.get(" -> ".join([items[a],items[b]]),0) + 1
                a = a + 1
                b = b + 1
                if b == len(items)-1 or b == len(items):
                    break 

    #Sort the dictionary based on the count of the flow-               

    sorted_count_key = dict(sorted(count_key.items(), key=operator.itemgetter(1),reverse=True))

    # Converting the lists to dataframe
    flow_dict = {'Flow Direction': list(sorted_count_key.keys()),'Count': list(sorted_count_key.values())}
    flow_df = pd.DataFrame(flow_dict, columns=['Flow Direction','Count'])
    

    #Convert the dictionary to dataframe
    # flow_df = pd.DataFrame.from_dict(data = list(sorted_count_key.items()))
    # flow_df.rename(columns={0: "Flow", 1: "Count"},inplace=True)

    return flow_df.to_dict('records')



def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])


    return html.Div([
        #html.H5(filename),
        #html.H6(datetime.datetime.fromtimestamp(date)),

        html.H1(children="FlowCount App",style = {
            'textAlign': 'center',
            'color': '#2F396E'
            }),
        
        html.Hr(),  # horizontal line

        #Flow Count Table
        dash_table.DataTable(
            id = 'table',

            data =  flow_table(df),

            columns = [{'name': 'Flow Direction', 'id': 'Flow Direction'},{'name': 'Count', 'id': 'Count'}],


            style_header={'fontWeight': 'bold'},

            style_data_conditional = [
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            },

            
        ],
           
         
            style_cell_conditional = [
                {
                'if': {'column_id': c},
                'textAlign': 'center'
                } for c in ['Flow Direction', 'Count']
        ],

            export_columns = 'all',
            export_format = 'csv',
            export_headers = 'display'

                
              
        ),

        # For debugging, display the raw contents provided by the web browser
        # html.Div('Raw Content'),
        # html.Pre(contents[0:200] + '...', style={
        #     'whiteSpace': 'pre-wrap',
        #     'wordBreak': 'break-all'
        # })
    ])


@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children



if __name__ == '__main__':
    app.run_server(debug=True)
