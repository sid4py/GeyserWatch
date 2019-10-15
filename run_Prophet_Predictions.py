import json
import requests

import pandas as pd
from pandas.io.json import json_normalize

import datetime
import pytz 

import pickle

response = requests.get('https://www.geysertimes.org/api/v5/entries_latest/old+faithful;beehive;daisy;riverside;grand;castle;great+fountain')

if response.status_code != 200:
    print('GeyserTimes API down !!')
    exit()

df = json_normalize(response.json()['entries'])

df['utc_datetime'] = pd.to_datetime(df['time'],unit='s')
cols = ['eruptionID', 'geyserID', 'time', 'hasSeconds', 'exact', 'ns',
       'ie', 'E', 'A', 'wc', 'ini', 'maj', 'min', 'q', 'duration',
       'durationSec', 'durationRes', 'durationMod', 'entrant', 'entrantID',
       'observer', 'comment', 'timeUpdated', 'timeEntered', 'timezone']
df.drop(columns=cols, inplace=True)

geysers = ['Old Faithful', 'Beehive', 'Daisy', 'Riverside', 'Grand', 'Castle', 'Great Fountain']

modeldict = {'Old Faithful':'m_oldfaithful_model.pckl',
             'Beehive':'m_beehive_model.pckl',
             'Daisy':'m_daisy_model.pckl',
             'Riverside':'m_riverside_model.pckl',
             'Grand':'m_grand_model.pckl',
             'Castle':'m_castle_model.pckl',
             'Great Fountain':'m_greatfountain_model.pckl'
            }

curr_time = datetime.datetime.now()
#convtz = pytz.timezone('US/Mountain')
#curr_time = curr_time.astimezone(convtz)
todays_date = curr_time.date()
seventh_day = todays_date + datetime.timedelta(days=7)

primary_forecast_list = []

for geyser in geysers:
    with open(modeldict[geyser], 'rb') as fin:
        model = pickle.load(fin)
    ts = df.loc[df['geyser'] == geyser]['utc_datetime'].iloc[0]
    todays_date = curr_time.date()
    print(ts)
    while todays_date < seventh_day:
        pdf = pd.DataFrame()
        pdf = pd.DataFrame([[ts]], columns=['ds'])
        forecast_df = model.predict(pdf)
        forecast_df['geyser'] = geyser
        cols = ['geyser', 'ds', 'yhat_lower', 'yhat_upper', 'yhat']
        forecast_df = forecast_df[cols]
        l = forecast_df.values.tolist()
        primary_forecast_list.append(l[0])
        ts = ts + datetime.timedelta(minutes=abs(forecast_df.loc[0,'yhat']))
        ts = ts.replace(second=0, microsecond=0)
        todays_date = ts.date()
        print("Next eruption of", geyser, "is at", ts, "and new date is", todays_date)
        #break

#print(primary_forecast_list)
predictions_df = pd.DataFrame(primary_forecast_list, columns = ['geyser', 'ds', 'yhat_lower', 'yhat_upper', 'yhat'])
predictions_df.sort_values(by=['ds'], inplace=True)
predictions_df.to_csv('predictions3.csv', index=False)