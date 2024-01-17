import pathlib
import pandas as pd
from dash import Dash, html, dcc, dash_table, Input, Output
from dash.dash_table.Format import Format
import dash_daq as daq
import plotly.express as px
import plotly.graph_objects as go

app = Dash(__name__, title="InflationInequalityApp")

# Declare server for deployment. Needed for Procfile.
server = app.server

# Load data
def load_data(data_file: str) -> pd.DataFrame:
    '''
    Load data from /data directory
    '''
    PATH = pathlib.Path(__file__).parent
    DATA_PATH = PATH.joinpath("data").resolve()
    return pd.read_csv(DATA_PATH.joinpath(data_file))

dfs = {}
for i in range(1, 4):  # Loop through figures 1, 2, and 3
    dfs[f'fig{i}'] = load_data(f'fig{i}.csv')

# Define global variables
opacity_fig1 = 0.9
opacity_fig2 = 0.9
opacity_fig3 = 0.75

figmargin = dict(
    l=5,
    r=5
)
titlesize = 14
captionsize = 12
legendsize = 12
labelsize = 10

country_dict = {
    'AT':'Austria', 
    'BE':'Belgium',
    'BG':'Bulgaria', 
    'CY':'Cyprus',
    'CZ':'Czechia',
    'DE':'Germany', 
    'DK':'Denmark', 
    'EE':'Estonia ', 
    'EL':'Greece', 
    'ES':'Spain',
    'FI':'Finland',
    'FR':'France',
    'HR':'Croatia',
    'HU':'Hungary',
    'IE':'Ireland',
    'IT':'Italy',
    'LT':'Lithuania',
    'LU':'Luxembourg',
    'LV':'Latvia',
    'MT':'Malta',
    'NL':'Netherlands',
    'PL':'Poland',
    'PT':'Portugal',
    'RO':'Romania',
    'SE':'Sweden',
    'SI':'Slovenia',
    'SK':'Slovakia'
}

# Layout of the Dash app
app.layout = html.Div([
    html.H1("Inflation Inequality Dashboard", style={'text-align': 'center', 'font-family': 'Arial, sans-serif'}),  # Title

    # Dropdown for country selection
    dcc.Dropdown(
        id='country-dropdown',
        options=[{'label': country_dict[country], 'value': country} for country in dfs['fig1']['Country'].unique()],
        value=dfs['fig1']['Country'].unique()[0],  # Default selected country
        multi=False,
        style={'font-family': 'Arial, sans-serif'}  # Set font for dropdown options
    ),

    # Dropdown for figure selection
    dcc.Dropdown(
        id='figure-dropdown',
        options=[
            {'label': 'Figure 1: Inflation rate for top and bottom', 'value': 'fig1'},
            {'label': 'Figure 2: Expenditure categories', 'value': 'fig2'},
            {'label': 'FIgure 3: Price growth and difference', 'value': 'fig3'}
        ],
        value='fig1',  # Default selected figure
        multi=False,
        style={'font-family': 'Arial, sans-serif'}  # Set font for dropdown options
    ),
    
    # Boolean switch for displaying the data table
    daq.BooleanSwitch(
        id='display-table-switch',
        on=False,
        label='Display Data Table',
        style={
            'font-family': 'Arial, sans-serif',
            'margin-top': '20px',  # Adjust the margin-top property as needed
            'font-size': '24px'  # Adjust the font-size property as needed
        }
    ),

    # Div to hold the selected figure
    html.Div(id='selected-figure')
])

# Text descriptions for each figure
figure_descriptions = {
    'fig1': """   
    Source: Bruegel based on Eurostat and national statistical institutes. Note: Figure 1 displays multiple 
    measures of year-on-year (yoy) inflation since January 2019. 
    The red line represents inflation faced by the top income quantile, the red line by the 
    bottom quantile and the dashed grey line by the total population. If the blue line is above 
    the red, low-income households are more affected by rising prices than high-income ones. 
    The light grey dotted line is the HICP inflation, included to see whether the 
    inflation measure for the total population based on the HBS corresponds broadly to the one 
    reported by Eurostat every month. Given that the weights used for the HICP are calculated 
    differently, slight differences are expected.
    """,
    'fig2': """   
    Source: Bruegel based on Eurostat and national statistical institutes. Note: Figure 2 shows ‘inflation inequality’,
    the black line, defined here as the difference in inflation rates faced by low- and high-income 
    households. If the black line is in positive territory, low-income households face higher rates of yoy 
    inflation than high-income ones. The stacked bars show the contributions of each category of goods and services
    to inflation ineuality. For instance, if a category is positive in a given month, price changes in the goods and services 
    falling under this category contributed to the difference in inflation rates faced by 
    low- and high-income households. This could be either because this category represents a higher 
    share of the low-income consumption basket compared to the high-income basket and its price is 
    rising, or because its share is relatively smaller for the lower-income consumption and the price is decreasing.
    """,
    'fig3': """    
    Source: Bruegel based on Eurostat and national statistical institutes. Note: Figure 3 shows the two factors necessary 
    for a consumption category to affect inflation inequality: the change in price of that category of goods 
    and the difference between the share that it makes up of the consumption bundle of 
    low- and high-income households. 

    Figure 3 distinguishes between the two drivers of inflation inequality: the change in price of categories of goods 
    (average rate of inflation for 2022, y-axis) the difference between the share that each category makes up of the 
    consumption bundle of low- and high-income households (top minus bottom quantile share, x-axis). 
    If all households place the same weight in their overall consumption on a certain good, then even very large 
    increases in its price will not affect inflation inequality. Conversely, even a small increase in prices can 
    drive inflation inequality up if that good makes up a substantially larger share of low-income household consumption.
    If a category is in the top right corner of the plot, it means that its price has increased and that it makes up a 
    greater share of low-income households’ consumption than of high-income ones.
    """
}

# Callback to update the selected figure based on dropdown values
@app.callback(
    Output('selected-figure', 'children'),
    [Input('country-dropdown', 'value'),
     Input('figure-dropdown', 'value'),
     Input('display-table-switch', 'on')]  
)

def update_selected_data(selected_country, selected_figure, display_figure):

    # Select df based on selected figure and country
    selected_data = dfs[selected_figure].loc[dfs[selected_figure]['Country'] == selected_country]

    # Define country-dependent variables
    if selected_country == 'Belgium':
        quantile = 'quartile'
    else:
        quantile = 'quintile'

    # Create table with selected data if switch is on
    if display_figure:
        table = dash_table.DataTable(
            id='table',
            columns=[
                {'name': col, 'id': col, 'type': 'numeric', 'format': Format(precision=3)} for col in selected_data.columns
            ],
            data=selected_data.to_dict('records'),
            style_table={'font-family': 'Arial, sans-serif'},  # Set font for the table
            style_cell={'font-family': 'Arial, sans-serif'}  # Set font for cells
        ) 
    else:
        table = None  # Display table only if switch is on



    # Retrieve the selected country's data for the chosen figure
    if selected_figure == 'fig1':

        # Display Figure 1
        fig = px.line(
            selected_data[['date', f'Bottom {quantile}', f'Top {quantile}']].melt(id_vars='date'),
            x='date',
            y='value',
            color='variable',
            markers=False,
            custom_data=selected_data[['date', f'Bottom {quantile}', f'Top {quantile}']].melt(id_vars='date')
        )

        fig.update_traces(
            hovertemplate='<b>%{customdata[1]}</b><br>%{customdata[0]}: %{customdata[2]:.2f}<extra></extra>',
            line=dict(width=2.5),
            opacity=opacity_fig1
        )

        fig.add_trace(
            go.Scatter(
                x=selected_data[['date', 'Total']].melt(id_vars='date')['date'],
                y=selected_data[['date', 'Total']].melt(id_vars='date')['value'],
                line=dict(
                    color='#696969',
                    width=2,
                    dash='dash'
                ),
                opacity=opacity_fig1,
                name="Total",
                customdata=selected_data[['date', 'Total']].melt(id_vars='date'),
                hovertemplate='<b>Total</b><br>%{x}: %{y:.2f}<extra></extra>'
            ))

        fig.add_trace(
            go.Scatter(
                x=selected_data[['date', 'HICP']].melt(id_vars='date')['date'],
                y=selected_data[['date', 'HICP']].melt(id_vars='date')['value'],
                line=dict(
                    color='#A9A9A9',
                    width=2,
                    dash='dot'
                ),
                opacity=opacity_fig1,
                name="HICP",
                customdata=selected_data[['date', 'HICP']].melt(id_vars='date'),
                hovertemplate='<b>HICP</b><br>%{x}: %{y:.2f}<extra></extra>'
            ))

        fig.update_xaxes(title_text='')  # Set x-axis title to an empty string
        fig.update_yaxes(title_text='') 

        fig.update_layout(
            # ... (Figure 1 layout settings)
            title_text=f'Figure 1: Inflation rate for top and bottom quantile - {country_dict[selected_country]}',
            legend_title_text=''
        )

    elif selected_figure == 'fig2':
        # Display Figure 2
        fig = px.bar(
            selected_data,
            x='date',
            y='value',
            color='coicop',
            opacity=opacity_fig2,
            custom_data= selected_data
        )
        
        fig.add_trace(
            go.Scatter(
                x= selected_data['date'],
                y= selected_data['diff'],
                line=dict(color='#000000'),
                name=f"Difference between inflation rates<br>of bottom and top {quantile}s",
                customdata= selected_data,
                opacity=opacity_fig2,
                hovertemplate='<b>Difference between inflation rates of bottom and top quintiles</b><br>%{x}: %{y:.2f}<extra></extra>'
            )
        )      

        fig.update_xaxes(title_text='')  # Set x-axis title to an empty string
        fig.update_yaxes(title_text='') 

        fig.update_layout(
            # ... (Figure 2 layout settings)
            title_text=f'Figure 2: Expenditure categories driving inflation inequality - {country_dict[selected_country]}',
            legend_title_text=''
        )

    elif selected_figure == 'fig3':
        
        # Display Figure 3
        fig = px.scatter(
            selected_data, 
            x='Difference in share of total expenditure', 
            y='Average inflation in 2022', 
            color='Main category',
            opacity=opacity_fig3,
            custom_data=selected_data)
        
        fig.update_traces(marker=dict(size=7),
                    selector=dict(mode='markers'),
                    hovertemplate='<b>%{customdata[2]}</b><br>Difference in consumption share: %{x:.2f}<br>Average inflation in 2022: %{y:.2f}<extra></extra>',
                    line=dict(width=2.5),
                    opacity=opacity_fig3)

        fig.update_xaxes(
            zeroline=True, 
            zerolinewidth=1,
            zerolinecolor='grey',
        )

        fig.update_yaxes(
            zeroline=True, 
            zerolinewidth=1,
            zerolinecolor='grey',
        )

        fig.update_layout(
            # ... (Figure 3 layout settings)
            title_text=f'Figure 3: Price growth and difference in importance of consumption categories - {country_dict[selected_country]}',
            legend_title_text=''
        )

    return [
            table,
            dcc.Graph(
                id='line-plot',
                figure=fig
            ),
            html.Div([
                html.P(figure_descriptions[selected_figure], style={'font-family': 'Arial, sans-serif'})
            ])
        ]


if __name__ == '__main__':
    app.run_server(debug=True)
