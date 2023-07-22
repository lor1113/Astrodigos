import networkx
import csv
import json

metadata = {"trig": [30004981, 30000163, 30003464, 30005330, 30002557, 30003856, 30002645, 30003076, 30045338, 30045345,
                     30000182,
                     30002771, 30001400, 30002760, 30003073, 30001401, 30000205, 30004244, 30001685, 30002795, 30001358,
                     30001390,
                     30001391, 30045354, 30002575, 30001447, 30001383, 30045331],
            "edencom": [30004090, 30000105, 30002704, 30002266, 30003398, 30003515, 30005252, 30002253, 30003556,
                        30003885, 30005251,
                        30000113, 30002530, 30003548, 30002700, 30003397, 30003574, 30004973, 30004250, 30004305,
                        30003392, 30002651,
                        30003541, 30002386, 30004084, 30004248, 30004100, 30000188, 30004141, 30000004, 30003883,
                        30005260, 30003490,
                        30004103, 30002242, 30002986, 30003539, 30002665, 30005058, 30003050, 30004992, 30003573,
                        30002662, 30002251,
                        30045322, 30000005, 30002243, 30004150, 30005052, 30002385, 30000118, 30003553, 30003514,
                        30003854, 30002644,
                        30003480, 30004301, 30002051, 30003824, 30005086, 30000012, 30003919, 30002724, 30003478,
                        30003908, 30002048,
                        30000109, 30005267, 30003809, 30005034, 30004108, 30003904, 30001660, 30002513, 30005074,
                        30004284, 30000102,
                        30004256, 30003078, 30003463, 30004287, 30004263, 30004254, 30003918, 30004257, 30003900,
                        30003587, 30005213,
                        30002397, 30000048, 30003788, 30000062, 30001696, 30000060, 30005308, 30004295, 30003823,
                        30005066, 30004999,
                        30003558, 30003482, 30003061, 30005263, 30005236, 30001376, 30003460, 30003058, 30004302,
                        30002506, 30003088,
                        30001718, 30004978, 30002772, 30002239, 30000160, 30003829, 30002241, 30003894, 30003090,
                        30005255, 30003074,
                        30003931, 30005222, 30004231, 30002999, 30004268, 30005209, 30005219, 30003794, 30005334,
                        30003932, 30003481,
                        30002755, 30004289, 30003927, 30005284],
            "hs": [],
            "ls": [],
            "ns": []}
system_metadata = {}
system_security = {}
eve_map = networkx.Graph()
csv_map = open('fuzzwork_sde/mapSolarSystems.csv', 'r')
csv_reader = csv.reader(csv_map, delimiter=',')
next(csv_reader)
for row in csv_reader:
    system = float(row[21])
    eve_map.add_node(int(row[2]))
    system_security[str(row[2])] = system
    system = {
        "region_id": int(row[0]),
        "constellation_id": int(row[1]),
        "id": int(row[2]),
        "name": row[3],
        "security": float(row[21]),
    }
    system_metadata[str(row[2])] = system
csv_map.close()

csv_jump_map = open('fuzzwork_sde/mapSolarSystemJumps.csv', 'r')
csv_reader = csv.reader(csv_jump_map, delimiter=',')
next(csv_reader)
for row in csv_reader:
    eve_map.add_edge(int(row[2]), int(row[3]), weight=0.01)
csv_jump_map.close()

remove_list = []

paths = networkx.single_source_shortest_path(eve_map, 30003014)
for node in eve_map.nodes():
    if node not in paths:
        remove_list.append(node)

for node in remove_list:
    eve_map.remove_node(node)

for node in eve_map.nodes():
    if system_security[str(node)] < 0.0:
        metadata["ns"].append(str(node))
    elif system_security[str(node)] < 0.45:
        metadata["ls"].append(str(node))
    elif system_security[str(node)] > 0.45:
        metadata["hs"].append(str(node))
    else:
        print("Something went wrong!")
        print(node)

metadata["trig"] = [str(x) for x in metadata["trig"]]
metadata["edencom"] = [str(x) for x in metadata["edencom"]]

networkx.write_multiline_adjlist(eve_map, "static/eve_map_base.adjlist")
json.dump(metadata, open("static/metadata.json", "w"))
json.dump(system_metadata, open("static/system_metadata.json", "w"))
