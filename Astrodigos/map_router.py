import networkx
import json
import time

eve_map = networkx.read_adjlist('static/eve_map.adjlist')
metadata = json.load(open('static/eve_map_metadata.json', 'r'))


def get_route(start, end, waypoints):
    eve_map.add_node("dummy")
    eve_map.add_edge("dummy", start)
    eve_map.add_edge("dummy", end)
    waypoints.extend([start, end, "dummy"])
    solution = networkx.approximation.traveling_salesman_problem(eve_map, nodes=waypoints)
    eve_map.remove_node("dummy")
    return solution


test_start = "30000142"
test_end = "30000144"
test_waypoints = ["30004237", "30003597"]


start_time = time.time()
print(get_route(test_start, test_end, test_waypoints))
print(time.time() - start_time)
