import pandas as pd
import dash
from dash import html, dcc, Input, Output
import plotly.express as px

# Read the SpaceX data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
spacex_df['outcome'] = spacex_df['class'].map({1: 'Success', 0: 'Failed'})

max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Get unique launch sites for dropdown
site_options = [{'label': 'All Sites', 'value': 'ALL'}]
site_options += [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()]

# Create a dash application
app = dash.Dash(__name__)

# App layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    # Dropdown for Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=site_options,
        value='ALL',
        placeholder="Select a Launch Site",
        searchable=True
    ),
    html.Br(),
    # Pie chart
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    html.P("Payload range (Kg):"),
    # RangeSlider for payload
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        step=1000,
        marks={int(min_payload): str(int(min_payload)), int(max_payload): str(int(max_payload))},
        value=[min_payload, max_payload]
    ),
    # Scatter chart
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Pie chart callback
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Show total successful launches by site
        fig = px.pie(
            spacex_df,
            names='Launch Site',
            values='class',
            title='Total Success Launches by Site'
        )
    else:
        # Show success vs failed for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        fig = px.pie(
            filtered_df,
            names='outcome',
            title=f'Total Success vs Failed Launches for site {selected_site}'
        )
    return fig

# Scatter chart callback
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter(selected_site, payload_range):
    low, high = payload_range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask]
    if selected_site == 'ALL':
        fig = px.scatter(
            filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category',
            title='Correlation between Payload and Success for All Sites',
            labels={'class': 'Launch Outcome'}
        )
    else:
        site_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        fig = px.scatter(
            site_df, x='Payload Mass (kg)', y='class', color='Booster Version Category',
            title=f'Correlation between Payload and Success for site {selected_site}',
            labels={'class': 'Launch Outcome'}
        )
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
