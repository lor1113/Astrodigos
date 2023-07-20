import networkx
import time
import itertools
import json
import copy

metadata = json.load(open("static/metadata.json", "r"))
system_metadata = json.load(open("static/system_metadata.json", "r"))
eve_map_base = networkx.read_multiline_adjlist("static/eve_map_base.adjlist")
avoid_weights = [10000000000, 100000000, 1000000, 10000, 100, 1]


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


def get_route(eve_map, waypoints):
    start = waypoints.pop(0)
    end = waypoints.pop(-1)
    if len(waypoints) != 0:
        eve_map_complete = networkx.Graph()
        total_nodes = waypoints + [start, end]
        for a in total_nodes:
            for b in total_nodes:
                if a != b:
                    eve_map_complete.add_edge(a, b, weight=networkx.shortest_path_length(eve_map, str(a), str(b)))
        if networkx.density(eve_map_complete) != 1:
            print("Something went wrong! Graph not complete.")
            return None
        if len(waypoints) > 9:
            eve_map_complete.add_node("dummy")
            eve_map_complete.add_edge("dummy", start, weight=0)
            eve_map_complete.add_edge("dummy", end, weight=0)
            for x in waypoints:
                eve_map_complete.add_edge("dummy", x, weight=999999999)
            greedy = networkx.approximation.greedy_tsp(eve_map_complete)
            output = networkx.approximation.threshold_accepting_tsp(eve_map_complete, greedy, max_iterations=100,
                                                                    N_inner=1000)
            output = cycle_post_process(output, start)
        else:
            output = tsp_brute_force(eve_map_complete, waypoints, start, end)
        output = array_to_pairs(output)
    else:
        output = [(start, end)]
    final_path = []
    for x in output:
        path = networkx.shortest_path(eve_map, str(x[0]), str(x[1]), weight="weight")
        final_path += path[:-1]
    final_path.append(output[-1][1])
    final_path = [str(x) for x in final_path]
    route_validator(eve_map, final_path, start, end, waypoints)
    return final_path


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
    return best_route


def route_validator(graph, final_path, start, end, waypoints):
    if final_path[0] != str(start) or final_path[-1] != str(end):
        print("Something went wrong! Start or end not correct.")
        return None
    waypoints = [str(x) for x in waypoints]
    if not all(x in final_path for x in waypoints):
        print("Something went wrong! Not all waypoints present.")
        return None
    for i in range(len(final_path) - 1):
        if not graph.has_edge(final_path[i], final_path[i + 1]):
            return False
    print("Route is valid")
    return True


def route_mapper(waypoints, config):
    eve_map = copy.copy(eve_map_base)
    full_avoid = []
    avoid_priority = copy.copy(config["avoid_priority"])
    for x in range(len(avoid_priority)):
        edge_weight = avoid_weights[x]
        current_avoid = avoid_priority.pop()
        print(current_avoid)
        if current_avoid == "system":
            full_avoid += config["avoid_systems"]
            for system in config["avoid_systems"]:
                for edge in eve_map.edges(str(system)):
                    eve_map[edge[0]][edge[1]]["weight"] = edge_weight
        if current_avoid == "trig":
            full_avoid += metadata["trig"]
            for system in metadata["trig"]:
                for edge in eve_map.edges(str(system)):
                    eve_map[edge[0]][edge[1]]["weight"] = edge_weight
        if current_avoid == "edencom":
            full_avoid += metadata["edencom"]
            for system in metadata["edencom"]:
                for edge in eve_map.edges(str(system)):
                    eve_map[edge[0]][edge[1]]["weight"] = edge_weight
        if current_avoid == "hs":
            full_avoid += metadata["hs"]
            for avoid_hs in metadata["hs"]:
                for edge in eve_map.edges(str(avoid_hs)):
                    eve_map[edge[0]][edge[1]]["weight"] = edge_weight
        if current_avoid == "ls":
            full_avoid += metadata["ls"]
            for system in metadata["ls"]:
                for edge in eve_map.edges(str(system)):
                    eve_map[edge[0]][edge[1]]["weight"] = edge_weight
        if current_avoid == "ns":
            full_avoid += metadata["ns"]
            for system in metadata["ns"]:
                for edge in eve_map.edges(str(system)):
                    eve_map[edge[0]][edge[1]]["weight"] = edge_weight

    networkx.write_multiline_adjlist(eve_map, "eve_map_test.adjlist")
    full_avoid = list(set(full_avoid))
    full_avoid = [str(x) for x in full_avoid]
    out_route = get_route(eve_map, waypoints)
    avoid_checker(out_route, full_avoid)
    return out_route


def avoid_checker(final_route, full_avoid):
    for x in final_route:
        if x in full_avoid:
            print(f"Something went wrong! Avoid system {x} present in route.")
            return False
    print("No avoid systems present in route.")
    return True


test_waypoints = [30000142, 30001954]
test_avoid_systems = ["30001718"]
test_avoid_priority = ["edencom", "trig", "hs"]
test_config = {
    "avoid_systems": test_avoid_systems,
    "avoid_priority": test_avoid_priority
}
start_time = time.time()
test_result = route_mapper(test_waypoints, test_config)
named_result = [system_metadata[str(x)]["name"] for x in test_result]
print(named_result)
print(len(named_result))
print(time.time() - start_time)
