import numpy as np
from scipy.spatial import Voronoi, voronoi_plot_2d
import matplotlib.pyplot as plt
points = np.array([ [3,5], [6,3], [8,4], [7,6], [5,7]])


vor = Voronoi(points)
vor2 = Voronoi(vor.vertices)

fig = voronoi_plot_2d(vor2)
plt.show()


