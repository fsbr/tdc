# 
import sys
import heapq
import copy
from shapely.geometry import LineString

from visualizer import Visualizer
import planners

class Edge:
    def __init__(self):
        self.source_state = None
        self.target_state = None
        self.f = None
        self.c = None
        self.sourceIsLeftMost = None

        self.startPoint = None
        self.endPoint = None

class Event:
    def __init__(self):
        self.location = None
        self.type = None
        self.floorPointer = []
        self.ceilingPointer = []

class Interval:
    def __init__(self):
        self.top_point = None
        self.bot_point = None
        self.safe = False

class Cell:
    def __init__(self):
        self.ceilingList = []
        self.floorList = []
        self.visited = False
        self.cleaned = False

        # for computing the adjacency
        self.neighborList = []

        # omfg
        self.minFloor = None
        self.maxFloor = None

        self.minCeiling = None
        self.maxCeiling = None

class TDC:
    def __init__(self):
        self.eventsList = []

        self.open = []
        self.closed = []

        # okay
        self.connectivity = 1
        # cellList is the primary output
        self.cellList = []
        self.eventId = 0
        self.dbg = False

    def readObstacles(self):
        inputFile = open("input%s.txt"%(sys.argv[1]), "r")
        #inputFile = open("inputfloat.txt", "r")
        #inputFile = open("input3.txt", "r")
        #inputFile = open("input2.txt", "r")
        #inputFile = open("input.txt", "r")
        #inputFile = open("input4.txt", "r")

        obstacles = []
        lineNumber = 0
        for line in inputFile:
            #sys.stdout.write(line)
            splitLine = line.split(";")
            #print(splitLine)
            if lineNumber == 0:
                self.xMax = float(line)      
            elif lineNumber == 1:
                self.yMax = float(line)
            elif lineNumber >= 1:
                obstacle = []
                for item in splitLine:
                    a = item.split(",") 
                    #print("a", a)
                    if a[0] != "\n":
                        obstacle.append( (float(a[0]), float(a[1])) )
                obstacles.append(obstacle)
            lineNumber+=1
        self.obstacles = obstacles
        print(obstacles)
        print("OBSTACLES", obstacles)
        return self.obstacles

    def makeEvents(self, obstacles):
        obstacles = self.obstacles
        print("Making TDC")
        print("With obstacles, ", obstacles)
        for obstacle in obstacles:
            for i, vertex in enumerate(obstacle):
                print("Vertex", vertex)
                eventToAdd = Event()
                eventToAdd.location = vertex
                prior_x = obstacle[(i-1)%len(obstacle)][0]
                next_x = obstacle[(i+1)%len(obstacle)][0]

                if vertex[0] < prior_x and vertex[0] < next_x:
                    eventToAdd.type = "IN" 
                    print("IN EVENT at ", vertex)
                    self.connectivity+=1

                    ceilingEdgeToAdd = Edge()
                    ceilingEdgeToAdd.source_state = obstacle[i]
                    ceilingEdgeToAdd.target_state = obstacle[(i+1)%len(obstacle)]
                    eventToAdd.ceilingPointer.append(ceilingEdgeToAdd)

                    floorEdgeToAdd = Edge()
                    floorEdgeToAdd.source_state = obstacle[i-1]
                    floorEdgeToAdd.target_state = obstacle[i]
                    eventToAdd.floorPointer.append(floorEdgeToAdd)

                elif vertex[0] > prior_x and vertex[0] < next_x:
                    print("CEILING EVENT at ", vertex)
                    eventToAdd.type = "CEILING"
                    ceilingEdgeToAdd = Edge()
                    ceilingEdgeToAdd.source_state = obstacle[i]
                    ceilingEdgeToAdd.target_state = obstacle[i+1]
                    eventToAdd.ceilingPointer.append(ceilingEdgeToAdd)
                
                elif vertex[0] > prior_x and vertex[0] > next_x:
                    print("OUT EVENT at ", vertex)
                    self.connectivity -= 1
                    eventToAdd.type = "OUT"

                    ceilingEdgeToAdd = Edge()
                    ceilingEdgeToAdd.source_state = obstacle[i-1]
                    ceilingEdgeToAdd.target_state = obstacle[i]
                    eventToAdd.ceilingPointer.append(ceilingEdgeToAdd)

                    floorEdgeToAdd = Edge()
                    floorEdgeToAdd.source_state = obstacle[i]
                    print("i", i)
                    print(" lenght of the obstacles", len(obstacle))
                    # i think i do this over every one
                    floorEdgeToAdd.target_state = obstacle[(i+1)%(len(obstacle))]
                    eventToAdd.floorPointer.append(floorEdgeToAdd)

                elif vertex[0] < prior_x and vertex[0] > next_x:
                    print("FLOOR EVENT at ", vertex)
                    eventToAdd.type = "FLOOR"
                    floorEdgeToAdd = Edge()
                    floorEdgeToAdd.source_state = obstacle[i-1]
                    floorEdgeToAdd.target_state = obstacle[i]
                    eventToAdd.floorPointer.append(floorEdgeToAdd)
                else:
                    print("Some other type of event at ", vertex)
                heapq.heappush(self.eventsList, (vertex[0], self.eventId, eventToAdd))
                print("Connectivity is = ", self.connectivity)
                self.eventId+=1
         
        if self.dbg == True:
            self.dbgEventsList() 

    # slice control?
    # this was the key to the whole thing
    def slice_control(self, current_event, current_intersections):
        # Input: the event, and a list of the current intersections
        # Output: Relevant Index to "current" cell 
        print("INSIDE SLICE CONTROL")
        print(current_event, current_intersections)
        event_location = current_event.location
        event_type = current_event.type

        intervals = []
        for i in range(0,len(current_intersections)-1): 
            a = current_intersections[i] 
            b = current_intersections[i+1]
            intervals.append((a,b))
        #print("Intervals", intervals)
        #print("corresponding event location", event_location)

        # flag the intervals as OK or NOT OK
        intervals_with_status = []
        safe = True
        if event_type == "IN" or event_type == "OUT":
            for i in range(0, len(intervals)):
                #print("intervals[i]", intervals[i])
                if event_location in intervals[i]:
                    safe = True 
                else:
                    safe = not safe 
                intervals_with_status.append((intervals[i], safe))
        if event_type == "FLOOR" or event_type == "CEILING":
            for i in range(0, len(intervals)):
                #print("intervals[i]", intervals[i])
                intervals_with_status.append((intervals[i], safe))
                safe = not safe

        print("intervals with status", intervals_with_status)
        safe_intervals = []
        for i in range(0, len(intervals_with_status)):
            if intervals_with_status[i][1] == True:
                safe_intervals.append(intervals_with_status[i])
        print("safe intervals", safe_intervals)

        # finally, check the indices that contain the 
        current_cell_locations = []
        for i in range(0, len(safe_intervals)):
            if event_location in safe_intervals[i][0]:
                print("index of importance", i)
                current_cell_locations.append(i)
        print("for the event type", event_type)
        print("current cell locations", current_cell_locations)

        return (current_cell_locations, safe_intervals)
       
    def find_all_intersections(self, current_event): 
        current_intersections = []
        for r_event in self.reference_events:
            r_event = r_event[2]
            #print("r_event", r_event)
            #print("r_event.ceilingPointer", r_event.ceilingPointer)
            #print("r_event.floorPointer", r_event.floorPointer)
            for edges in r_event.ceilingPointer + r_event.floorPointer:
                intersect = self.findIntersection(edges, current_event)
                current_intersections.append(intersect)

        ibot = self.findIntersection(self.botEdge, current_event)
        itop = self.findIntersection(self.topEdge, current_event)

        current_intersections.append(ibot)
        current_intersections.append(itop)
        current_intersections = [*set(current_intersections)]

        if False in current_intersections:
            current_intersections.remove(False)

        # finally sort this by second element
        current_intersections.sort(key = lambda x: x[1])
        #print("Post Filter Current Intersections", current_intersections)
        return current_intersections

    def makeCells2(self):
        initialCell = Cell()
        self.topEdge = Edge()
        self.topEdge.source_state  = (0,  self.yMax)
        self.topEdge.target_state = (self.xMax, self.yMax)

        self.botEdge = Edge()
        self.botEdge.source_state = (0,0)
        self.botEdge.target_state = (self.xMax, 0)

        initialCell.ceilingList.append(self.topEdge)
        initialCell.floorList.append(self.botEdge)

        self.connectivity = 1

        self.reference_events = self.eventsList.copy()

        print("IN MAKE CELLS 2")

        # place the initial cell into the open list
        self.open.append(initialCell)
        while len(self.eventsList) > 0:

            curr = heapq.heappop(self.eventsList)
            current_event = curr[2]
            print("\n\nPOPPING EVENTS")
            print("curr", curr, current_event)
            print("current_event.location", current_event.location)
            print("current_event.type", current_event.type)
            current_intersections = self.find_all_intersections(current_event)
            sweep_line_control = self.slice_control(current_event, current_intersections)

            if current_event.type == "IN":
                print("PROCESSING OF AN IN EVENT")
                print("sweep_line_control_indices", sweep_line_control)
                self.connectivity +=1 
                # I have an assumption right now that the lower index is always indicating the cell
                # to close, so if stuff stops working for whatever reason, that's probably what's wrong
                
                index_to_close = sweep_line_control[0][0]
                indices_to_open = sweep_line_control[0]
                print("index_to_close", index_to_close)
                print("indices_to_open", indices_to_open)

                cell_to_close = self.open[index_to_close]

                # Calculations on the cell we are CLOSING
                c = self.findIntersection(cell_to_close.ceilingList[-1], current_event)
                f = self.findIntersection(cell_to_close.floorList[-1], current_event)
                cell_to_close.ceilingList[-1].c = c
                cell_to_close.ceilingList[-1].endPoint = c
                cell_to_close.floorList[-1].f = f
                cell_to_close.floorList[-1].endPoint = f
                print("f", f)
                print("c", c)

                # close up the current cell
                self.printCell(cell_to_close)
                self.closed.append(cell_to_close)
                self.open.remove(cell_to_close)

                # two new cells are to be opened
                botCell = Cell()
                topCell = Cell()


                botCell.floorList.append(copy.copy(cell_to_close.floorList[-1]))
                botCell.floorList[-1].endPoint = None
                botCell.floorList[-1].startPoint = f

                botCell.ceilingList.append(copy.copy(current_event.ceilingPointer[-1]))
                botCell.ceilingList[-1].endPoint = None
                botCell.ceilingList[-1].startPoint = current_event.location 

                botCell.neighborList.append(cell_to_close)

                # conversely for the top cell...
                topCell.floorList.append(copy.copy(current_event.floorPointer[-1]))
                topCell.floorList[-1].endPoint = None
                topCell.floorList[-1].startPoint = current_event.location

                topCell.ceilingList.append(copy.copy(self.closed[-1].ceilingList[-1]))
                topCell.ceilingList[-1].endPoint = None
                topCell.ceilingList[-1].startPoint = c

                topCell.neighborList.append(cell_to_close)

                # append this to open IS 
                # its weird becasue you are appending linearly and the number of elements changes
                # THIS IS THE CULPRIT
                self.open.insert(indices_to_open[0],botCell)
                self.open.insert(indices_to_open[1],topCell)
    
                #self.closed[-1].neighborList.insert(0, topCell)
                #self.closed[-1].neighborList.insert(0, botCell)
                
                self.closed[-1].neighborList.append(topCell)
                self.closed[-1].neighborList.append(botCell)
                  
            elif current_event.type == "FLOOR":
                index_to_update = sweep_line_control[0][0]
                current_cell = self.open[index_to_update]
                print("\n\nself.open", self.open)
                print("sweep_line_control", sweep_line_control)
                print("index_to_update", index_to_update)
                print("Printing Current Cell")
                self.printCell(current_cell)
                # follow the instructions of the paper
                current_cell.floorList.append(copy.copy(current_event.floorPointer[-1]))


            elif current_event.type == "CEILING":
                print("PROCESSING A CEILING EDGE")
                index_to_update = sweep_line_control[0][0]
                current_cell = self.open[index_to_update]
                print("sweep_line_control", sweep_line_control)
                print("index_to_update", index_to_update)
                print("Printing Current Cell")
                self.printCell(current_cell)
                # i wish i understood why copy.copy was needed here, maybe its not
                current_cell.ceilingList.append(copy.copy(current_event.ceilingPointer[-1]))

            elif current_event.type == "OUT":
                print("PROCESSING OF THE OUT EVENT")
                self.connectivity-=1
                index_to_open = sweep_line_control[0][0]
                indices_to_close = sweep_line_control[0]

                print("index_to_open", index_to_open)
                print("indices_to_close", indices_to_close)
                botCell = self.open[indices_to_close[0]]
                topCell = self.open[indices_to_close[1]]

                f = self.findIntersection(botCell.floorList[-1], current_event)
                print("f", f)
                botCell.floorList[-1].f = f
                botCell.floorList[-1].endPoint = f

                c = self.findIntersection(topCell.ceilingList[-1], current_event)
                topCell.ceilingList[-1].c = c
                topCell.ceilingList[-1].endPoint = c

                # "next, a new cell is to be opened"....
                cellToAdd = Cell()
                cellToAdd.floorList.append(copy.copy(botCell.floorList[-1]))
                cellToAdd.ceilingList.append(copy.copy(topCell.ceilingList[-1]))

                cellToAdd.floorList[-1].startPoint = f
                cellToAdd.floorList[-1].endPoint = None

                cellToAdd.ceilingList[-1].startPoint = c
                cellToAdd.ceilingList[-1].endPoint= None
    
                self.open.insert(index_to_open, cellToAdd)

                botCell.neighborList.append(cellToAdd)
                topCell.neighborList.append(cellToAdd)

                cellToAdd.neighborList.append(botCell)
                cellToAdd.neighborList.append(topCell)

                # close the cells
                self.closed.append(botCell)
                self.closed.append(topCell)


                # remove the cells from open
                self.open.remove(botCell)
                self.open.remove(topCell)

            print("self.connectivity", self. connectivity)
            print("current_intersections", current_intersections)
        # there should just be one cell left at the last OUT event 
        self.closed.append(self.open[-1])
            

    def determineCellBounds(self, intersections, current_event):
        # given the connectivity and a list of the current slice intersections, 
        # output the Index of the active cell in Open 
        # What I really want is for this to output a tuple:
        # IN EVENT the first element in the tuple is the index of the cell to be closed 
        bounds = []
        modulo = len(intersections)%2
        if modulo == 0:
            # if number of intersections is even it is a floor or ceiling event
            L = len(intersections)
            for i in range(0, L-1):
                if i%2 == 0:
                    print("lower bound = ", intersections[i][1])
                    print("upper bound = ", intersections[i+1][1])
                    lb = intersections[i][1]
                    ub = intersections[i+1][1]
                    bounds.append( (lb, ub) )
                    print("bounds", bounds)
                    for b in bounds:
                        if current_event.location[1] == b[0] or current_event.location[1] == b[1]:
                            print("FOUND IN BOUND at INDEX == ", bounds.index(b))
                            return bounds.index(b)
        else:
            # if number of intersections is odd, its an IN/OUT event
            # every other pair of bounds represents a cell, except for the two that bound the out event also represent
            # the cell
            return_indices = []
            print("This is an IN//OUT EVENT")
            print("Event Location = ", current_event.location)
            print("AMBER IS THE BEST GENSHIN CHARACTER")
            print("Index", intersections.index(current_event.location))
            idx = intersections.index(current_event.location)
            print("Intersections = ", intersections)
            L = len(intersections)
            for i in range(0, L-1):
                if intersections[i] == current_event.location:
                    print("event intersection is ", i)
                lb = intersections[i][1]
                ub = intersections[i+1][1]
                bounds.append( (lb, ub) )

            bounds = [*set(bounds)]
            bounds.sort(key = lambda x: x[0])
            print("bounds in odd numbered case", bounds)
            for b in bounds:
                if current_event.location[1] == b[0] or current_event.location[1] == b[1]:
                    print("FOUND IN BOUND at INDEX == ", bounds.index(b))
                    return_indices.append(bounds.index(b))
            return return_indices

    def findIntersection(self, edge, event):
        #print("find intersection")
        #print("edge", edge)
        #print("event", event)

        x1,y1 = edge.source_state[0], edge.source_state[1]
        x2, y2 = edge.target_state[0], edge.target_state[1]
        #print("x1, y1", x1, y1)
        #print("x2, y2", x2, y2)

        line = LineString([(x1, y1), (x2, y2)])
        sweep_line_x = event.location[0]
        sweep_line = LineString([(sweep_line_x, -1), (sweep_line_x, self.yMax + 1)])
        status = sweep_line.intersects(line)
        if status == True:
            intersection_point = sweep_line.intersection(line)
            #print("Sweep Line Intersects Edge ?", status)
            #print("Intersection Point", intersection_point)
            return (intersection_point.x, intersection_point.y)
        else:
            return False

    def findEdgeIntersections(self, e1, e2):
        x11,y11 = e1.source_state[0], e1.source_state[1]
        x12, y12 = e1.target_state[0], e1.target_state[1]
        line = LineString([(x11, y11), (x12, y12)])

        x21,y21 = e2.source_state[0], e2.source_state[1]
        x22, y22 = e2.target_state[0], e2.target_state[1]
        line2 = LineString([(x21, y21), (x22, y22)])
        if status == True:
            intersection_point = line2.intersection(line)
            #print("Sweep Line Intersects Edge ?", status)
            #print("Intersection Point", intersection_point)
            return (intersection_point.x, intersection_point.y)
        else:
            return False

    # DEBUGGING STUFF TO MAKE MY LIFE EASIER
    def dbgEventsList(self):    
        print("\nCHECKING EVENTS LIST\n\n")
        while len(self.eventsList) > 0:
            curr = heapq.heappop(self.eventsList)
            curr = curr[2]
            self.printEvent(curr)

    def printEvent(self, event):
        # these try excepts are fine because its just for printing
        print("location = ", event.location)
        print("type = ", event.type)
        try:
            fp = event.floorPointer[0]
            print("FP = source state = %s, target state = %s"%
                        (fp.source_state, fp.target_state))
        except:
            print("no floor pointer")
        try:
            cp = event.ceilingPointer[0]
            print("CP = source state = %s, target_state = %s"% 
                    (cp.source_state, cp.target_state))
        except:
            print("no ceiling pointer")

    def printCell(self, cell):
        for ce in cell.ceilingList:
            print("CEILING EDGE")
            print("there are %s edges", len(cell.ceilingList))
            print("source state = ", ce.source_state)
            print("target state = ", ce.target_state)
            print("ce.f = ", ce.f)
            print("ce.c = ", ce.c)
            print("ce.startPoint = ", ce.startPoint)
            print("ce.endPoint = ", ce.endPoint) 
        for fe in cell.floorList:
            print("FLOOR EDGE")
            print("there are %s edges", len(cell.floorList))
            print("source state = ", fe.source_state)
            print("target state = ", fe.target_state)
            print("fe.f = ", fe.f)
            print("fe.c = ", fe.c)
            print("fe.startPoint = ", fe.startPoint)
            print("fe.endPoint = ", fe.endPoint)

        print("NeighborList: ", cell.neighborList)
        print("Visited: ", cell.visited)
        print("Cleaned: ", cell.visited)
        
        

if __name__ == "__main__":
    tdc = TDC()
    obstacles = tdc.readObstacles()
    tdc.makeEvents(obstacles)
    print("tdc.connectivity", tdc.connectivity)
    tdc.makeCells2()

    print("\n\n CHECKING THE Cells")
    for j, cell in enumerate(tdc.closed):
        print(" NEW Cell ", j, cell)
        tdc.printCell(cell)
        print(" ")
        print(" *** ")



    # do the planner here
    print("DOING THE PLANNING")
    result = planners.bfs(tdc)
    result2 = planners.dfs(tdc)
    print("result", result)

    # output waypoints
    print("\n\nGETTING THE WAYPOINTS\n\n")
    waypoints = planners.get_waypoints(tdc)

    print("\n\n DONE GETTING WAYPOINTS\n\n")
    gv = Visualizer(tdc)
    gv.printStuff()
    gv.floorAndCeilingEdges()
    gv.plotAll()
