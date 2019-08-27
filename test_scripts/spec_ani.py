# -*- coding: utf-8 -*-
"""
Created on Sat Sep 29 17:38:24 2018

live spectra 
@author: aq
"""

import matplotlib.pyplot as plt
from matplotlib import animation
import numpy as np
#https://github.com/ap--/python-seabreeze
import seabreeze.spectrometers as sb

fig = plt.figure()
ax = plt.axes(xlim=(200, 1100), ylim=(0, 14000))
line, = ax.plot([], [], lw=0.5)

def init():
    line.set_data([], [])
    return line,

devices = sb.list_devices()
print(devices)
spec = sb.Spectrometer(devices[0])
spec.integration_time_micros(0.5e6)

substract_zero = False
zero_count = np.zeros(3648, )
if substract_zero:
	f = open('zero_count.txt', 'r')
	s = f.readline()
	f.close()
	zero_count = np.array([float(x) for x in s.split()])

def handle_close(evt):
	spec.close()
	print('spec closed')

fig.canvas.mpl_connect('close_event', handle_close)

wavelengths = spec.wavelengths()

def animate(i):
    #wavelengths = spec.wavelengths()
    intensities = spec.intensities( correct_dark_counts=True)
    line.set_data(wavelengths, intensities - zero_count)
    return line,

ani = animation.FuncAnimation(fig, animate, init_func=init, 
                              frames=200, interval=100, blit=True)
plt.show()
