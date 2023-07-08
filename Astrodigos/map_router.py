import networkx
import msgpack
import time

eve_map = networkx.read_multiline_adjlist("static/eve_map.adjlist")
map_metadata = msgpack.unpack(open("static/eve_map_metadata.msgpack", "rb"))


def cycle_post_process(cycle_in, start):
    dummy = cycle_in.index("dummy")
    cut1 = cycle_in[:dummy]
    cut2 = cycle_in[dummy + 1:]
    cut2.pop()
    cut1.reverse()
    cut2.reverse()
    out = cut1 + cut2
    if out[-1] == start:
        out.reverse()
    return out


def array_to_pairs(array):
    pairs = []
    for i in range(len(array) - 1):
        pairs.append((array[i], array[i + 1]))
    return pairs


def remove_duplicates(input_array):
    seen = set()
    seen_add = seen.add
    return [x for x in input_array if not (x in seen or seen_add(x))]


def get_route(start, end, waypoints):
    eve_map_complete = networkx.Graph()
    total_nodes = waypoints + [start, end]
    with open("static/eve_complete_edges.msgpack", "rb") as data_file:
        unpacker = msgpack.unpack(data_file)
        for unpacked in unpacker:
            if unpacked[0] in total_nodes and unpacked[1] in total_nodes:
                eve_map_complete.add_edge(unpacked[0], unpacked[1], weight=unpacked[2])
    eve_map_complete.add_node("dummy")
    eve_map_complete.add_edge("dummy", start, weight=0)
    eve_map_complete.add_edge("dummy", end, weight=0)
    for x in waypoints:
        eve_map_complete.add_edge("dummy", x, weight=999999999)
    print(networkx.density(eve_map_complete))
    greedy_cycle = networkx.approximation.greedy_tsp(eve_map_complete, weight="weight")
    output = networkx.approximation.simulated_annealing_tsp(eve_map_complete, greedy_cycle, weight="weight")
    print(output)
    output = cycle_post_process(output, start)
    print(output)
    output = array_to_pairs(output)
    print(output)
    final_path = []
    for x in output:
        path = networkx.shortest_path(eve_map, str(x[0]), str(x[1]))
        final_path += path[:-1]
    final_path.append(output[-1][1])
    final_path = [str(x) for x in final_path]
    if final_path[0] != str(test_start) or final_path[-1] != str(test_end):
        print("Something went wrong! Start or end not correct.")
        print(final_path[0], test_start)
        print(final_path[-1], test_end)
        return None
    waypoints = [str(x) for x in waypoints]
    if not all(x in final_path for x in waypoints):
        print("Something went wrong! Not all waypoints present.")
        print(waypoints)
        return None
    route_validator(eve_map, final_path)
    return final_path


def route_validator(graph, route, verbose=False):
    if verbose:
        print("Route start: {}".format(map_metadata[route[0]]["name"]))
        print("Route end: {}".format(map_metadata[route[-1]]["name"]))
    for i in range(len(route) - 1):
        if verbose:
            print("Checking edge {} to {}".format(map_metadata[route[i]]["name"], map_metadata[route[i + 1]]["name"]))
        if not graph.has_edge(route[i], route[i + 1]):
            if verbose:
                print("Edge {} to {} does not exist".format(map_metadata[route[i]]["name"],
                                                            map_metadata[route[i + 1]]["name"]))
            return False
        else:
            if verbose:
                print("Edge {} to {} exists".format(map_metadata[route[i]]["name"], map_metadata[route[i + 1]]["name"]))

    print("Route is valid")
    return True


test_start = 30000142
test_end = 30000144
test_waypoints = [30004131, 30003731, 30001899, 30001953, 30001131, 30001956, 30002655, 30000450, 30001954, 30003269,
                  30003350, 30001044, 30002386, 30004510, 30002533, 30000598, 30000794, 30004362, 30001560,
                  30001679, 30000567, 30005109, 30003161, 30001161, 30000002, 30003154, 30003254, 30003234, 30002738]
start_time = time.time()
print(get_route(test_start, test_end, test_waypoints))
print(time.time() - start_time)
