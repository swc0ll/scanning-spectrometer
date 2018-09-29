# -*- coding: utf-8 -*-
"""
Created on Sat Sep 29 17:38:24 2018

live spectra 
@author: aq
"""

import matplotlib.pyplot as plt
from matplotlib import animation
#https://github.com/ap--/python-seabreeze
import seabreeze.spectrometers as sb

fig = plt.figure()
ax = plt.axes(xlim=(200, 1100), ylim=(0, 3000))
line, = ax.plot([], [], lw=0.5)

def init():
    line.set_data([], [])
    return line,

devices = sb.list_devices()
print(devices)
spec = sb.Spectrometer(devices[0])
spec.integration_time_micros(50000)

def handle_close(evt):
	spec.close()
	print('spec closed')

fig.canvas.mpl_connect('close_event', handle_close)

wavelengths = spec.wavelengths()

def animate(i):
    #wavelengths = spec.wavelengths()
    intensities = spec.intensities( correct_dark_counts=True)
    line.set_data(wavelengths, intensities)
    return line,

ani = animation.FuncAnimation(fig, animate, init_func=init, 
                              frames=200, interval=100, blit=True)
plt.show()
