# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

#-------------------------------------------------------------------------------
# Read the airline data into pandas dataframe
#-------------------------------------------------------------------------------
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload  = spacex_df['Payload Mass (kg)'].max()
min_payload  = spacex_df['Payload Mass (kg)'].min()

#-------------------------------------------------------------------------------
# Additional Function
#-------------------------------------------------------------------------------
def get_launch_site_opts()  :
    selections = [ {"label" : site, "value" : site } for site in spacex_df['Launch Site'].unique() ]
    selections.insert(0,{"label" : "All Sites", "value" : "ALL" })
    return selections

def get_df_for_scatter(site_selected, min_val,max_val) :
    if site_selected == "ALL" :
        data_scatter = [
            spacex_df[ spacex_df["Payload Mass (kg)"].between(min_val, max_val) 
            ],"All Sites"
        ]
    else :
        data_scatter = [
            spacex_df[ 
                (spacex_df["Launch Site"] == site_selected) & 
                (spacex_df["Payload Mass (kg)"].between(min_val, max_val)) 
            ],site_selected
        ]
    return data_scatter

#-------------------------------------------------------------------------------
# Create a dash application
#-------------------------------------------------------------------------------
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(
    children=[
        html.H1(
            'SpaceX Launch Records Dashboard',
            style={
            'textAlign': 'center', 
            'color': '#503D36',
            'font-size': 40}),

        # TASK 1: Add a dropdown list to enable Launch Site selection
        # The default select value is for ALL sites
        # dcc.Dropdown(id='site-dropdown',...)
        dcc.Dropdown(
            id = 'site-dropdown',
            options = get_launch_site_opts(),
            value = 'ALL',
            placeholder = "Site Selection",
            searchable = True
        ),
        html.Br(),

        # TASK 2: Add a pie chart to show the total successful launches count for all sites
        # If a specific launch site was selected, show the Success vs. Failed counts for the site
        html.Div(dcc.Graph(id='success-pie-chart')),
        html.Br(),

        # TASK 3: Add a slider to select payload range
        #dcc.RangeSlider(id='payload-slider',...)
        html.P("Payload range (Kg):"),
        dcc.RangeSlider(
            id    = 'payload-slider',
            min   = 0, 
            max   = max_payload,
            step  = 1000, 
            value = [min_payload, max_payload]
        ),

        # TASK 4: Add a scatter chart to show the correlation between 
        # payload and launch success
        html.Div(dcc.Graph(id='success-payload-scatter-chart')),
    ])

#-------------------------------------------------------------------------------
# Callback Functions
#-------------------------------------------------------------------------------
# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(site_selected):
    data_chart   = spacex_df
    
    if site_selected == 'ALL':
        chart_names  = data_chart["Launch Site"]
        chart_values = "class"
        chart_title  = "Total Launched By Site"
        fig = px.pie( 
            data_chart, values=chart_values, names=chart_names, title=chart_title
        )
    else:
        # return the outcomes piechart for a selected site
        data_chart   = spacex_df[ spacex_df["Launch Site"] == site_selected ]
        success_rate = sum(data_chart['class'] == 1)
        failed_rate  = sum(data_chart['class'] == 0)
        chart_values = [success_rate, failed_rate]
        chart_names  = ["Success", "Failed"]
        chart_title  = f"Success vs Failed Launches By {site_selected}"
        fig = px.pie( 
            data_chart, values=chart_values, names=chart_names, 
            title=chart_title, color = chart_names, 
            color_discrete_map = {"Failed": "red", "Success" : "royalblue"}
        )
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, 
# `success-payload-scatter-chart` as output
@app.callback(
    Output(
        component_id='success-payload-scatter-chart', component_property='figure'),
        [
            Input(component_id='site-dropdown' , component_property='value'), 
            Input(component_id='payload-slider', component_property='value')
        ]
)
def get_slider(site_selected, mass_selected) :
    if site_selected is None or len(mass_selected) == 0 : fig = None
    else :
        data_chart = get_df_for_scatter(
            site_selected = site_selected, 
            min_val = mass_selected[0],
            max_val = mass_selected[1] 
        )
        fig = px.scatter(
            data_chart[0],
            x          = "Payload Mass (kg)",
            y          = "class",
            color      = "Booster Version Category",
            size       = 'Payload Mass (kg)', 
            hover_data = ['Payload Mass (kg)'],
            title      = f"Correlation Between Payload and Success for {data_chart[1]}"
        )
    return fig

#-------------------------------------------------------------------------------
# Run the app
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server()
