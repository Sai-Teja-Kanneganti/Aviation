import socket
import sys
import json
import pandas as pd
import datetime
from json import dumps
import numpy as np
import string
import random
from subprocess import Popen

def id_generator(size=3, chars=string.ascii_uppercase + string.digits):
   return ''.join(random.choice("0123456789ABCDEF") for _ in range(size))

Flights = {}

def get_color (Flight_No):
    if Flight_No == '2500000':
        color = "#FF0000"
    else:
        color = "#0000FF"
    return color

def df_to_geojson_point(df, properties, lat='Latitude', lon='Longitude'):
    geojson = {'type':'FeatureCollection', 'features':[]}
    for _, row in df.iterrows():
        feature = {'type':'Feature',
                   'properties':{},
                   'geometry':{'type':'Point',
                               'coordinates':[]}}
        feature['geometry']['coordinates'] = [row[lon],row[lat]]
        for prop in properties:
            #print("Flight_No in Geo Json =",row["Flight_No"])
            feature['properties']['marker-color'] = get_color(row['Flight_No'])

            feature['properties'][prop] = row[prop]
        geojson['features'].append(feature)
    return geojson

def df_to_geojson_icon(df, properties, lat='Latitude', lon='Longitude'):
    geojson = {'type':'FeatureCollection', 'features':[]}
    for _, row in df.iterrows():
        feature = {'type':'Feature',
                   'properties':{},
                   'geometry':{'type':'Point',
                               'coordinates':[]}}
        feature['geometry']['coordinates'] = [row[lon],row[lat]]
        for prop in properties:
            #print("Flight_No in Geo Json =",row["Flight_No"])
            #feature['properties']['marker-color'] = get_color(row['Flight_No'])

            feature['properties']['title'] = row['Flight_No']
            feature['properties']['icon'] = "airplane"


            #feature['properties'][prop] = row[prop]
        geojson['features'].append(feature)
    return geojson

def df_to_geojson(df, properties, lat='Latitude', lon='Longitude'):
    geojson = {'type': 'FeatureCollection', 'features': []}
    for index, row in df.iterrows():
        try:
            current_row = row
            next_row = df.iloc[index + 1]
            # earlier_row =  df.iloc[index - 1]
            if current_row['Flight_No'] == next_row['Flight_No']:
                begin_cord = [current_row["Longitude"], current_row["Latitude"]]
                end_cord = [next_row["Longitude"], next_row["Latitude"]]
                feature = {'type': 'Feature',
                           'properties': {},
                           'geometry': {'type': 'LineString',
                                        'coordinates': []},
                           'paint': {"line-color": get_color(current_row['Flight_No']),
                                     "line-width": 8}}
                feature['geometry']['coordinates'] = [begin_cord, end_cord]
                for prop in properties:
                    feature['properties'][prop] = row[prop]
                geojson['features'].append(feature)

            else:
                #print("In else loop")
                temp_row = current_row
                temp_index = index
                while True:  # for index, row in df.iterows(): # once check even adding index error
                    temp_index = temp_index - 1
                    current_row = df.iloc[temp_index]
                    if temp_row['Flight_No'] == current_row['Flight_No']:
                        # print("Now breaking")
                        # break # instead of breaking here, generate line and then break while or for loop

                        begin_cord = [current_row["Longitude"], current_row["Latitude"]]
                        end_cord = [temp_row["Longitude"], temp_row["Latitude"]]
                        feature = {'type': 'Feature',
                                   'properties': {},
                                   'geometry': {'type': 'LineString',
                                                'coordinates': []},
                                   'paint': {"line-color": get_color(current_row['Flight_No']),
                                             "line-width": 8}}
                        feature['geometry']['coordinates'] = [begin_cord, end_cord]
                        for prop in properties:
                            feature['properties'][prop] = row[prop]
                        geojson['features'].append(feature)
                        break
        except IndexError:
            pass
    return geojson

def Reduce_df(df):
    reduced_df = []
    for index, row in df.iterrows():
        current_row = row
        row_time = current_row['TimeStamp']
        #print("row time =",row_time)
        Df_Time = datetime.datetime.strptime(row_time,'%Y-%m-%d %H:%M:%S.%f')
        if datetime.datetime.now() - Df_Time < datetime.timedelta(minutes=20):
            reduced_df.append(current_row)
    df_reduced = pd.DataFrame(reduced_df).reset_index(drop=True)
    #df_reduced.sort_values(by=["Flight_No", "TimeStamp"]).reset_index(drop=True)
    #print("reduced_df=", df_reduced)
    #df_reduced.sort_values(by=["Flight_No", "TimeStamp"])

    df_less = df[df.Altitude < 1524000].reset_index(drop=True)
    df_more = df[df.Altitude >= 1524000].reset_index(drop=True)

    with open("C:/Users/CASS_4600/Desktop/Aviation/flightsgeo4.json", "w") as f1:
        #print("within geojson______________________________________________________")
        f1.write(dumps(df_to_geojson_point(df_reduced, ["Flight_No"]), indent=4, separators=(',', ': ')))

    with open("C:/Users/CASS_4600/Desktop/Aviation/flightsgeo2.json", "w") as f1:
        #print("within geojson______________________________________________________")
        f1.write(dumps(df_to_geojson(df_less, ["Flight_No"]), indent=4, separators=(',', ': ')))
    print("df_reduced()=",df_reduced)

    with open("C:/Users/CASS_4600/Desktop/Aviation/flightsgeo3.json", "w") as f1:
        #print("within geojson______________________________________________________")
        f1.write(dumps(df_to_geojson(df_more, ["Flight_No"]), indent=4, separators=(',', ': ')))
    print("df_reduced()=",df_reduced)

    df2 = df_reduced.sort_values(by=["Flight_No", "TimeStamp"], ascending=[True, False])
    df3 = df2.drop_duplicates(['Flight_No'])

    print("df_less=", df_less)
    print("df_more=", df_more)

    with open("flightsgeo1.json", "w") as f1:
        # print("again",df3)
        f1.write(dumps(df_to_geojson_icon(df3, ["Flight_No"]), indent=4, separators=(',', ': ')))
    print("reduced_df=", df_reduced)
    return df_reduced

switch = input('Enter 0 for previous data & 1 for live')
#print ("switch =",switch )
#print (type(switch))

if switch == '0':

    LatString = "[-97,35]"

    with open(r"map.template", "r") as f:
        html_text = f.read()

    new_text = html_text.replace("<<<thisismylatlonplaceholder>>>", LatString)

    with open(r"map.html", "w") as f:
        f.write(new_text)

    p = Popen("localhost.bat",cwd=r"C:\Users\CASS_4600\Desktop\Aviation")
    stdout, stderr = p.communicate()

    print ("In if loop")
    df = pd.read_csv("Data4.csv")
    df = df.drop_duplicates(subset=['Flight_No', 'Longitude', 'Latitude'])

    df = df.sort_values(by=["Flight_No", "TimeStamp"])
    #print("data=", df)

    df_less = df[df.Altitude < 1524000].reset_index(drop=True)
    df_more = df[df.Altitude >= 1524000].reset_index(drop=True)

    print("df_less=", df_less)
    print("df_more=", df_more)

    df2 = df.sort_values(by=["Flight_No", "TimeStamp"], ascending=[True, False])
    df3 = df2.drop_duplicates(['Flight_No'])

    with open("flightsgeo2.json", "w") as f1:
        f1.write(dumps(df_to_geojson(df_less, ["Flight_No"]), indent=4, separators=(',', ': ')))

    with open("flightsgeo3.json", "w") as f1:
        f1.write(dumps(df_to_geojson(df_more, ["Flight_No"]), indent=4, separators=(',', ': ')))

    with open("flightsgeo4.json", "w") as f1:
        f1.write(dumps(df_to_geojson_point(df, ["Flight_No"]), indent=4, separators=(',', ': ')))

    with open("flightsgeo1.json", "w") as f1:
        # print("again",df3)
        f1.write(dumps(df_to_geojson_icon(df3, ["Flight_No"]), indent=4, separators=(',', ': ')))


else:
    print ("In else loop")
    HOST = "192.168.1.25"   # Client IP address
    PORT = 8081             # Client Listening port

    server = ("192.168.1.24",8081)  # Ping station IP address and port

    S = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # socket.SOCK_DGRAM for UDP packets
    print("Socket Created")

    S.bind((HOST, PORT))
    print("Socket Bind Complete")
    print("started listening on",HOST,":",PORT)

    f = open("Data.csv", 'w')
    f.write("Flight_No,Longitude,Latitude,Altitude,TimeStamp\n")
    print("File opened")
    f.close()

    x = 0
    y = 0

    # While receiving packets
    while True:

        df = pd.read_csv("Data.csv")
        df = df.drop_duplicates(subset=['Flight_No', 'Longitude', 'Latitude'])

        df = df.sort_values(by=["Flight_No", "TimeStamp"])
        #Reduce_df(df)

        data, addr = S.recvfrom(1024) #recvfrom  for UDP packets # data is bytes
        print(data)
        json_parsed = json.loads(data.strip()) # convert into a dictionary # json_parsed is dictionary
        #print(json_parsed)

        for key, value in dict.items(json_parsed):  # helps to deal only with aircraft messages
            if x == 0:
                if key.startswith("status"): # can keeep if above this
                    for item in json_parsed['status']:
                        #print("item=",item)
                        for key, value in dict.items(json_parsed):
                            #print("key",key)
                            #print("value",value)
                            #for each in value:
                            #    for key1, value1 in dict.items(each):
                            if item.startswith("pingStationLatDD"):
                                #print("item=",item)
                                Ping_Latitude = value["pingStationLatDD"]
                                print("Ping Latitude = ",Ping_Latitude)
                            if item.startswith("pingStationLonDD"):
                                Ping_Longitude = value["pingStationLonDD"]
                                print("Ping Longitude = ", Ping_Longitude)
                                #print (type(Ping_Longitude))
                                if Ping_Longitude == 0.0:
                                    LatString = "[-97,35]"
                                    #print(type(LatString))
                                    print(LatString)
                                else:
                                    LatString = '['
                                    LatString += str(Ping_Longitude)
                                    LatString += ','
                                    LatString += str(Ping_Latitude)
                                    LatString += ']'
                                    print(LatString)

                                with open(r"map.template", "r") as f:
                                    html_text = f.read()

                                p = Popen("adsb_run2.bat", cwd=r"C:\Users\CASS_4600\Desktop\Aviation")
                                stdout, stderr = p.communicate()

                                new_text = html_text.replace("<<<thisismylatlonplaceholder>>>", LatString)

                                with open(r"map.html", "w") as f:
                                    f.write(new_text)

                                x = x +1

            elif key.startswith("aircraft"):
                for item in json_parsed['aircraft']:
                    for key, value in dict.items(json_parsed):
                        # print(key)
                        # print(value)
                        for each in value:
                            # print(each)
                            count = 0
                            for key1, value1 in dict.items(each):
                                if key1.startswith("icaoAddress"):
                                    count = count + 1
                                if key1.startswith("lonDD"):
                                    count = count + 1
                                if key1.startswith("latDD"):
                                    count = count + 1
                                if key1.startswith("altitudeMM"):
                                    count = count + 1
                            if count == 4:
                                with open("Data.csv", 'a+') as f:
                                    f.write("{0},{1},{2},{3},{4}\n".format(str(item["icaoAddress"]), str(item["lonDD"]),
                                                                       str(item["latDD"]), str(item["altitudeMM"]), datetime.datetime.now()))
                                df = pd.read_csv("Data.csv")
                                df = df.drop_duplicates(subset=['Flight_No', 'Longitude', 'Latitude'])
                                #print("DataFrame:", df)
                                df = df.sort_values(by=["Flight_No", "TimeStamp"])
                                Reduce_df(df)

                                #with open("C:/Users/admin/PycharmProjects/Aviation/flightsgeo.json", "w") as f1:
                                    # print("within geojson______________________________________________________")
                                    #f1.write(dumps(df_to_geojson(df_reduced, ["Flight_No"]), indent=4, separators=(',', ': ')))

    S.close()
