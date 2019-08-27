# -*- coding: utf-8 -*-
"""
Created on Sat Sep 29 17:19:53 2018

@author: aq
"""
import matplotlib.pyplot as plt
#https://github.com/ap--/python-seabreeze
import seabreeze.spectrometers as sb
import time
import numpy as np
devices = sb.list_devices()
print(devices)
spec = sb.Spectrometer(devices[0])
#время накопления
spec.integration_time_micros(0.05e6)
wavelengths = spec.wavelengths()

def different_int_time():
	list_of_intensities = []
	#измерение времени между последовательными накоплениями спектра
	#минимум - 5 мс 
	n = 20
	start = time.time()
	for i in range(100000, 500000, 50000):
		spec.integration_time_micros(i)
		plt.plot(wavelengths, spec.intensities(correct_dark_counts = True), label = str(i))
	dt = (time.time() - start)/n
	print(dt)
	
	plt.legend()
	
n_plot = 0
def one_more_plot():
	global n_plot
	plt.plot(wavelengths, spec.intensities(correct_dark_counts = True), label = str(n_plot))
	n_plot += 1
	plt.legend()
	
def one_more_plot_zero():
	global n_plot
	plt.plot(wavelengths, spec.intensities(correct_dark_counts = True) - zero, label = str(n_plot))
	n_plot += 1
	plt.legend()
#
#mean_int = sum(list_of_intensities)/len(list_of_intensities)
#err = np.zeros(mean_int.shape)
#
#f = open('zero_count.txt', 'r')
#s = f.readline()
#f.close()
#zero_count = np.array([float(x) for x in s.split()])
#
#for i in range(n):
#	err += (mean_int - list_of_intensities[i])**2
#	err /= n
#	
#for i in range(n):
#	plt.plot(wavelengths, list_of_intensities[i])
#	
#plt.plot(wavelengths, err)

#spec.close()

