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

    def plotAll(self):
        # plot obstacles
        print("self.tdc.obstacles", self.tdc.obstacles)
        for obstacle in self.tdc.obstacles:
            xs, ys = [], []
            for i, vertex in enumerate(obstacle):
                plt.scatter(vertex[0], vertex[1], color = "#AAAAAA")
                xs.append(vertex[0])
                ys.append(vertex[1])
            plt.plot(xs+[xs[0]], ys+[ys[0]])


        for cell in self.tdc.closed:
            print("\n\n NEW CELL \n\n")
            xs, ys = [], []
            for edge in cell.ceilingList + cell.floorList:
                if edge.startPoint != None:
                    source_state = edge.startPoint
                else:
                    source_state = edge.source_state
                if edge.endPoint != None:
                    target_state = edge.endPoint
                else:
                    target_state = edge.target_state
                xs = [source_state[0], target_state[0]]
                ys = [source_state[1], target_state[1]]
                print("xs", xs)
                print("ys", ys)
    
                plt.plot(xs,ys)
        #plt.axis("equal")
        plt.xlim((-10,15))
        plt.ylim((-10,15))

        plt.title("Boustro Decomposition")
        plt.show()

