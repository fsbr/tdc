# planners that cover the boustrophedon decomposition
import collections
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import LineString

class Agent:
    # what is an agent to me?
    def __init__(self):
        # each element of waypoints_list is the list of waypoints for a particular cell
        self.waypoints_list = []

        # an altitude we assign the drone to prevent collisions
        self.transition_elevation = None
        self.number = None


    def generate_transition_path(self,start,end, f):
        # a list of waypoints that 
        z = self.transition_elevation
        print("transition elevation to be added into the waypoint", z)
        print("start point", start) 
        print("end point", end) 
        intermediate_xs = np.arange(start[0], end[0], 1)    
        m = (end[1] - start[1])/(end[0] - start[0])
        b = end[1] - m*end[0]
        intermediate_ys = m*intermediate_xs + b
        for x,y in zip(intermediate_xs, intermediate_ys):
            transition_path = (x,y,z)
            print("transition_path", transition_path)
            f.write("%s,%s,%s\n"%(transition_path[0], transition_path[1], transition_path[2]))

    def format_waypoints_printable(self):
        f = open("output_file_agent%s.csv"%self.number, "w")
        #f.write(str(self.waypoints_list))
        for ii, waypoint_set in enumerate(self.waypoints_list):
            #f.write(str(waypoint_set)+"\n")
            for waypoint in waypoint_set:
                f.write("%s,%s,%s\n"%(waypoint[0],waypoint[1],waypoint[2]))
            # between waypoint sets generate the transition waypoints except  
            start = waypoint_set[-1]
            # end point is the next cells first waypoint
            end = self.waypoints_list[(ii+1)%len(self.waypoints_list)][0]
            print(start) 
            print(end)
            transition_waypoints = self.generate_transition_path(start, end, f)
        # outputting the waypoints with safe transition elevations
        f.close()
        
def bfs(tdcInstance):
    cells = tdcInstance.closed
    Q = collections.deque()
    start = cells[0]
    solution = []
    print(start)
    Q.append(start)
    start.visited = True
    while len(Q) > 0:
        v = Q.pop()
        solution.append(v)
        for neighbor in v.neighborList:
            if neighbor.visited == False:
                neighbor.visited = True
                Q.append(neighbor)
    return solution

def dfs(tdcInstance):
    cells = tdcInstance.closed
    Q = collections.deque()
    start = cells[0]
    solution = []
    print(start)
    Q.append(start)
    start.visited = True
    while len(Q) > 0:
        v = Q.pop()
        solution.append(v)
        for neighbor in v.neighborList:
            if neighbor.visited == False:
                neighbor.visited = True
                Q.appendleft(neighbor)
    return solution


def boustro_endpoints(ceil_floor_list, jj):
    colors = ["blue", "green", "red", "orange"]
    xs, ys = [], []
    # what this loop is suppose to do is assign source_state and target_state based on the 
    # thing, f,c 
    edges_for_boustro = []
    for edge in ceil_floor_list:
        if edge.endPoint != None and edge.endPoint != False:
            tmp = edge.endPoint
            if edge.source_state[0] < tmp[0]:
                edge.target_state = tmp
            else:
                edge.source_state = tmp

        if edge.startPoint != None and edge.startPoint != False:
            tmp = edge.startPoint
            if edge.source_state[0] > tmp[0]:
                edge.target_state = tmp
            else:
                edge.source_state = tmp
    
        xs = [edge.source_state[0], edge.target_state[0]]
        ys = [edge.source_state[1], edge.target_state[1]]
        plt.plot(xs, ys, color = colors[jj%len(colors)])
        edges_for_boustro.append( (xs,ys) )
    return edges_for_boustro

def floor_ceiling_boundaries(edges_list, kind, safety_boundary):
    # buffer where the drone goes by the safety_boundary
    floor_ceiling_boundary = []
    for edge in edges_list:
        x_coords = edge[0]
        y_coords = edge[1]
        if kind == "CEILING":
            y_coords = [y - safety_boundary for y in y_coords]
        elif kind == "FLOOR":
            y_coords = [y + safety_boundary for y in y_coords]
        floor_ceiling_boundary.append((x_coords, y_coords))
    return  floor_ceiling_boundary

def boundary_intersections(yMax, line, x):
    # takes edges and finds the intersections 
    # line is the edge in the floor or ceiling list
    print(line)
    x1 = line[0][0]
    x2 = line[0][1]
    y1 = line[1][0]
    y2 = line[1][1]
    
    sweep_line = LineString([(x, -1), (x, yMax+1)])
    print(line)
    line = LineString([(x1, y1), (x2, y2)]) 
    status = sweep_line.intersects(line)
    if status == True:
        intersection_point = sweep_line.intersection(line)
        print("points = ", intersection_point.x, intersection_point.y)
        return (intersection_point.x, intersection_point.y) 

def get_waypoints(tdcInstance):
    # this function needs to examine the edges in each cell, and output waypoints that DB can use in his demo
    cells = tdcInstance.closed
    xMax = tdcInstance.xMax
    yMax = tdcInstance.yMax
    
    # each quadcopter will fly at its own elevation, z coordinate
    elevation_base = 14 
    elevations = [elevation_base+1, elevation_base + 2, elevation_base +3, elevation_base+4]
    safety_boundary = 0.5
    lap_width = 1

    print(cells)
    agent_list = []
    colors = ["blue", "green", "red", "orange"]
    for i in range(0, len(colors)):
        agent_to_add = Agent()
        agent_to_add.transition_elevation = elevations[i]
        agent_to_add.number = i
        agent_list.append( agent_to_add )
        
    for jj, cell in enumerate(cells):
        # a new waypoints list is to be generated each cell
        waypoints = []
        # this function is trying to do too much since it is plotting and processing the cell somehow
        #print("\n\n NEW CELL \n\n")
        xs, ys = [], []
        leftmost_x = np.Inf
        rightmost_x = -np.Inf 
        leftmost_y, rightmost_y = [],[]
        ceiling_edges = boustro_endpoints(cell.ceilingList, jj)    
        floor_edges = boustro_endpoints(cell.floorList, jj)    
        
        print("EDGES IN WAYPOINT GENERATION")
        print(ceiling_edges)
        print(floor_edges)

        # its like my handwriting is better if i write code like this
        # small functions are good
        ceiling_boundary = floor_ceiling_boundaries(ceiling_edges, "CEILING", safety_boundary)
        floor_boundary = floor_ceiling_boundaries(floor_edges, "FLOOR", safety_boundary)
        print("ceiling boundary", ceiling_boundary)
        print("floor boundary", floor_boundary)
        
        # find the minimum x in the floor_boundary set
        # there has to be a better way to unwrap this
        x_coords = []
        for floor_edge in floor_boundary:
            print("FLOOR EDGE", floor_edge)
            print("Floor_edge[0]", floor_edge[0])
            for x_coord in floor_edge[0]:
                x_coords.append(x_coord)
        x_max = max(x_coords)
        x_min = min(x_coords)
        print("max, min", x_max, x_min)

        # intention: sweep from x_min to x_max, in intervals of lap_width
        x_range = np.arange(x_min, x_max+1, lap_width) 
        print(x_range)
        flip = True
        for x in x_range:
            print("floor boundary", floor_boundary)
            print("floor boundary", floor_boundary[0])

            # check that point of x against everythign in the ceiling and floor boundary
            for edge in ceiling_boundary:
                ceil_int = boundary_intersections(yMax, edge, x)
                if ceil_int != None:
                    y_max = ceil_int[1]
            for edge in floor_boundary:
                floor_int = boundary_intersections(yMax, edge, x)
                if floor_int != None:
                    y_min = floor_int[1]
            #print("floor int", floor_int)
            #print("ceil int", ceil_int)
            #print("y_min", y_min)
            #print("y_max", y_max)
            y_steps = np.arange(y_min, y_max, lap_width)
            #print("y_steps", y_steps) 
            #print("x", x)
            if flip == False:
                y_steps = y_steps[::-1]
            for step in y_steps:
                waypoints.append((x, step, elevation_base))
                plt.scatter(x, step, c="k", s=0.5)
            flip = not flip
        agent_to_update = agent_list[jj%len(agent_list)]
        agent_to_update.waypoints_list.append(waypoints)
        print("jj", jj)
        print("waypoints", waypoints)
        plt.xlim((0, tdcInstance.xMax))
        plt.ylim((0, tdcInstance.yMax))
        plt.axis("equal")
        #plt.show()
    return agent_list 
