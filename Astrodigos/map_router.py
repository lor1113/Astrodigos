import networkx
import time
import itertools

eve_map = networkx.read_multiline_adjlist("static/eve_map.adjlist")

avoid_weights = [1, 100, 10000, 1000000, 100000000]
trig = [30004981, 30000163, 30003464, 30005330, 30002557, 30003856, 30002645, 30003076, 30045338, 30045345, 30000182,
        30002771, 30001400, 30002760, 30003073, 30001401, 30000205, 30004244, 30001685, 30002795, 30001358, 30001390,
        30001391, 30045354, 30002575, 30001447, 30001383, 30045331]
edencom = [30004090, 30000105, 30002704, 30002266, 30003398, 30003515, 30005252, 30002253, 30003556, 30003885, 30005251,
           30000113, 30002530, 30003548, 30002700, 30003397, 30003574, 30004973, 30004250, 30004305, 30003392, 30002651,
           30003541, 30002386, 30004084, 30004248, 30004100, 30000188, 30004141, 30000004, 30003883, 30005260, 30003490,
           30004103, 30002242, 30002986, 30003539, 30002665, 30005058, 30003050, 30004992, 30003573, 30002662, 30002251,
           30045322, 30000005, 30002243, 30004150, 30005052, 30002385, 30000118, 30003553, 30003514, 30003854, 30002644,
           30003480, 30004301, 30002051, 30003824, 30005086, 30000012, 30003919, 30002724, 30003478, 30003908, 30002048,
           30000109, 30005267, 30003809, 30005034, 30004108, 30003904, 30001660, 30002513, 30005074, 30004284, 30000102,
           30004256, 30003078, 30003463, 30004287, 30004263, 30004254, 30003918, 30004257, 30003900, 30003587, 30005213,
           30002397, 30000048, 30003788, 30000062, 30001696, 30000060, 30005308, 30004295, 30003823, 30005066, 30004999,
           30003558, 30003482, 30003061, 30005263, 30005236, 30001376, 30003460, 30003058, 30004302, 30002506, 30003088,
           30001718, 30004978, 30002772, 30002239, 30000160, 30003829, 30002241, 30003894, 30003090, 30005255, 30003074,
           30003931, 30005222, 30004231, 30002999, 30004268, 30005209, 30005219, 30003794, 30005334, 30003932, 30003481,
           30002755, 30004289, 30003927, 30005284]


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
        output = array_to_pairs(output)
    else:
        output = tsp_brute_force(eve_map_complete, waypoints, start, end)
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


def route_validator(graph, route):
    for i in range(len(route) - 1):
        if not graph.has_edge(route[i], route[i + 1]):
            return False
    print("Route is valid")
    return True


test_start = 30000142
test_end = 30000144
test_waypoints = [30004131, 30003731, 30001899, 30001953, 30001131, 30001956, 30002655, 30000450, 30001954, 30003269,
                  30003350, 30001044, 30002386, 30004510, 30002533, 30000598, 30000794, 30004362, 30001560,
                  30001679, 30000567, 30005109, 30003161, 30001161, 30000002, 30003154, 30003254, 30003234, 30002738]
start_time = time.time()
out_route = get_route(test_start, test_end, test_waypoints)
print(len(out_route))
print(time.time() - start_time)
