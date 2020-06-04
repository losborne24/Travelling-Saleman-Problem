import random
import re
import math
import os.path as path


def substring_after(s, splitter):       # substring(string to split, split text at splitter)
    s = s.rstrip('\n')
    return s.partition(splitter)[2]     # return text after '= '


def find_tour(filename):
    all_lengths = ""                    # stores all lengths of tours
    city_file = open(filename, "r")     # open city file
    filename = substring_after(filename, "NEW")     # create tour file
    tour_file = open(path.abspath(path.join(__file__, "../../tourfiles/Simulated Annealing/tourNEW" + filename)), 'w')
    size = 0
    for line in city_file:
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
    max_size = int(size)                            # size of distance matrix
    all_lengths = all_lengths.replace("\n", "")     # convert all_lengths into an array of lengths
    all_lengths = re.sub("[^0123456789,]", "", all_lengths)
    all_lengths = all_lengths.split(",")
    dist_matrix = [['-'] * int(size) for _ in range(int(size))]
    for x in range(0, len(all_lengths)):        # build dist_matrix
        if col_count - row_count > max_size - 1:
            row_count += 1
            col_count = row_count + 1
            max_size -= 1
        dist_matrix[int(col_count)][int(row_count)] = all_lengths[x]
        dist_matrix[int(row_count)][int(col_count)] = all_lengths[x]
        col_count += 1
    temperature = list()                        # list of temperatures
    temp_size = 8
    curr_tour = list()
    for i in range(0, int(size)):               # create initial tour 1,2,3...n
        curr_tour.append(i)
    set_temp(temp_size, size, curr_tour, dist_matrix, temperature)           # create initial temperature values
    tsp_tour = sim_ann(temperature, size, curr_tour, dist_matrix, temp_size)  # run sim_ann algorithm
    total_length = get_length(dist_matrix, tsp_tour, size)
    print("LENGTH = " + str(total_length) + ",")
    tour_file.write("LENGTH = " + str(total_length) + "," + "\n")
    tsp_tour_cs = ""
    for c in tsp_tour:                          # change nodes to 1,2,3...n (from 0,1,2...n-1)
        val = int(c) + 1
        tsp_tour_cs = tsp_tour_cs + str(val) + ","
    tsp_tour_cs = tsp_tour_cs[:-1]              # remove last ','
    print(tsp_tour_cs)
    tour_file.write(tsp_tour_cs)                # write to file


def get_length(dist_matrix, tour, size):        # get length of tour
    total_length = 0
    for i in range(0, int(size) - 1):
        total_length += int(dist_matrix[int(tour[i])][int(tour[i + 1])])
    total_length += int(dist_matrix[int(tour[int(size) - 1])][int(tour[0])])    # convert path length to cycle length
    return total_length


def sim_ann(temperature, size, curr_tour, dist_matrix, temp_size):
    mini = 0.025                                # minimum temperature before exiting loop
    count = 1
    max_temp = 0
    for i in temperature:                       # find max temp in list
        if int(max_temp) < i:
            max_temp = i
    while float(max_temp) > float(mini):        # repeat while temperature is greater than minimum
        t = 0                                   # inner loop cumulative temperature
        c = 0                                   # inner loop counter
        if max_temp == 0:
            break
        for i in range(0, int(size)):
            tour_one = ran_tour_one(size, curr_tour)    # find three tours using three different algorithms.
            tour_two = ran_tour_two(size, curr_tour)
            tour_three = ran_tour_three(size, curr_tour)
            curr_tour_length = get_length(dist_matrix, curr_tour, size)     # find the lengths of these tours
            tour_one_length = get_length(dist_matrix, tour_one, size)
            tour_two_length = get_length(dist_matrix, tour_two, size)
            tour_three_length = get_length(dist_matrix, tour_three, size)
            new_tour_length = tour_one_length
            new_tour = tour_one
            if new_tour_length > tour_two_length:       # and take shortest cycle as new tour.
                new_tour = tour_two
                new_tour_length = tour_two_length
            if new_tour_length > tour_three_length:
                new_tour = tour_three
                new_tour_length = tour_three_length
            if curr_tour_length >= new_tour_length:     # if new_tour is shorter than curr_tour, update curr_tour
                curr_tour = new_tour
            else:                                       # else use temperature to calculate if longer tour is acceptable
                prob = math.exp((curr_tour_length - new_tour_length) / max_temp)
                r = random.randint(1, 999) / 1000
                if r < prob:                            # accept tour if random value is less than the probability
                    # add temperature to cumulative total
                    t = t + (curr_tour_length - new_tour_length) / (math.log10(r))
                    curr_tour = new_tour                # update tour
                    c = c + 1                           # increment counter (used later to calculate mean temperature t)
        if c != 0:
            cooling_value = cooling_system(temp_size, temperature, count)       # calculate cooling value (0,1)
            # replace max_temp with mean temperature multiplied by cooling value
            temperature.remove(max_temp)
            temperature.append((t / c) * cooling_value)
        else:                                           # if no worse tour gets accepted, c=0, and max_temp remains.
            cooling_value = cooling_system(temp_size, temperature, count)
            for i in range(0, temp_size):
                if temperature[i] == max_temp:          # lower max_temp by multiplying it with cooling_value
                    temperature[i] = max_temp * cooling_value
        count += 1
        max_temp = 0
        for i in range(0, temp_size):                   # reset and find new max_temperature
            if max_temp < temperature[i]:
                max_temp = temperature[i]
        # print(str(curr_tour_length) + " + " + str(count) + " + " + str(max_temp))
    return curr_tour


def cooling_system(temp_size, temperature, count):      # calculate cooling value by using variance
    mean_temp = 0
    square_mean_temp = 0
    for i in range(0, temp_size):                       # sigma^2 = E[X^2]- [E[X]]^2
        mean_temp += temperature[i]
        square_mean_temp += (temperature[i]) ** 2
    mean_temp = mean_temp / temp_size
    square_mean_temp = square_mean_temp / temp_size
    variance = square_mean_temp - (mean_temp ** 2)      # count ** 0.999 decreases max_temp
    cooling_value = variance ** (1 / (1 - (variance ** (3/2)))) * (0.999 ** count)
    return cooling_value


def set_temp(temp_size, size, curr_tour, dist_matrix, temperature):
    i = 0
    prob = 0.9
    while i < temp_size:                                # while temperature list isn't full
        tour_one = ran_tour_one(size, curr_tour)        # find shortest tour from three tour-finding algorithms
        tour_two = ran_tour_two(size, curr_tour)
        tour_three = ran_tour_three(size, curr_tour)
        curr_tour_length = get_length(dist_matrix, curr_tour, size)
        tour_one_length = get_length(dist_matrix, tour_one, size)
        tour_two_length = get_length(dist_matrix, tour_two, size)
        tour_three_length = get_length(dist_matrix, tour_three, size)
        new_tour = tour_one
        new_tour_length = tour_one_length
        if new_tour_length > tour_two_length:
            new_tour = tour_two
            new_tour_length = tour_two_length
        if new_tour_length > tour_three_length:
            new_tour = tour_three
            new_tour_length = tour_three_length
        if curr_tour_length > new_tour_length:
            curr_tour = new_tour
        new_temp = abs((new_tour_length - curr_tour_length) / -(math.log10(prob)))  # calculate temperature values
        # if new_tour_length = curr_tour_length, find a different temperature
        if new_temp == 0:
            i -= 1
        else:                                           # else add temperature to list
            temperature.append(new_temp)
        i += 1


def ran_tour_one(size, curr_tour):                      # swap node one with node two
    ran_one = random.randint(0, int(size) - 1)
    ran_two = ran_one
    tour = list()
    while ran_one == ran_two:                           # make sure ran_one and ran_two are different nodes
        ran_two = random.randint(0, int(size) - 1)
    for i in range(0, int(size)):
        if i == ran_one:
            tour.append(curr_tour[ran_two])
        elif i == ran_two:
            tour.append(curr_tour[ran_one])
        else:
            tour.append(curr_tour[i])
    return tour


def ran_tour_two(size, curr_tour):                      # insert node ran_two next to node ran_one
    ran_one = random.randint(0, int(size) - 1)
    ran_two = ran_one
    tour = list()
    while ran_one == ran_two:                           # make sure ran_one and ran_two are different nodes
        ran_two = random.randint(0, int(size) - 1)
    if ran_one > ran_two:
        temp = ran_one
        ran_one = ran_two
        ran_two = temp
    shift = 0
    for i in range(0, int(size)):                       # keep path the same until ran_one is reached
        if shift == 0:
            if i == ran_one:                            # then insert ran_two and shift remaining nodes
                tour.append(curr_tour[ran_two])
                shift = 1
            else:
                tour.append(curr_tour[i])
        elif shift == 1:
            if i == ran_two:
                tour.append(curr_tour[i-1])
                shift = 0
            else:
                tour.append(curr_tour[i-1])
    return tour


def ran_tour_three(size, curr_tour):                    # invert nodes between ran_one and ran_two
    ran_one = random.randint(0, int(size) - 1)
    ran_two = ran_one
    tour = list()
    while ran_one == ran_two:                           # make sure ran_one and ran_two are different nodes
        ran_two = random.randint(0, int(size) - 1)
    if ran_one > ran_two:                               # swap ran_one with ran_two if ran_one > ran_two
        temp = ran_one
        ran_one = ran_two
        ran_two = temp
    flip = 0
    for i in range(0, int(size)):                       # keep path the same until ran_one is reached
        if flip == 0:
            if i == ran_one:                            # then inverse all nodes between ran_one and ran_two
                flip = 1                                    # and leave remaining nodes in same position
                tour.append(curr_tour[ran_two])
            else:
                tour.append(curr_tour[i])
        else:
            if i == ran_two:
                flip = 0
                tour.append(curr_tour[ran_one])
            else:
                tour.append(curr_tour[ran_two - (i - ran_one)])
    return tour


if __name__ == '__main__':
    input_file = "NEWAISearchfile012.txt"
    city_filename = path.abspath(path.join(__file__, "../../cityfiles/" + input_file))
    find_tour(city_filename)
