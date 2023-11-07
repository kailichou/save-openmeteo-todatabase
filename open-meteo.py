# retrieve historical meteo data, no auth required
import requests
import json 
import openmeteo_requests
import requests_cache
from retry_requests import retry 
import dbEngine
import pandas as pd

database = "test"





api_url = "https://archive-api.open-meteo.com/v1/"
sample_url = "https://api.open-meteo.com/v1/forecast?latitude=40.7143&longitude=-74.006&hourly=temperature_2m&daily=uv_index_max&timezone=America%2FNew_York"
sample_url2 = "https://archive-api.open-meteo.com/v1/era5?latitude=52.52&longitude=13.41&start_date=2023-01-01&end_date=2023-03-31&hourly=temperature_2m"
#r = requests.get(sample_url2)


# setup the open-meteo api client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache',expire_after = 60)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)


# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://archive-api.open-meteo.com/v1/archive"

# HTTP request
params = {
        "latitude":40.7143,
        "longitude":-74.006,
        "start_date":"2023-04-01",
        "end_date":"2023-04-30",
        "hourly":"temperature_2m"
        }

responses = openmeteo.weather_api(url, params=params)


# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
response = responses[0]
print(f"Coordinates {response.Latitude()}°E {response.Longitude()}°N")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")



# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s"),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s"),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}
hourly_data["temperature_2m"] = hourly_temperature_2m

hourly_dataframe = pd.DataFrame(data = hourly_data)
#print(hourly_dataframe)
#with open("weather2023.json",'w') as f:
#    f.write(r.text)


# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s"),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s"),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}
hourly_data["temperature_2m"] = hourly_temperature_2m
hourly_dataframe = pd.DataFrame(data = hourly_data)
#print(hourly_dataframe)


try:	
	
	# start db engine
	engine = dbEngine.start_engine(database="test")
	with engine.connect() as conn, conn.begin():
		# save data into database
		hourly_dataframe.to_sql("city_meteo_api", conn, if_exists="append")
		conn.close()
except Exception as e:
	print("error: \n", e)

