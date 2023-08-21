import numpy as np
import pandas as pd
import os
from datetime import date, timedelta

from urllib.request import urlopen
from io import BytesIO
from zipfile import ZipFile
import shutil

import time
from inspect import getsourcefile
from os.path import abspath

import plotly.express as px
import plotly.graph_objects as go
import chart_studio
import chart_studio.plotly as py

import geopandas as gpd

mapbox_access_token = os.environ['MAPBOX_KEY']
username = 'markedwardson' # your plotly username
api_key = os.environ["PLOTLY_API_KEY"] # your plotly api key - go to profile > settings > regenerate key
chart_studio.tools.set_credentials_file(username=username, api_key=api_key)

#set active directory to file location
directory = abspath(getsourcefile(lambda:0))
#check if system uses forward or backslashes for writing directories
if(directory.rfind("/") != -1):
    newDirectory = directory[:(directory.rfind("/")+1)]
else:
    newDirectory = directory[:(directory.rfind("\\")+1)]
os.chdir(newDirectory)

#Generic function to create a heatmap
def create_heatmap(stops,title = ""):
    fig = px.density_mapbox(stops, lat='stop_lat', lon='stop_lon', z='count', radius=15,
                            center=dict(lat=0, lon=180), zoom=0,
                            mapbox_style="stamen-terrain",
                            range_color=[0, 800],
                            )

    fig.update_layout(
            title = title,
            title_x = 0.5,
            #increase title size
            title_font_size=20,
            #rename colorbar
            coloraxis_colorbar=dict(
                title="Stop count"
            ),
            margin=dict(l=0, r=0, t=35, b=0),
            
            hovermode='closest',
            mapbox=dict(
                accesstoken=mapbox_access_token,
                style = "dark",
                bearing=0,
                center=go.layout.mapbox.Center(
                    lat=np.average(stops["stop_lat"]),
                    lon=np.average(stops["stop_lon"])
                ),
                pitch=0,
                zoom=10
        
        ))
    
    return fig


def main():
    #for each folder in GTFS
    for name in ['Calgary','London', 'Translink', 'TTC', 'Victoria']:
        print(name)
        folder = "GTFS/{}/".format(name)

        today = date.today()
        next_tuesday = today + timedelta((1-today.weekday()) % 7)
        
        next_tuesday = pd.to_datetime(next_tuesday)

        print(next_tuesday)

        calendar = pd.read_csv(folder+"calendar.csv")
        calendar_dates = pd.read_csv(folder+"calendar_dates.csv")
        trips = pd.read_csv(folder+"trips.csv")
        stop_times = pd.read_csv(folder+"stop_times.csv")
        stops = pd.read_csv(folder+"stops.csv")

        #convert to datetime
        calendar['start_date'] = pd.to_datetime(calendar['start_date'], format='%Y%m%d')
        calendar['end_date'] = pd.to_datetime(calendar['end_date'], format='%Y%m%d')
        calendar_dates['date'] = pd.to_datetime(calendar_dates['date'], format='%Y%m%d')

        #filter calendar to see if it's active on next tuesday
        calendar = calendar[(calendar['start_date'] <= next_tuesday) & (calendar['end_date'] >= next_tuesday)]

        calendar = calendar[calendar.tuesday == 1]
        #now compare against calendar_dates for any date-specific exceptions
        unique_service_codes = calendar['service_id'].unique()

        #for row in calendar_dates
        #check if 'date' is the same as next_tuesday
        for index, row in calendar_dates.iterrows():
            if row['date'] == next_tuesday:
                print("yes")
                if row['exception_type'] == 2:
                    #remove service_id from unique_service_codes
                    unique_service_codes = unique_service_codes[unique_service_codes != row['service_id']]
                if row['exception_type'] == 1:
                    #add service_id to unique_service_codes
                    unique_service_codes = np.append(unique_service_codes, row['service_id'])

        #unique_service_codes is now a list of service codes that are a) valid on next_tuesday and b) not cancelled on next_tuesday
        print(unique_service_codes)

        #filter trips for only the service codes in unique_service_codes
        trips = trips[trips['service_id'].isin(unique_service_codes)]

        #filter stop_times for only the trips in trips
        stop_times = stop_times[stop_times['trip_id'].isin(trips['trip_id'])]

        def fix_hour(hour_str):
            x = hour_str.find(':')
            hour = int(hour_str[:x])
            if hour >= 24:
                hour -= 24
            return(f'{hour:02d}{hour_str[x:]}')

        # Apply the fix_hour function to arrival_time
        stop_times['arrival_time'] = stop_times['arrival_time'].apply(fix_hour)

        stop_times['arrival_time'] = pd.to_datetime(stop_times['arrival_time'])

        print("Fixed stop data")

        def lookup(stop_id):
            #count how many times stop_id appears in stop_times['stop_id']
            count = len(stop_times[stop_times["stop_id"] == stop_id])
            return(count)

        stops['count'] = stops['stop_id'].apply(lookup)

        #export to csv
        stops.to_csv("stop activity counts csvs/{} stops.csv".format(name))

        fig = create_heatmap(stops, name + " Stop Activity")
        fig.write_html("docs/" + name + " stop activity.html")

main()