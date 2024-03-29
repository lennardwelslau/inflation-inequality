
from dash import Dash, html, dcc, dash_table, Input, Output, callback, State, clientside_callback
from dash.dash_table.Format import Format
import dash_daq as daq
import plotly.express as px
import plotly.graph_objects as go
import pathlib
import pandas as pd
import textwrap


app = Dash(
    __name__, 
    title='Inflation Inequality'
    )

# Declare server for deployment. Needed for Procfile.
server = app.server

# Load data
def path(data_file: str):
    """
    Get file path for data file.
    """
    PATH = pathlib.Path(__file__).parent
    DATA_PATH = PATH.joinpath("data").resolve()
    return DATA_PATH.joinpath(data_file)

dfs = {}
for i in range(1, 4):  # Loop through figures 1, 2, and 3
    dfs[f'fig{i}'] = pd.read_excel(path('inflation_inequality.xlsx'), sheet_name=f'fig{i}', engine='openpyxl')

# Define global variables
opacity = 0.9
titlesize = 14
captionsize = 12
legendsize = 12
labelsize = 10
font_family = 'Arial, sans-serif'
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

# Intro text for the app
app_intro_text = """
    This website explores consumption-based inflation inequality in the EU to shed light on how different income groups 
    are affected differently by inflation. Headline inflation reflects changes in the consumption basket of an average household 
    and thus overlooks variations in individual spending patterns. Depending on how different consumption categories change in price, 
    different spending patterns can result in different rates of inflation. The analysis presented here leverages Household Budget Surveys (HBSs) 
    to estimate the different consumption baskets and inflation rates for households across income groups and EU countries between 2019 and 2024.
    """

# Boolean switches for displaying the data table and figure legend
boolean_switches_div = html.Div([
    # Boolean switch for displaying the data table
    daq.BooleanSwitch(
        id='table-switch',
        on=False,
        label='Show data',
        style={
            'font-family': font_family,
            'margin-top': '5px', 
            'margin-bottom': '10px',
            'font-size': '15px',
            'color': '#333333',
            'display': 'inline-block',  # Display the switch inline
            'margin-right': '20px',     # Add margin between switches
        }
    ),

    # Boolean switch for displaying the figure legend
    daq.BooleanSwitch(
        id='legend-switch',
        on=True,
        label='Show legend',
        style={
            'font-family': font_family,
            'margin-top': '5px', 
            'margin-bottom': '10px',
            'font-size': '15px',
            'color': '#333333',
            'display': 'inline-block',  # Display the switch inline
        }
    ),
])

# Layout of the Dash app
app.layout = html.Div([
        # Title
        html.H1(
            "Inflation Inequality in the EU", 
            style={
                'text-align': 'center', 
                'font-family': font_family
                }
            ),  # Title

        # Intro text
        html.P(
            app_intro_text,
            style={'font-family': 'Arial, sans-serif', 'margin-bottom': '15px'}
        ), 

        # Dropdown for country selection
        dcc.Dropdown(
            id='country-dropdown',
            options=[{'label': country_dict[country], 'value': country} for country in country_dict.keys()],
            value='AT', # Default selected country
            multi=True,
            style={'font-family': font_family}  # Set font for dropdown options
        ),

        # Dropdown for figure selection
        dcc.Dropdown(
            id='figure-dropdown',
            options=[
                {'label': 'Figure 1: Inflation rate for top and bottom quantile', 'value': 'fig1'},
                {'label': 'Figure 2: Expenditure categories driving inflation inequality', 'value': 'fig2'},
                {'label': 'Figure 3: Price growth and difference in importance of consumption categories', 'value': 'fig3'}
            ],
            value='fig1',  # Default selected figure
            multi=False,
            style={
                'font-family': font_family,
                'margin-top': '5px', 
            } 
        ),
        
        # Button to download the data table
        html.Button(
            'Download dataset', 
            id='btn_download',
            className='button',
            style={
                'font-family': font_family,
                'margin-top': '5px'
            },
        ),
        dcc.Download(id='download'),

        # Boolean switches container
        boolean_switches_div,

        # Div to hold the selected figure
        html.Div(id='selected-figure'),

        # Store for detecting mobile devices
        dcc.Store(id='is-mobile-store', data=False),
    ])

# Text descriptions for each figure
figure_descriptions = {
    'fig1': """   
    Source: Bruegel based on Eurostat and national statistical institutes. Note: Figure 1 displays multiple 
    measures of year-on-year (yoy) inflation since January 2019. 
    The blue line represents inflation faced by the top income quantile, the red line by the 
    bottom quantile, and the dashed grey line by the total population. If the red line is above 
    the blue line, low-income households are more affected by rising prices than high-income ones. 
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
    (average rate of inflation for 2023, y-axis) the difference between the share that each category makes up of the 
    consumption bundle of low- and high-income households (top minus bottom quantile share, x-axis). 
    If all households place the same weight in their overall consumption on a certain good, then even very large 
    increases in its price will not affect inflation inequality. Conversely, even a small increase in prices can 
    drive inflation inequality up if that good makes up a substantially larger share of low-income household consumption.
    If a category is in the top right corner of the plot, it means that its price has increased and that it makes up a 
    greater share of low-income households’ consumption than of high-income ones.
    """
}


# Callback for data download button
@callback(
    Output('download', 'data'),
    Input('btn_download', 'n_clicks'),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_file(path('inflation_inequality.xlsx'))


# Clientside callback for detecting mobile devices
clientside_callback(
    """
    function updateIsMobile() {
        var isMobile = window.innerWidth < 700;
        return isMobile;
    }
    """,
    Output('is-mobile-store', 'data'),
    [Input('is-mobile-store', 'data')],
    prevent_initial_call=False
)

# Callback to update the selected figure based on dropdown values
@callback(
    Output('selected-figure', 'children'),
    [Input('country-dropdown', 'value'),
     Input('figure-dropdown', 'value'),
     Input('table-switch', 'on'),
     Input('legend-switch', 'on'),
     Input('is-mobile-store', 'data')]
)
def update_selected_data(selected_countries, selected_figure, show_table, show_legend, is_mobile):

    # Initiate list to hold figures
    figures = []

    # If only one country selected, turn into list
    if isinstance(selected_countries, str):
        selected_countries = [selected_countries]
    
    # Loop through selected countries
    for i, selected_country in enumerate(selected_countries):
        
        # Select df based on selected figure and country
        selected_data = dfs[selected_figure].loc[dfs[selected_figure]['Country'] == selected_country].drop(columns='Country').dropna(axis=1)
        
        # If selected figure is Figure 3, show only Average inflation in 2023 and drop COICOP
        if selected_figure == 'fig3':
            selected_data = selected_data.drop(columns=[
                'COICOP',
                'Average inflation in 2019', 
                'Average inflation in 2020', 
                'Average inflation in 2021', 
                'Average inflation in 2022'
            ])
        
        # Define country-dependent variables
        if selected_country == 'BE':
            quantile = 'quartile'
        else:
            quantile = 'quintile'
        
        # Create table with selected data if switch is on
        if show_table:
            table = dash_table.DataTable(
                id='table',
                columns=[{
                        'name': col, 
                        'id': col, 
                        'type': 'numeric', 
                        'format': Format(precision=3)
                        } for col in selected_data.columns
                    ],
                # selected_data without Country column
                data=selected_data.to_dict('records'),
                fixed_rows={'headers': True},
                page_action='none',
                sort_action='native',
                sort_mode='multi',
                style_header={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'minWidth': '90px', 
                    'width': '90px', 
                    'maxWidth': '90px',
                    'textAlign': 'center'
                    },
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'minWidth': '90px', 
                    'width': '90px', 
                    'maxWidth': '90px',
                    'textAlign': 'left'
                    },
                style_table={
                    'font-family': font_family, 
                    'height': '300px', 
                    'overflowY': 'auto'},
                style_cell={'font-family': font_family}  # Set font for cells
            ) 
        else:
            table = None  # Display table only if switch is on

        # Retrieve the selected country's data for the chosen figure
        if selected_figure == 'fig1':

            title_text=f'Figure 1: Inflation rate for top and bottom {quantile} - {country_dict[selected_country]}'

            fig = px.line(
                selected_data[['Date', f'Top {quantile}', f'Bottom {quantile}']].melt(id_vars='Date'),
                x='Date',
                y='value',
                template='plotly_white',
                color='variable',
                markers=False,
                custom_data=selected_data[['Date', f'Bottom {quantile}', f'Top {quantile}']].melt(id_vars='Date')
            )

            fig.update_traces(
                hovertemplate='<b>%{customdata[1]}</b><br>Date: %{x}<br>Inflation rate: %{y:.2f}<extra></extra>',
                line=dict(width=2.5),
                opacity=opacity
            )

            fig.add_trace(
                go.Scatter(
                    x=selected_data[['Date', 'Total']].melt(id_vars='Date')['Date'],
                    y=selected_data[['Date', 'Total']].melt(id_vars='Date')['value'],
                    line=dict(
                        color='#696969',
                        width=2,
                        dash='dash'
                    ),
                    opacity=opacity,
                    name="Total",
                    customdata=selected_data[['Date', 'Total']].melt(id_vars='Date'),
                    hovertemplate='<b>Total</b><br>Date: %{x}<br>Inflation rate: %{y:.2f}<extra></extra>',
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=selected_data[['Date', 'HICP']].melt(id_vars='Date')['Date'],
                    y=selected_data[['Date', 'HICP']].melt(id_vars='Date')['value'],
                    line=dict(
                        color='#A9A9A9',
                        width=2,
                        dash='dot'
                    ),
                    opacity=opacity,
                    name="HICP",
                    customdata=selected_data[['Date', 'HICP']].melt(id_vars='Date'),
                    hovertemplate='<b>HICP</b><br>Date: %{x}<br>Inflation rate: %{y:.2f}<extra></extra>',
                )
            )

            fig.update_xaxes(
                title_text=None,
                dtick="M3",
                tickformat='%b\n%Y',
                automargin=True
            )
            
            fig.update_yaxes(
                title_text='Inflation rate (yoy)',
                automargin=True
            ) 

        elif selected_figure == 'fig2':
            
            title_text=f'Figure 2: Expenditure categories driving inflation inequality - {country_dict[selected_country]}'

            fig = px.bar(
                selected_data,
                x='Date',
                y='Effect on inflation inequality',
                template='plotly_white',
                color='Consumption category',
                opacity=opacity,
                custom_data= selected_data
                )

            fig.update_traces(
                hovertemplate='<b>%{customdata[1]}</b><br>Date: %{x}<br>Effect on inflation inequality: %{y:.2f}<extra></extra>',
                )
            
            if quantile == 'quintile':
                fig.add_trace(
                    go.Scatter(
                        x= selected_data['Date'],
                        y= selected_data['Difference between inflation rates of bottom and top quantiles'],
                        line=dict(color='#000000'),
                        name=f'Difference between inflation rates<br>of bottom and top {quantile}s',
                        customdata= selected_data,
                        opacity=opacity,
                        hovertemplate='<b>Difference between inflation rates of bottom and top quintiles</b><br>%{x}: %{y:.2f}<extra></extra>'
                        )
                    )  

            elif quantile == 'quartile':
                fig.add_trace(
                    go.Scatter(
                        x= selected_data['Date'],
                        y= selected_data['Difference between inflation rates of bottom and top quantiles'],
                        line=dict(color='#000000'),
                        name=f'Difference between inflation rates<br>of bottom and top {quantile}s',
                        customdata= selected_data,
                        opacity=opacity,
                        hovertemplate='<b>Difference between inflation rates of bottom and top quartiles</b><br>%{x}: %{y:.2f}<extra></extra>'
                        )
                    )   
                
            fig.update_xaxes(
                title_text=None,
                dtick="M3",
                tickformat='%b\n%Y',
                automargin=True
                )
            
            fig.update_yaxes(
                title_text=None,
                automargin=True
                ) 

        elif selected_figure == 'fig3':
            title_text = f'Figure 3: Price growth and difference in importance of consumption categories - {country_dict[selected_country]}'

            fig = px.scatter(
                selected_data, 
                x='Difference in share of total expenditure', 
                y='Average inflation in 2023', 
                template='plotly_white',
                color='Main category',
                opacity=opacity,
                custom_data=selected_data
                )
            
            fig.update_traces(
                marker=dict(size=7),
                selector=dict(mode='markers'),
                hovertemplate='<b>%{customdata[1]}</b><br>Difference in consumption share: %{x:.2f}<br>Average inflation in 2023: %{y:.2f}<extra></extra>',
                line=dict(width=2.5),
                opacity=opacity
                )

            fig.update_xaxes(
                zeroline=True, 
                zerolinewidth=1,
                zerolinecolor='grey',
                automargin=True
                )

            fig.update_yaxes(
                zeroline=True, 
                zerolinewidth=1,
                zerolinecolor='grey',
                automargin=True
                )
        
        # Update title text according to selected country
        if len(selected_countries) > 1:
            # insert letter to title text atfer 8th character
            fig_letter = chr(97 + i)
            title_text = title_text[:8]+fig_letter+title_text[8:]

        # Set common layout options across figures
        fig.update_layout(
            dragmode=False,
            font_family=font_family,
            font_color= '#000000',
            margin={
                't':20,
                'b':20,
                'l':5, 
                'r':40,
            },
            legend=dict(
                itemsizing='trace'
            ),
            legend_title_text=None,
            showlegend=show_legend,
            )

        # Set layout options for mobile devices
        if is_mobile:
            # Set margins to zero
            fig.update_layout(
                margin={
                    'l':0, 
                    'r':0
                    },
                legend=dict(
                    itemsizing='trace',
                    orientation='h',
                    yanchor='top',
                    y=-0.25,
                    xanchor='center',
                    x=0.5
                    )
                )

            # Set legend position and x-axis tick format to month and year for fig 1 and 2
            if selected_figure != 'fig3':
                fig.update_xaxes(
                    dtick="M6"
                    )
                fig.update_layout(
                    margin={
                        'l':0, 
                        'r':0
                        },
                    legend=dict(
                        y=-0.15,
                        )
                    )
        
        # Add figure to the list
        figures.extend([
            html.H3(title_text,
                    style={'font-family': font_family}),
            dcc.Graph(
                id=f'figure-{selected_country}',
                figure=fig
            ),
            table
        ])

    return figures + [html.Div([
                html.P(figure_descriptions[selected_figure], style={'font-family': font_family})
            ])]

if __name__ == '__main__':
    app.run_server(debug=True)
