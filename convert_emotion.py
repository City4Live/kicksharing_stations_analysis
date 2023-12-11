import json
import geojson
from shapely import Point, Polygon

city_boundary = Polygon([[33.36265944731505,44.5725486893333],[33.47340189175782,44.4823202334386],[33.62855928525582,44.47128961813394],[33.74912639286006,44.627100100990276],[33.599715479609046,44.710383782508245],[33.446266433568184,44.66732095682761],[33.36265944731505,44.5725486893333]])

input_file = open('emotion_original.json', 'r')
input_data = json.load(input_file)

dock_types = []

def stations_filter(x):
    station_point = Point(x['lon'], x['lat'])
    return city_boundary.contains(station_point) and x['icon_code'] == 'dock_1'

filtered_stations = filter(stations_filter, input_data['body']['stations'])

features = []

for station in filtered_stations:
    station_feature = geojson.Feature('emotion_' + str(station['id']), geojson.Point([station['lon'], station['lat']]), station)
    features.append(station_feature)

features_collection = geojson.FeatureCollection(features)

output_file = open('emotion.geojson', 'w')
json.dump(features_collection, output_file)
