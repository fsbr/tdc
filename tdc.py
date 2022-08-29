# 
import sys
import heapq
import copy
from shapely.geometry import LineString
from visualizer import Visualizer

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
        #inputFile = open("inputfloat.txt", "r")
        inputFile = open("input.txt", "r")

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
                    ceilingEdgeToAdd.target_state = obstacle[i+1]
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
                    floorEdgeToAdd.target_state = obstacle[i+1]
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
    def makeCells(self):
        self.connectivity = 1
        self.cellCount = 0
        initialCell = Cell()
        self.topEdge = Edge()
        self.topEdge.source_state  = (0,  self.yMax)
        self.topEdge.target_state = (self.xMax, self.yMax)

        self.botEdge = Edge()
        self.botEdge.source_state = (0,0)
        self.botEdge.target_state = (self.xMax, 0)

        initialCell.ceilingList.append(self.topEdge)
        initialCell.floorList.append(self.botEdge)
        
        # this is a hack but we are gonna let it rip
        self.reference_events = self.eventsList.copy()

        while len(self.eventsList) > 0:
            curr = heapq.heappop(self.eventsList)
            current_event = curr[2]
            print("curr", curr, current_event)
            print("current_event.location", current_event.location)
            print("current_event.type", current_event.type)

            # check for intersections
            # first within the reference events
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

            # quick filtering on current_intersections
            # this notation forms the set
            current_intersections = [*set(current_intersections)]
            if False in current_intersections:
                current_intersections.remove(False)

            # finally sort this by second element
            current_intersections.sort(key = lambda x: x[1])
            print("Post Filter Current Intersections", current_intersections)
             
            #print("length of reference events", len(self.reference_events))
            # skeleton for processing "event point schedule" 
            if current_event.type == "IN" and self.cellCount == 0:
                self.connectivity+=1
                # i kind of want UNIQUE edges in the cell list
                c = self.findIntersection(initialCell.ceilingList[-1], current_event)
                f = self.findIntersection(initialCell.floorList[-1], current_event)
                initialCell.ceilingList[-1].c = c
                initialCell.ceilingList[-1].endPoint = c
                initialCell.floorList[-1].f = f
                initialCell.floorList[-1].endPoint = f
                print("f", f)
                print("c", c)
                self.printCell(initialCell)
                self.closed.append(initialCell)

                botCell = Cell()
                topCell = Cell()


                botCell.floorList.append(copy.copy(self.closed[-1].floorList[-1]))
                botCell.floorList[-1].endPoint = None
                botCell.floorList[-1].startPoint = f

                botCell.ceilingList.append(copy.copy(current_event.ceilingPointer[-1]))
                botCell.ceilingList[-1].endPoint = None
                botCell.ceilingList[-1].startPoint = current_event.location 

                botCell.neighborList.append(initialCell)


                # conversely for the top cell...
                topCell.floorList.append(copy.copy(current_event.floorPointer[-1]))
                topCell.floorList[-1].endPoint = None
                topCell.floorList[-1].startPoint = current_event.location

                topCell.ceilingList.append(copy.copy(self.closed[-1].ceilingList[-1]))
                topCell.ceilingList[-1].endPoint = None
                topCell.ceilingList[-1].startPoint = c

                topCell.neighborList.append(initialCell)

                # append this to open
                self.open.append(botCell)
                self.open.append(topCell)
    
                self.closed[-1].neighborList.insert(0, topCell)
                self.closed[-1].neighborList.insert(0, botCell)
                self.cellCount+=1

                

            #elif current_event.type == "IN" and self.cellCount !=0:
            #    self.connectivity+=1
            #    print("I HIT MY SECOND IN EVENT BUT IDK WHAT TO DO")
            #    #quit()
            elif current_event.type == "FLOOR":
                activeIndex = self.determineCellBounds(current_intersections, current_event)
                current_cell = self.open[activeIndex]
                print("Active Index", activeIndex)
                print("Printing Current Cell")
                self.printCell(current_cell)
                # follow the instructions of the paper
                current_cell.floorList.append(copy.copy(current_event.floorPointer[-1]))
                    
            elif current_event.type == "CEILING":
                activeIndex = self.determineCellBounds(current_intersections, current_event)
                current_cell = self.open[activeIndex]
                print("Active Index", activeIndex)
                print("Printing Current Cell")
                self.printCell(current_cell)
                current_cell.ceilingList.append(copy.copy(current_event.ceilingPointer[-1]))

            elif current_event.type == "OUT":
                self.connectivity -= 1
                activeIndex = self.determineCellBounds( current_intersections, current_event) 
                botCell = self.open[activeIndex[0]]
                topCell = self.open[activeIndex[1]]

                f = self.findIntersection(botCell.floorList[-1], current_event)
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
    
                self.open.insert(activeIndex[0], cellToAdd)

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

            
            else:
                print("Invalid Event Type")
       
        # there should just be one cell left at the last OUT event 
        self.closed.append(self.open[-1])

    def determineCellBounds(self, intersections, current_event):
        # given the connectivity and a list of the current slice intersections, 
        # output the Index of the active cell in Open 
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
            print("Index", intersections.index(current_event.location))
            idx = intersections.index(current_event.location)
            print("Intersections = ", intersections)
            L = len(intersections)
            for i in range(0, L-1):
                if i%2 == 0:
                    lb = intersections[i][1]
                    ub = intersections[i+1][1]
                    bounds.append( (lb, ub) )
                    print("bounds")
                if i == idx:
                    # i fucking hate this code
                    # like the if moduluo == 0 is so pointless but im too underslept to actually figure out a good solution
                    # also its just such a huge thing for what its doing
                    lb = intersections[i-1][1]
                    ub = intersections[i][1]
                    bounds.append( (lb, ub) )

                    lb = intersections[i+1][1]
                    ub = intersections[i][1]
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
        sweep_line = LineString([(sweep_line_x, -1), (sweep_line_x, 11)])
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
            print("source state = ", ce.source_state)
            print("target state = ", ce.target_state)
            print("ce.f = ", ce.f)
            print("ce.c = ", ce.c)
            print("ce.startPoint = ", ce.startPoint)
            print("ce.endPoint = ", ce.endPoint) 
        for fe in cell.floorList:
            print("FLOOR EDGE")
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
    tdc.makeCells()

    print(" CHECKING THE Cells")
    for j, cell in enumerate(tdc.closed):
        print(" NEW Cell ", j, cell)
        tdc.printCell(cell)
        print(" ")
        print(" *** ")




    gv = Visualizer(tdc)
    gv.printStuff()
    gv.floorAndCeilingEdges()
    gv.plotAll()
