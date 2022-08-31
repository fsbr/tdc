# okay so this is
import matplotlib.pyplot as plt
import numpy as np

class Visualizer:
    def __init__(self, tdcInstance):
        self.tdc = tdcInstance
    def printStuff(self):
        # prints stuff so i can figure out how the visualization is suppose to work.
        print("CELLS")
        print(self.tdc.closed)
        print("initial cell", self.tdc.closed[0])

    def floorAndCeilingEdges(self):
        for cell in self.tdc.closed:
            for f_edge in cell.floorList:
                print("edge", f_edge) 

    def getEndpoints(self, myList):
        cminx = np.Inf 
        cminy = 0 
        cmaxx = -np.Inf
        cmaxy = 0
        for edge in myList:
            # find the minimum edge.source_state
            print(" I AM BLIND")
            print("e.s.x,y", edge.source_state[0], edge.source_state[1])      
            if edge.source_state[0] < cminx:
                cminx = edge.source_state[0]
                cminy = edge.source_state[1]
            if edge.target_state[0] < cminx:
                cminx = edge.target_state[0]
                cminy = edge.target_state[1]
           
            if edge.source_state[0] > cmaxx:
                cmaxx = edge.source_state[0]
                cmaxy = edge.source_state[1]
            if edge.target_state[0] > cmaxx:
                cmaxx = edge.target_state[0]
                cmaxy = edge.target_state[1]
        print("ceiling points", cminx, cminy)
        print("ceiling points", cmaxx, cmaxy)
        return ((cminx, cminy) , (cmaxx, cmaxy))

    def plotAll(self):
        # plot obstacles
        print("self.tdc.obstacles", self.tdc.obstacles)
        for obstacle in self.tdc.obstacles:
            xs, ys = [], []
            for i, vertex in enumerate(obstacle):
                plt.scatter(vertex[0], vertex[1], color = "#AAAAAA")
                xs.append(vertex[0])
                ys.append(vertex[1])
            #plt.plot(xs+[xs[0]], ys+[ys[0]])

        colors = ["blue", "red", "green", "orange"]
        for jj, cell in enumerate(self.tdc.closed):
            # this function is trying to do too much since it is plotting and processing the cell somehow
            print("\n\n NEW CELL \n\n")
            xs, ys = [], []
            leftmost_x = np.Inf
            rightmost_x = -np.Inf 
            leftmost_y, rightmost_y = [],[]
            print(cell.ceilingList + cell.floorList)
            # what this loop is suppose to do is assign source_state and target_state based on the 
            # thing, f,c 
            for edge in cell.ceilingList + cell.floorList:
                print("\n\n edge edge edge")
                print("edge.source_state", edge.source_state)
                print("edge.target_state", edge.target_state)
                print("edge.startPoint", edge.startPoint)
                print("edge.endPoint", edge.endPoint)
                #print("edge.startPoint", edge.startPoint)
                print("\n\n edge edge edge")
                if edge.endPoint != None or edge.endPoint != False:
                    tmp = edge.endPoint
                    if edge.source_state[0] < tmp[0]:
                        edge.target_state = tmp
                    else:
                        edge.source_state = tmp

                if edge.startPoint != None or edge.startPoint != False:
                    tmp = edge.startPoint
                    if edge.source_state[0] > tmp[0]:
                        edge.target_state = tmp
                    else:
                        edge.source_state = tmp
            
                #if edge.startPoint != False or edge.startPoint!=None:
                #    tmp = edge.startPoint
                #    print("tmp", tmp)
                #    print("edge.source_state", edge.source_state)
                #    if edge.source_state[0]> tmp[0]:
                #        edge.target_state = tmp
                #    else:
                #        edge.source_state = tmp
                #else:
                #    edge.source_state = edge.source_state
                #if edge.endPoint != False or edge.endPoint != None:
                #    print("edge.endPoint", edge.endPoint)
                #    tmp = edge.endPoint
                #    print("tmp", tmp)
                #    if edge.target_state[0] < tmp[0]:
                #        edge.source_state = tmp
                #    else:
                #        edge.target_state = tmp
                #else:
                #    edge.target_state = edge.target_state
                xs = [edge.source_state[0], edge.target_state[0]]
                ys = [edge.source_state[1], edge.target_state[1]]

                print("Source Coordinate is, %s, %s"%(edge.source_state[0], edge.source_state[1]))
                print("Target Coordinate is, %s, %s"%(edge.target_state[0], edge.target_state[1]))
                

                plt.plot(xs, ys, color = colors[jj%len(colors)])

           
            ce = self.getEndpoints(cell.ceilingList)
            fe = self.getEndpoints(cell.floorList)
            print("ce", ce)
            print("fe", fe)
            vminx = [ce[0][0], fe[0][0]]
            vminy = [ce[0][1], fe[0][1]]
            vmaxx = [ce[-1][0], fe[-1][0]]
            vmaxy = [ce[-1][1], fe[-1][1]]
            plt.plot(vminx, vminy, color = colors[jj%len(colors)])
            plt.plot(vmaxx, vmaxy, color = colors[jj%len(colors)])
        #plt.axis("equal")
        plt.xlim((-10,15))
        plt.ylim((-10,15))

        plt.title("Boustro Decomposition")
        plt.show()

