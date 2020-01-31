import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import dash_table
import base64
import pandas as pd
import datetime
import pytz 
import time


# ----- Reading in the predictions csv and adding required columns -----
df = pd.read_csv('predictions.csv')

df['ds'] = pd.to_datetime(df['ds'])
df['MTN_datetime'] = df['ds'].dt.tz_localize('utc').dt.tz_convert('US/Mountain')
df['date'] = [d.date() for d in df['MTN_datetime']]
df['time'] = [d.time() for d in df['MTN_datetime']]
df['time_window'] = (df['yhat_upper'] - df['yhat_lower'])/2
df['time_window'] = [int(d) for d in df['time_window']]
df['epoch'] = [datetime.datetime.timestamp(d) for d in df['ds']]
df['epoch_err'] = [datetime.timedelta(minutes=j).total_seconds() for j in df['time_window']]
df['hover_text'] = [str(df.loc[i,'time'])[:-3] + ' ± ' + str(df.loc[i,'time_window']) + ', ' + str(df.loc[i,'geyser']) for i in df.index]

# ----- Generating slider marks list -----
marks = df['date'].unique()

# ----- Getting current time and date for Mountain time -----
local_curr_time = datetime.datetime.now()
mtn_tz = pytz.timezone('US/Mountain')
mtn_time_now = local_curr_time.astimezone(mtn_tz)
todays_date = mtn_time_now.date()
# Setting slider value to always initialize at todays date
for i in range(len(marks)):
	if marks[i] == todays_date:
		sliderval = i

# ----- Getting UTC time for calculating time difference value (to take care of Daylight Savings Time) -----
utc_tz = pytz.timezone('UTC')
utc_time_now = local_curr_time.astimezone(utc_tz)
# converting to epoch to get integer difference in seconds
t_diff = time.mktime(utc_time_now.timetuple()) - time.mktime(mtn_time_now.timetuple())


image_directory = '/home/ubuntu/geyserwatch_webapp'
list_of_images = ['Old Faithful Area Map','Geyser Hill Group','Lower Midway Upper Basin','Old Faithful Area Geysers']
static_image_route = '/static/'


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

app.layout = html.Div([
				html.H1('Geyser Watch', style={'textAlign':'center'}),
				html.Div([
					html.H4('Predicting Geyser Eruptions at Yellowstone National Park', style={'textAlign':'center'}),
					html.Hr(),
					html.Div(
						dcc.Markdown('''
						* All times in US/Mountain timezone
						* Hover over predictions to see more information, you can also interact by zooming in/out or using top-right controls.
						* Double click anywhere to reset view.
						* Slider updates timeline and the Predictions table below
						'''),style={'padding-left':'8%'}
					),
					dcc.Graph(
						id='graph-with-slider',
					),
					html.Div(
						[dcc.Slider(
						id='day-slider',
						min=0,
						max=len(df['date'].unique())-1,
						value=sliderval,
						step=1,
						marks={i: str(marks[i]) for i in range(len(marks))})
						],style={'width':'50%', 'padding-left':'25%', 'padding-right':'25%', 'padding-top':'1%'}
					),
					html.Div('',style={'padding-top':'2%'}),
					html.Div([dcc.Markdown('''Move slider right to see future predictions''', style={'textAlign':'center'})]),
					html.Hr()
				], className="row"),

				html.Div([

					html.Div([
						html.Div(
							dcc.Markdown('''
								Time Window represents uncertainty in prediction in minutes  \n
								To be interpreted as : "*geyser* will erupt at *time* ± *time_window*"  \n
								Example: Old Faithful will erupt at 8:45 ± 5 minutes
							''')
						),
						html.H4('Predictions'),
						dash_table.DataTable(
							id='datatable',
							columns=[{"name": i, "id": i} for i in ['geyser','date','time','time_window']],
							style_table={'maxHeight': '700px','overflowY': 'scroll'}
						)
					], className="six columns", style={'width':'40%', 'display':'inline-block', 'padding-left':'3%'}),

					html.Div([
						html.Div(
							dcc.Markdown('''Select Area Maps from the drop-down menu to plan your itinerary''')
						),
						html.H4('Geyser Locations'),
						dcc.Dropdown(
								id='image-dropdown',
								options=[{'label': i, 'value': i} for i in list_of_images],
								value=list_of_images[0]
						), html.Img(id='image', style={'width':'500px'})
					], className="six columns", style={'width':'40%', 'display':'inline-block', 'float':'top', 'float':'right', 'padding-right':'3%'}),

				], className="row"),

				html.Hr(),

				html.H5('Thank you for visiting Geyser Watch', style={'textAlign':'center'}),

			])		

@app.callback(
	Output('image', 'src'),
	[Input('image-dropdown', 'value')])
def update_image_src(value):
	image_filename = image_directory + static_image_route + value.replace(' ','_') + '.png'
	encoded_image = base64.b64encode(open(image_filename, 'rb').read())
	return 'data:image/png;base64,{}'.format(encoded_image.decode())

@app.callback(
	[Output('graph-with-slider', 'figure'),
	Output('datatable', 'data')],
	[Input('day-slider', 'value')])
def update_figure(selected_day):
	selected_date = marks[selected_day]

	# ----- Selecting data for specific date in a new dataframe -----
	filtered_df = df[df.date == selected_date]
	filtered_df.sort_values(by=['geyser', 'time'], inplace=True)

	# Creating a geyser list
	geyser_list = filtered_df['geyser'].unique()

	# ----- Converting selected_date into UTC epoch -----
	dtts = selected_date.timetuple() 
	ts = time.mktime(dtts)
	# Converting epoch from UTC to Mountain Time
	ts = ts + t_diff #21600 #25200

	# Making xaxis range
	x_range = []
	x_range.append(ts)
	x_range.append(ts + 86400) # Adding 24 hours to range - i.e. 86400 seconds
	# The x axis ranges now from 0000 hrs on selected date to midnight of selected date

	# ----- Creating a fixed tick values list -----
	tickval_list=[]
	for i in range(24):
	    tickval_list.append(ts)
	    ts = ts + 3600
	tickval_list.append(ts)

	# ----- Creating a fixed tick text list -----
	ticktext_list = []
	for i in tickval_list:
	    i = i - t_diff #25200 #21600 # Converting from Mountain time back into UTC - because data points are in UTC epoch
	    t = str(datetime.datetime.fromtimestamp(i).time())
	    ticktext_list.append(t[:-3])

	# ----- Getting Mountain time for every date that is selected -----
	tz = pytz.timezone('US/Mountain')
	tn_str = str(selected_date)+' '+str(datetime.datetime.now().astimezone(tz).replace(second=0,microsecond=0).time())
	tn_dt_obj = datetime.datetime.strptime(tn_str, '%Y-%m-%d %H:%M:%S')
	time_now = tn_dt_obj.timestamp() + t_diff #25200 #21600
	time_list = [time_now]*7
	tn_hover = str(tn_dt_obj.time())[:-3]

	# ----- Plotting Traces -----
	trace1 = go.Scatter(
				y=filtered_df.geyser,
				x=filtered_df['epoch'],
				error_x={'type':'data', 'array':filtered_df.epoch_err, 'thickness':6, 'width':0, 'visible':True},
				name='Prediction',
				mode='markers',
				marker={'size': 12},
				hovertext=filtered_df.hover_text,
				hoverinfo='text'
			)

	trace2 = go.Scatter(
				y=geyser_list,
				x=time_list,
				mode='lines',
				name='Current Time: ' + tn_hover,
				marker={'size': 2},
				hovertext='Current Time '+ tn_hover, hoverinfo='text'
			)

	data = [trace1,trace2]

	layout = go.Layout(
				margin={'l': 160, 'b': 30, 't': 0, 'r': 100},
				height=300,
				xaxis={
					'title':'Time (Hrs)',
					'showgrid':False,
					'showticklabels':True,
					'tickmode':'array',
					'tickvals':tickval_list,
					'ticktext':ticktext_list
				},
				yaxis={'showgrid':True},
				title={
					'text':('Predicted Geyser Eruptions for ' + str(selected_date)),
					'x':0.5,
					'y':1,
					'xanchor':'center',
					'yanchor':'top',
					'pad':{'t':30}
				},
				titlefont={'size':18},
				legend=dict(x=-0.1, y=1.3)
			)

	fig = go.Figure(data=data, layout=layout)
	fig.update_xaxes(range=x_range, tickangle=45, tickfont={'size':14}, showline=True, linewidth=1, linecolor='black', mirror=True, title_font={'size':18})
	fig.update_yaxes(tickfont={'size':16})

	filcols = ['geyser','date','time','time_window']
	return fig, filtered_df[filcols].to_dict('records')


if __name__ == '__main__':
	app.run_server(debug=True)
