import networkx
import cProfile
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
                    eve_map_complete.add_edge(a, b, weight=networkx.shortest_path_length(eve_map, a, b,
                                                                                         weight="weight"))
        if networkx.density(eve_map_complete) != 1:
            print("Something went wrong! Graph not complete.")
            return None
        print("what")
        networkx.write_multiline_adjlist(eve_map_complete, "static/testing.adjlist")
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
        path = networkx.shortest_path(eve_map, x[0], x[1], weight="weight")
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
    if final_path[0] != start or final_path[-1] != end:
        print("Something went wrong! Start or end not correct.")
        return None
    if not all(x in final_path for x in waypoints):
        print("Something went wrong! Not all waypoints present.")
        return None
    for i in range(len(final_path) - 1):
        if not graph.has_edge(final_path[i], final_path[i + 1]):
            return False
    print("Route is valid")
    return True


def route_mapper(waypoints, config):
    full_avoid = []
    avoid_priority = copy.copy(config["avoid_priority"])
    for x in range(len(avoid_priority)):
        edge_weight = avoid_weights[x]
        current_avoid = avoid_priority.pop(0)
        if current_avoid == "system":
            current_avoid_list = config["avoid_systems"]
        else:
            current_avoid_list = metadata[current_avoid]
        full_avoid.append(current_avoid_list)
        for system in current_avoid_list:
            for edge in eve_map_base.edges(system):
                eve_map_base[edge[0]][edge[1]]["weight"] = edge_weight

    out_route = get_route(eve_map_base, waypoints)
    out_waypoints = waypoint_deconstructor(out_route, eve_map_base)
    if config["avoid_check"] == "full":
        if not full_avoid_checker(out_waypoints, out_route, full_avoid, config):
            print("Something went wrong! Avoid checker failed.")
            return [], []
    elif config["avoid_check"] == "simple":
        if not simple_avoid_checker(out_route, full_avoid):
            print("Something went wrong! Avoid checker failed.")
            return [], []
    return out_route, out_waypoints


def waypoint_deconstructor(route, eve_map):
    out_waypoints = []
    route_end = route[-1]
    current_start = route[0]
    verification_route = []
    while current_start != route_end:
        for a in reversed(route):
            sub_route = networkx.shortest_path(eve_map, current_start, a)
            test_index = route.index(a) + 1
            current_start_index = route.index(current_start)
            actual_route = route[current_start_index:test_index]
            if sub_route == actual_route:
                out_waypoints.append(a)
                if verification_route:
                    verification_route.pop()
                verification_route.extend(sub_route)
                current_start = a
                break
    if verification_route != route:
        print("Something went wrong! Route deconstruction failed.")
        return []
    else:
        print("Route deconstruction successful.")
        return out_waypoints


def simple_avoid_checker(final_route, full_avoid):
    full_avoid = [x for a in full_avoid for x in a]
    full_avoid = list(set(full_avoid))
    for x in final_route:
        if x in full_avoid:
            print(f"Something went wrong! Avoid system {x} present in route.")
            return False
    print("No avoid systems present in route.")
    return True


def full_avoid_checker(out_waypoints, out_route, full_avoid, config):
    avoid_priority = copy.copy(config["avoid_priority"])
    for x in range(len(avoid_priority)):
        eve_map = eve_map_base.copy(eve_map_base)
        avoid_set = full_avoid[x]
        for avoid_system in avoid_set:
            eve_map.remove_node(avoid_system)
        out_pairs = array_to_pairs(out_waypoints)
        try:
            avoidable = all(networkx.has_path(eve_map, x[0], x[1]) for x in out_pairs)
        except networkx.exception.NodeNotFound:
            avoidable = False
        avoided = all(x not in avoid_set for x in out_route)
        if avoidable != avoided:
            return False
    print("Avoid checker passed.")
    return True


test_waypoints = ["30004131", "30001899"]
test_avoid_systems = ["30001899"]
test_avoid_priority = ["system", "ls"]
test_config = {
    "avoid_systems": test_avoid_systems,
    "avoid_priority": test_avoid_priority,
    "avoid_check": False
}
if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    test_route, test_waypoints = route_mapper(test_waypoints, test_config)
    named_route = [system_metadata[x]["name"] for x in test_route]
    named_waypoints = [system_metadata[x]["name"] for x in test_waypoints]
    profiler.disable()
    profiler.dump_stats("test1.prof")

