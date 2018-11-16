# -*- coding: utf-8 -*-
"""
Created on Mon Nov 12 15:03:42 2018

@author: aq
"""

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.gridspec as gridspec
import wl_to_rgb as wl
import time

start = time.time()
f = open('spec_scan_15_11_2018__16-39-57.txt', 'r')
print(f.readline())
n, m = [int(x) for x in f.readline().split()]
wavelengths = np.array([float(x) for x in f.readline().split()])
spec = np.zeros((n, m, wavelengths.size))
for i in range(n):
	for j in range(m):
		line = f.readline().split()
		k, l = [int(x) for x in line[:2]]
		a = [float(x) for x in line[2:]]
		spec[k,l] = np.array(a)
print(time.time() - start)

img = np.zeros((n,m))
for i in range(n):
	for j in range(m):
		img[i,j] = spec[i,j].sum()
		
if spec.min() < 0:
	spec -= spec.min()

start1 = time.time()
wl_in_rgb = np.array([wl.wavelength_to_rgb(wave) for wave in wavelengths]) / 255
rgb_img = np.zeros((n,m,3))
for i in range(n):
	for j in range(m):
		col = wl_in_rgb.copy()
		col[:,0] *= spec[i,j,:]
		col[:,1] *= spec[i,j,:]
		col[:,2] *= spec[i,j,:]
		rgb_img[i,j] = np.ones((1, wavelengths.size)).dot(col).reshape(3)
rgb_img /= rgb_img.max()
print(2, time.time() - start1)

fig = plt.figure(constrained_layout=True)
gs = fig.add_gridspec(1, 3)
f_ax1 = fig.add_subplot(gs[:, 0])
f_ax2 = fig.add_subplot(gs[:, 1:])
f_ax2.set_ylim(spec.min(), spec.max())

f_ax1.imshow(rgb_img) #img, cmap = 'gray')
line, = f_ax2.plot(wavelengths, spec[n//2, m//2])

def onclick(event):
	try:	
		print(event.inaxes == f_ax1)
		
		print('%s %s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
          (event.canvas, 'double' if event.dblclick else 'single', event.button,
           event.x, event.y, event.xdata, event.ydata))
		line.set_ydata(spec[int(event.ydata), int(event.xdata)])
		fig.canvas.draw()
	except:
		pass

cid = fig.canvas.mpl_connect('button_press_event', onclick)

#print(img.max(), img.min())
