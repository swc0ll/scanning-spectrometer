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
import scipy.misc
import os

def file_import(file_name = 'spec_scan_16_11_2018__18-22-33.txt', 
			 substract_zero = False, zero_count_file = 'zero_count.txt', k= 1):
	pass

def draw_map(file_name = 'spec_scan_16_11_2018__18-22-33.txt', 
			 substract_zero = False, zero_count_file = 'zero_count.txt', k= 1,
			 draw = True):
	zero_count = np.zeros(3648, )
	if substract_zero:
		f = open(zero_count_file, 'r')
		s = f.readline()
		f.close()
		zero_count = np.array([float(x) for x in s.split()])/k
	
	start = time.time()
	f = open(file_name, 'r')
	print(f.readline())
	n, m = [int(x) for x in f.readline().split()]
	wavelengths = np.array([float(x) for x in f.readline().split()])
	spec = np.zeros((n, m, wavelengths.size))
	try:
		for i in range(n):
			for j in range(m):
				line = f.readline().split()
				k, l = [int(x) for x in line[:2]]
				a = [float(x) for x in line[2:]]
				spec[k,l] = np.array(a)-zero_count
	except:
		print('not full data')
	last_i = i - 1
	
	print(time.time() - start)
	
	img = np.zeros((n,m))
	for i in range(n):
		for j in range(m):
			img[i,j] = spec[i,j].sum()
	
	spec = spec[::-1,:,:]
			
	if spec.min() < 0:
		spec -= spec.min()
	
	def make_img(wl_in_rgb):
		start1 = time.time()
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
		return rgb_img
	
	wl_in_rgb = np.array([wl.wavelength_to_rgb(wave) for wave in wavelengths]) / 255
	rgb_img = make_img(wl_in_rgb)
	
	if draw:
		fig = plt.figure(constrained_layout=True)
		gs = fig.add_gridspec(1, 3)
		f_ax1 = fig.add_subplot(gs[:, 0])
		f_ax2 = fig.add_subplot(gs[:, 1:])
		f_ax2.set_ylim(spec.min(), spec.max())
		
		f_ax1.imshow(rgb_img) #img, cmap = 'gray')
		line, = f_ax2.plot(wavelengths, spec[n//2, m//2])
		
		break_point = 600
		black_points = 0
		for i in range(n):
			for j in range(m):
				if max(spec[i,j,:]) < break_point:
					black_points += 1
		print('black points fraction', black_points/n/m, n, m)

		def onclick(event):
	#		try:	
	#			if event.inaxes == f_ax1:
	#				line.set_ydata(spec[int(event.ydata), int(event.xdata)])
	#				fig.canvas.draw()				
	#			elif event.inaxes == f_ax2:
	#				highlighted_wl = np.zeros_like(wl_in_rgb)
	#				nonlocal rgb_img 
	#				center = event.xdata
	#				for i in wavelengths:
	#					if  center - 10 < wavelengths[i] < center +10:
	#						highlighted_wl[i] = np.array([1, 1, 1])
	#				rgb_img = make_img(highlighted_wl)
	#			print('%s %s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
	#	          (event.canvas, 'double' if event.dblclick else 'single', event.button,
	#	           event.x, event.y, event.xdata, event.ydata))
	
	
			if event.inaxes == f_ax1:
				line.set_ydata(spec[int(event.ydata), int(event.xdata)])
				fig.canvas.draw()				
			elif event.inaxes == f_ax2:
				highlighted_wl = np.zeros_like(wl_in_rgb)
				nonlocal rgb_img 
				center = event.xdata
				for i in range(len(wavelengths)):
					if  (center-1) < wavelengths[i] < (center+1):
						highlighted_wl[i] = np.array([1, 1, 1])
				rgb_img = make_img(highlighted_wl)
				f_ax1.imshow(rgb_img[:,:,0], cmap = 'nipy_spectral')
				fig.canvas.draw()
			else:
				rgb_img = make_img(wl_in_rgb)
				f_ax1.imshow(rgb_img)
				fig.canvas.draw()
	
		cid = fig.canvas.mpl_connect('button_press_event', onclick)
	else:		
		img_file_name = '.'.join([file_name.split(sep = '.')[0], 'jpg'])
		scipy.misc.toimage(rgb_img, cmin=0.0, cmax=1.0).save(img_file_name)

if __name__ == '__main__':
	pass
	#draw_map()
	
	#draw_map('spec_scan_06_12_2018__15-41-59.txt', True, 'zero_count_50000.0us.txt')
#print(img.max(), img.min())
