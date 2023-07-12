import networkx
import csv
import copy

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
    metadata[str(row[2])] = system
csv_map.close()

csv_jump_map = open('fuzzwork_sde/mapSolarSystemJumps.csv', 'r')
csv_reader = csv.reader(csv_jump_map, delimiter=',')
next(csv_reader)
for row in csv_reader:
    eve_map.add_edge(int(row[2]), int(row[3]), weight=0)
csv_jump_map.close()

remove_list = []
for node in eve_map.nodes():
    if eve_map.degree(node) == 0:
        remove_list.append(node)

for node in remove_list:
    eve_map.remove_node(node)
remove_list = []

paths = networkx.single_source_shortest_path(eve_map, 30003014)
for node in eve_map.nodes():
    if node not in paths:
        remove_list.append(node)

for node in remove_list:
    eve_map.remove_node(node)

networkx.write_multiline_adjlist(eve_map, "static/eve_map_base.adjlist")

eve_map_avoid_ls = copy.deepcopy(eve_map)

for node in eve_map_avoid_ls.nodes():
    if metadata[str(node)]["security"] < 0.45:
        for edge in eve_map_avoid_ls.edges(node):
            eve_map_avoid_ls[edge[0]][edge[1]]["weight"] = 10000


networkx.write_multiline_adjlist(eve_map_avoid_ls, "static/eve_map_avoid_ls.adjlist")

eve_map_avoid_hs = copy.deepcopy(eve_map)

for node in eve_map_avoid_hs.nodes():
    if metadata[str(node)]["security"] >= 0.45:
        for edge in eve_map_avoid_hs.edges(node):
            eve_map_avoid_hs[edge[0]][edge[1]]["weight"] = 10000

networkx.write_multiline_adjlist(eve_map_avoid_hs, "static/eve_map_avoid_hs.adjlist")