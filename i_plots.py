import os
import numpy as np
import pandas as pd
import mplstereonet
import matplotlib.pyplot as plt
from windrose import WindroseAxes
import matplotlib.cm as cm

'''
u = x coordinate of the vector gradient
v = x coordinate of the vector gradient
mag = the magnitude of the vector gradient is corresponding to its hypotenuse

Bearing: the horizontal angle measured east or west from true north or south.

'''
os.chdir('d:/repos/pirnacasestudy')
os.chdir('Data')

df = pd.read_csv('VectorsGradient_20230112.csv')
df['mag'] = np.sqrt (np.power(df.u, 2) + np.power(df.v , 2))


'''
Element-wise arc tangent of x1/x2 choosing the quadrant correctly.
np.degrees is equivalent to:
    
    np.arctan2(df.u,df.v) * 180/ np.pi
    
'''

df['bearing'] = np.degrees(np.arctan2(df.u,df.v))%360
df['arc_mag'] = np.degrees(np.arctan(df.mag))
#apply rescale in a way that no angle bigger than 80 is existent
rescale_factor = 90 / df.arc_mag.max()
df['arc_mag_res'] = rescale_factor * df['arc_mag'] 


'''
Wind Rose
'''

ax = WindroseAxes.from_ax()
ax.bar(df['bearing'] , df.arc_mag , opening= 0.8, edgecolor='black', cmap=cm.coolwarm)
ax.set_legend()
ax.set_title('Rose Diagram of inverse hydraulic gradients', fontsize=15)
ax.figure.savefig('RoseDiagram.jpg', dpi = 300)


# '''
# Histogram
# '''
# fig = plt.figure(figsize=(8, 4))

# ax1 = fig.add_subplot(111)
# ax1.hist(df.arc_mag, bins = 50,
#           facecolor = '#2ab0ff', edgecolor='#169acf', linewidth=1)
# ax1.grid()
# ax1.set_title('Histogram of the magnitude of hydraulic gradients')
# fig.tight_layout()
# fig.savefig('Histogram_i.jpg', dpi = 500)


'''
Stereonet
'''
# reducing datapoints
# df = df.sample(n=500, random_state=6).reset_index(drop = True)
# fig = plt.figure(figsize=(8, 8))
# ax1 = fig.add_subplot(111, projection='stereonet')
# # ax1.line(df['arc_mag'], df.bearing, c='k', label='Pole of the Planes')
# ax1.density_contourf(df['arc_mag'] , df.bearing, measurement='lines', cmap='coolwarm') 
# ax1.grid()
# ax1.set_title('Polar diagram of inverse hydraulic gradients', y = 1.1, fontsize=15)
# fig.tight_layout()
# fig.savefig('Stereonet.jpg', dpi = 500)


'''
Stereonet from scratch
contour did not work
'''

# df['rads'] = np.radians(df.bearing)
# ang_fromhorizontal = df['arc_mag'] 
# df ['ang_fromperpendicular'] = 90 - ang_fromhorizontal

# fig, ax = plt.subplots(dpi=300,subplot_kw=dict(projection='polar'))
# ax.set_theta_zero_location("N")
# ax.set_theta_direction(-1)


# r, theta = np.meshgrid(df ['ang_fromperpendicular'] , df['rads'] )
# values = theta

# ax.plot(theta, r, 'o', alpha = 0.1)
# ax.set_rmax(90)
# ax.set_rticks([90, 45, 0])

# ax.set_title('Polar diagram of hydraulic gradients_1', y = 1.1, fontsize=15)