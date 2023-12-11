import geojson
from shapely import Polygon, Point

input_file = open('yes-sharing_edited.geojson')
input_data = geojson.load(input_file)

def map_features(feature):
    geometry = feature['geometry']
    feature['id'] = 'yes_' + str(feature['properties']['id'])
    if geometry['type'] == 'Polygon':
        polygon = Polygon(geometry['coordinates'][0])
        feature['properties']['origin_geometry'] = geometry
        feature['geometry'] = geojson.Point([polygon.centroid.x, polygon.centroid.y])
        return feature
    return feature

mapped_features = list(map(map_features, input_data['features']))

output_file = open('yes-sharing.geojson', 'w')
geojson.dump(geojson.FeatureCollection(mapped_features), output_file)

