import json
import geojson
import numpy as np

from shapely import Polygon
from pyproj import CRS, Transformer
from sklearn.cluster import DBSCAN

emotion_data = geojson.load(open('emotion.geojson', 'r'))
yes_sharing_data = geojson.load(open('yes-sharing.geojson', 'r'))

crs_msk90_1 = CRS.from_proj4('+proj=tmerc +lat_0=0 +lon_0=32.5 +k=1 +x_0=4300000 +y_0=-9214.692 +ellps=krass +towgs84=23.57,-140.95,-79.8,0,0.35,0.79,-0.22 +units=m +no_defs')
crs_4326 = CRS.from_epsg(4326)

merged = []
merged.extend(emotion_data['features'])
merged.extend(yes_sharing_data['features'])

direct_transformer = Transformer.from_crs(crs_4326, crs_msk90_1,  always_xy=True)

# def project_to_local(x):
#     geometry = x['geometry']
#     coordinates = geometry['coordinates']
#     projected = direct_transformer.transform(coordinates[0], coordinates[1])
#     x['geometry'] = geojson.Point(projected)
#     return x

# projected = list(map(project_to_local, merged))

coords = []
objects = []
for x in merged:
    obj_coords = x['geometry']['coordinates']
    coords.append(direct_transformer.transform(obj_coords[0], obj_coords[1]))
    objects.append(x)

clustering = DBSCAN(eps=50, min_samples=1).fit(coords)

id_cluster = list(zip(clustering.labels_, objects))

clusters = {}

for group, item in id_cluster:
    if group not in clusters:
        clusters[group] = [item]
    else:
        clusters[group].append(item)

def try_get_address(cluster):
    for x in cluster:
        if 'address' in x['properties']:
            return x['properties']['address']

def process_cluster(group_item):
    i, cluster = group_item
    emotion_present = any(['emotion' in x['id'] for x in cluster])
    yes_sharing_present = any(['yes' in x['id'] for x in cluster])
    charger_present = any([('type' in x['properties'] and x['properties']['type'] == 'normal') for x in cluster])
    address = try_get_address(cluster)
    coordinates = list(map(lambda x: x['geometry']['coordinates'], cluster))
    # if len(coordinates) > 1:
    #     centroid = Polygon(coordinates).centroid
    # else:
    #     centroid = coordinates

    companies = []
    if emotion_present:
        companies.append('Э-Моушен')
    if yes_sharing_present:
        companies.append('YES Sharing')

    table_id = int(i) + 1

    def make_geometry(coords):
        if len(coords) == 1:
            return geojson.Point(coords[0])
        if len(coords) == 2:
            return geojson.LineString(coords)
        else:
            return geojson.Polygon(coords)

    return (
    {
        'Номер': table_id,
        'Координаты': '; '.join(['{:.6f}, {:.6f}'.format(x[0], x[1]) for x in coordinates]),
        'Адрес': (address if address else ''),
        'Кикшеринги': ', '.join(companies),
        'Стационарная зарядка': ('Есть' if charger_present else 'Нет')
    },
    {
        'table_id': table_id,
        'coordinates': coordinates,
        'emotion_present': emotion_present,
        'yes_sharing_present': yes_sharing_present,
        'charger_present': charger_present,
        'address': address,
        'cluster_items': cluster
    },
    geojson.Feature(table_id, make_geometry(coordinates), {'address': address})
    )

table_data = []
table_raw_data = []
clustered_features = []

for item in clusters.items():
    td_item, trd_item, cf_item = process_cluster(item)
    table_data.append(td_item)
    table_raw_data.append(trd_item)
    clustered_features.append(cf_item)

json.dump(table_data, open('table_data.json', 'w', encoding='utf8'), ensure_ascii=False)
json.dump(table_raw_data, open('table_raw_data.json', 'w', encoding='utf8'), ensure_ascii=False)
geojson.dump(geojson.FeatureCollection(clustered_features), open('clustered_features.geojson', 'w', encoding='utf8'), ensure_ascii=False)

