import networkx
import msgpack
import time
import itertools

eve_map = networkx.read_multiline_adjlist("static/eve_map.adjlist")
map_metadata = msgpack.unpack(open("static/eve_map_metadata.msgpack", "rb"))


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
    start_time = time.time()
    for a in total_nodes:
        for b in total_nodes:
            if a != b:
                eve_map_complete.add_edge(a, b, weight=networkx.shortest_path_length(eve_map, str(a), str(b)))
    print("Graph complete in {} seconds".format(time.time() - start_time))
    if networkx.density(eve_map_complete) != 1:
        print("Something went wrong! Graph not complete.")
        return None
    start_time = time.time()
    output, cost = tsp_brute_force(eve_map_complete, waypoints, start, end)
    print("TSP complete in {} seconds".format(time.time() - start_time))
    print(output)
    output = array_to_pairs(output)
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


def tsp_brute_force(graph, waypoints, start, end):
    best_cost = -1
    best_route = []
    for permutation in itertools.permutations(waypoints):
        cost = 0
        route = [start] + list(permutation) + [end]
        for i in range(len(route) - 1):
            cost += graph[route[i]][route[i + 1]]["weight"]
        if best_cost == -1 or cost < best_cost:
            best_cost = cost
            best_route = route
    return best_route, best_cost


test_start = 30000142
test_end = 30000144
test_waypoints = [30004131, 30003731, 30001899, 30001953, 30001131, 30001956, 30002655, 30000450]
start_time = time.time()
route = get_route(test_start, test_end, test_waypoints)
print(len(route))
print("Total time: {} seconds".format(time.time() - start_time))

