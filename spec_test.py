# -*- coding: utf-8 -*-
"""
Created on Sat Sep 29 17:19:53 2018

@author: aq
"""
import matplotlib.pyplot as plt
#https://github.com/ap--/python-seabreeze
import seabreeze.spectrometers as sb
import time

devices = sb.list_devices()
print(devices)
spec = sb.Spectrometer(devices[0])
#время накопления
spec.integration_time_micros(10000)
wavelengths = spec.wavelengths()

list_of_intensities = []
#измерение времени между последовательными накоплениями спектра
#минимум - 5 мс 
n = 10
start = time.time()
for i in range(n):
	list_of_intensities.append(spec.intensities(correct_dark_counts = True))
dt = (time.time() - start)/n
print(dt)

for i in range(n):
	plt.plot(wavelengths, list_of_intensities[i])
spec.close()
