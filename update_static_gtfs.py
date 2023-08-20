import os
import time
from urllib.request import urlopen
from io import BytesIO
from zipfile import ZipFile
import shutil

#gtfs datasets

urls = {"Victoria": "http://victoria.mapstrat.com/current/google_transit.zip",
        "TTC": "http://opendata.toronto.ca/toronto.transit.commission/ttc-routes-and-schedules/OpenData_TTC_Schedules.zip",
        "Translink": "https://transitfeeds.com/p/translink-vancouver/29/latest/download",
        "Milan": "https://dati.comune.milano.it/gtfs.zip",
        "London": "https://transitfeeds.com/p/london-transit-commission/831/latest/download"}

#for name in urls.keys():
for name in ["London"]:
    print("Downloading data for " + name + "...")
    try:
        shutil.rmtree("GTFS/"+name)
    except:
        print("No previous data for " + name + " found.")
        
    http_response = urlopen(urls[name])
    zipfile = ZipFile(BytesIO(http_response.read()))
    zipfile.extractall(path="GTFS/"+name)

    print("Renaming files...")
    loc = "GTFS/"+name + "/"
    for filename in os.listdir(loc):
        print(filename)
        newname = filename[:-3]+'csv'
        os.rename(loc+filename,loc+newname)
        time.sleep(.5)

print("Done.")