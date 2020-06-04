import re
import copy
import os.path as path
import argparse

parser = argparse.ArgumentParser(description="City file of interest")
parser.add_argument("city_file", type=str)
args = parser.parse_args()

def substring_after(s, splitter):               # substring(string to split, split text at splitter)
    s = s.rstrip('\n')
    return s.partition(splitter)[2]             # return text after '= '


def find_tour(filename):
    all_lengths = ""                                # stores all lengths of paths in one line
    city_file = open(filename, "r")
    filename = substring_after(filename, "NEW")
    tour_file = open(path.abspath(path.join(__file__, "../../tourfiles/A Star/tourNEW" + filename)), 'w')
    size = 0
    for line in city_file:      # format file
        if "NAME" in line:
            name = substring_after(line, '= ')
            print("NAME = " + name)
            tour_file.write("NAME = " + name + "\n")
        elif "SIZE" in line:
            size = substring_after(line, '= ')
            size = size.replace(',', '')
            print("TOURSIZE = " + size + ",")
            tour_file.write("TOURSIZE = " + size + "," + "\n")
        else:
            all_lengths += line
    row_count = 0
    col_count = 1
    if size == 0:
        print("Error: No size specified in city file")
        exit()
    max_size = int(size)
    all_lengths = all_lengths.replace("\n", "")
    all_lengths = re.sub("[^0123456789,]", "", all_lengths)
    all_lengths = all_lengths.split(",")
    dist_matrix = [['-'] * int(size) for _ in range(int(size))]
    for x in range(0, len(all_lengths)):            # build dist_matrix
        if col_count - row_count > max_size - 1:
            row_count += 1
            col_count = row_count + 1
            max_size -= 1
        dist_matrix[int(col_count)][int(row_count)] = all_lengths[x]
        dist_matrix[int(row_count)][int(col_count)] = all_lengths[x]
        col_count += 1
    final_path = None
    shortest_length = None
    if int(size) > 25:                              # set maximum number of start locations to 25 or less
        max_it = 25
    else:
        max_it = int(size)
    for x in range(0, max_it):                      # for each start location, run A* search
        tsp_path = a_star(dist_matrix, size, x)
        total_length = 0
        for i in range(0, int(size) - 1):           # calculate total length of the new path
            total_length += int(dist_matrix[int(tsp_path[i])][int(tsp_path[i + 1])])
        total_length += int(dist_matrix[int(tsp_path[int(size) - 1])][int(tsp_path[0])])
        if final_path is None:                      # if the new path length is shorter than the best path, replace it.
            final_path = copy.deepcopy(tsp_path)
            shortest_length = total_length
        elif total_length < shortest_length:
            final_path = copy.deepcopy(tsp_path)
            shortest_length = total_length
    print("LENGTH = " + str(shortest_length) + ",")
    tour_file.write("LENGTH = " + str(shortest_length) + "," + "\n")
    tsp_path_cs = ""
    for c in final_path:                            # change nodes to 1,2,3...n (from 0,1,2...n-1)
        val = int(c) + 1
        tsp_path_cs = tsp_path_cs + str(val) + ","
    tsp_path_cs = tsp_path_cs[:-1]                  # remove last ','
    print(tsp_path_cs)
    tour_file.write(tsp_path_cs)                    # write to file


def prim(delete_rows, dist_matrix, size):           # use prim's algorithm to find minimum spanning tree
    prim_matrix = copy.deepcopy(dist_matrix)
    for c in delete_rows:                           # delete nodes already in path
        for x in range(0, int(size)):
            prim_matrix[int(c)][x] = 'x'
            prim_matrix[x][int(c)] = 'x'
    i = 0
    while prim_matrix[i][i] != '-':                 # find start col
        i += 1
    for x in range(0, int(size)):                   # and delete start row
        prim_matrix[int(i)][x] = 'x'
    prim_recall(prim_matrix, size, i)               # run recursive part of prim's algorithm
    mst_length = 0
    for x in range(0, int(size)):                   # add up connections to find length of minimum spanning tree
        for y in range(0, int(size)):
            if prim_matrix[x][y].isdigit():
                mst_length += int(prim_matrix[x][y])
    return mst_length


def prim_recall(prim_matrix, size, i):
    lowest = None
    for x in range(0, int(size)):                   # find lowest value in column
        if lowest is None:
            if prim_matrix[x][int(i)].isdigit():
                lowest = int(prim_matrix[x][int(i)])
                pos = x
        elif prim_matrix[x][int(i)].isdigit():
            if int(lowest) > int(prim_matrix[x][int(i)]):
                lowest = int(prim_matrix[x][int(i)])
                pos = x
    if lowest is not None:                          # once found, cross out all values in row except the found number.
        for x in range(0, int(size)):
            if x != i:
                prim_matrix[pos][x] = 'x'
        prim_recall(prim_matrix, size, pos)         # repeat until a column has all its values crossed out.


def a_star(dist_matrix, size, i):
    connected_nodes_list = list()
    # Set up dijkstra's box, where '[i]' is the initial path and '0' is the working value
    connected_nodes_list.append(DijkstraBox([i], 0))
    final_path = a_star_recall(dist_matrix, size, connected_nodes_list)     # run recursive A* algorithm
    return final_path                                    # return path


def a_star_recall(dist_matrix, size, path_list):
    lowest = None
    b = int(len(path_list))
    for i in range(0, len(path_list)):        # find lowest working value
        if lowest is None:
            pos = i
            lowest = path_list[i].get_working_val()
        elif lowest > path_list[i].get_working_val():
            pos = i
            lowest = path_list[i].get_working_val()
    nodes_connected = path_list[pos].get_nodes_connected()    # and get its path
    del path_list[pos]                        # remove the path from the list of dijkstra boxes.
    # calculate the minimum spanning tree of the nodes not connected in the path
    prim_length = int(prim(nodes_connected, dist_matrix, size))
    for n in range(0, int(size)):                       # for each node in the graph,
        a_star_length = 0
        if n not in nodes_connected:                    # if the node is not already in the path
            for cn in range(0, len(nodes_connected) - 1):   # calculate the length of the current path
                a_star_length += int(dist_matrix[nodes_connected[cn]][nodes_connected[cn+1]])
            # and add the new, final connection to the total
            a_star_length += int(dist_matrix[nodes_connected[len(nodes_connected) - 1]][n])
            # add the new length of the path to the minimum spanning tree length
            tot_length = prim_length + a_star_length
            # also add the shortest two connections between the minimum spanning tree and the path.
            tot_length += shortest_connections(nodes_connected[0], str(n), nodes_connected, dist_matrix, size)
            # store the new entry into the dijkstra box list
            path_list.append(DijkstraBox(copy.deepcopy(nodes_connected), tot_length))
            path_list[len(path_list)-1].add_to_nodes_connected(n)   # and add new connection
    tot_working_val = 0                                 # method of reducing list of possible connections
    lowest = path_list[0].get_working_val()
    for i in range(0, len(path_list)):        # find lowest working value and the mean value of all paths in list
        tot_working_val += path_list[i].get_working_val()
        if lowest > path_list[i].get_working_val():
            lowest = path_list[i].get_working_val()
    a = int((tot_working_val / len(path_list)) - lowest)  # a is the difference between the mean and minimum length
    b = int(b*2)                                        # b is twice the total number of paths in the list
    filter_val = int(lowest + (a / b))                  # filter value is set as lowest + (a/b)
    # for each path in the list, if the length is greater than the filter value, remove the Dijkstra box from the list
    for i in range(len(path_list)-1, -1, -1):
        if path_list[i].get_working_val() > filter_val:
            del path_list[i]
            i -= 1
    # repeat until two nodes are not connected and brute force the last three connections for the two nodes.
    if len(path_list[len(path_list)-1].get_nodes_connected()) < int(size) - 2:
        return a_star_recall(dist_matrix, size, path_list)
    else:
        lowest = None
        for i in range(0, len(path_list)):    # find shortest path in list of length size - 2
            if len(path_list[i].get_nodes_connected()) == (int(size) - 2):
                if lowest is None:
                    pos = i
                    lowest = path_list[i].get_working_val()
                elif lowest > path_list[i].get_working_val():
                    pos = i
                    lowest = path_list[i].get_working_val()
        new_node_list = path_list[pos].get_nodes_connected()
        count = 0
        for x in range(0, int(size)):                   # find two nodes not in path
            if x not in new_node_list:
                if count == 0:
                    node_one = int(x)
                    count += 1
                else:
                    node_two = int(x)
                    break
        # calculate the two possible routes the tour can take and select the lower length as the final solution.
        route_one = int(dist_matrix[new_node_list[0]][node_one]) + int(dist_matrix[new_node_list[len(new_node_list) - 1]][node_two])
        route_two = int(dist_matrix[new_node_list[0]][node_two]) + int(dist_matrix[new_node_list[len(new_node_list) - 1]][node_one])
        if route_one < route_two:
            new_node_list.append(node_two)
            new_node_list.append(node_one)
        else:
            new_node_list.append(node_one)
            new_node_list.append(node_two)
        return new_node_list


def shortest_connections(start_node, last_node, new_node_list, dist_matrix, size):
    shortest_start_length = None                        # find the shortest connections between the mst and path
    pos = None
    for x in range(0, int(size)):                       # for each node in graph, if not connected to the path,
        if str(x) not in new_node_list and str(x) != str(last_node):
            # calculate the connection length between node 'x' and the start node
            if dist_matrix[int(start_node)][x].isdigit():
                if shortest_start_length is None:           # select the node with the shortest connection
                    shortest_start_length = dist_matrix[int(start_node)][x]
                    pos = x
                elif int(shortest_start_length) > int(dist_matrix[int(start_node)][x]):
                    shortest_start_length = dist_matrix[int(start_node)][x]
                    pos = x
    shortest_last_length = None
    for x in range(0, int(size)):
        # calculate the connection length between node 'x' and the last node in the path
        if dist_matrix[int(last_node)][x].isdigit():
            # exclude the previous node found for the start connection
            if str(x) not in new_node_list and str(x) != str(pos):
                if shortest_last_length is None:
                    shortest_last_length = dist_matrix[int(last_node)][x]
                elif int(shortest_last_length) > int(dist_matrix[int(last_node)][x]):
                    shortest_last_length = dist_matrix[int(last_node)][x]
    return int(shortest_start_length) + int(shortest_last_length)   # return the combined length of the two connections


class DijkstraBox:
    def __init__(self, nodes_connected, working_val):
        self.nodes_connected = nodes_connected
        self.working_val = working_val

    def get_nodes_connected(self):
        return self.nodes_connected

    def get_working_val(self):
        return self.working_val

    def add_to_nodes_connected(self, nodes_connected):      # add nodes to path
        self.nodes_connected.append(nodes_connected)

    def set_working_val(self, working_val):                 # update working value
        self.working_val = working_val


if __name__ == '__main__':
    city_filename = path.abspath(path.join(__file__, "../../cityfiles/" + args.city_file))
    find_tour(city_filename)
