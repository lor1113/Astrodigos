import networkx
import csv
import json

metadata = {}
eve_map = networkx.Graph()
csv_map = open('fuzzwork_sde/mapSolarSystems.csv', 'r')
csv_reader = csv.reader(csv_map, delimiter=',')
next(csv_reader)
for row in csv_reader:
    system = {
        "region_id": int(row[0]),
        "constellation_id": int(row[1]),
        "id": int(row[2]),
        "name": row[3],
        "security": float(row[21]),
    }
    eve_map.add_node(int(row[2]))
    metadata[int(row[2])] = system

csv_map.close()
csv_jump_map = open('fuzzwork_sde/mapSolarSystemJumps.csv', 'r')
csv_reader = csv.reader(csv_jump_map, delimiter=',')
next(csv_reader)
for row in csv_reader:
    eve_map.add_edge(int(row[2]), int(row[3]))

print(eve_map.number_of_nodes())

remove_list = []
for node in eve_map.nodes():
    if eve_map.degree(node) == 0:
        remove_list.append(node)

for node in remove_list:
    eve_map.remove_node(node)

paths = networkx.single_source_shortest_path(eve_map, 30000142)
for node in eve_map.nodes():
    if node not in paths:
        remove_list.append(node)

print(eve_map.number_of_nodes())

networkx.write_adjlist(eve_map, 'static/eve_map.adjlist')
json.dump(metadata, open('static/eve_map_metadata.json', 'w'))