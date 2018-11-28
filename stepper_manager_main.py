# -*- coding: utf-8 -*-
"""
Created on Tue Oct  2 23:59:10 2018

@author: aq

To convert qt5 ui file to py use following command:
pyuic5 stepper_manager_interface.ui > stepper_manager_interface.py

"""

import sys
import os
import matplotlib
# Make sure that we are using QT5
matplotlib.use('Qt5Agg')

from PyQt5 import QtCore, QtWidgets
import numpy as np
import pandas as pd
import stepper_manager_interface as ui

from StepperMotor import *
from pymata_aio.pymata3 import PyMata3
from pymata_aio.constants import Constants

import time
import seabreeze.spectrometers as sb


class Stepper_manager(ui.Ui_MainWindow, QtWidgets.QMainWindow):

	def __init__(self, board, stop_pin, stepper_x, stepper_y, 
			  virt_spec, real_spec_init):
		super().__init__()
		self.setupUi(self)
		
		self.board = board
		self.stop_pin = stop_pin
		self.board.set_pin_mode( self.stop_pin, Constants.INPUT)
		
		self.stepper_x = stepper_x
		self.stepper_y = stepper_y
		
		self.virt_spec = virt_spec
		self.real_spec_init = real_spec_init
		self.spectrometer = self.virt_spec
		
		#self.colors = [[0, 1, 0, 0.5] for x in self.db['mkm/h']]
		
		#self.checkBox.stateChanged.connect(self.setcolor)		
#		self.init_combos()
		self.init_buttons()
		self.refresh_speed()
		#self.refresh_position()
		self.show()
		
#	def pick_handle(self, event):
#		print(324)
#	def init_combos(self):
#		self.combo = [s for s in list(self.db.columns) if self.db[s].dtype == np.float64]
#		labels_n = range(1, 4)
#		combos = [self.comboBox, self.comboBox_2, self.comboBox_3]
#		for i in range(len(combos)):
#			combos[i].insertItems(len(self.combo), self.combo)
#			combos[i].setCurrentIndex(labels_n[i])
#			combos[i].currentIndexChanged.connect(self.redraw)
	
	def steppers_set_to_zero(self):
		self.stepper_x.set_position_to_zero()
		self.stepper_y.set_position_to_zero()
		self.refresh_position()
		
	def refresh_position(self):
		x = self.stepper_x.position
		y = self.stepper_y.position
		self.joystickXYLabel.setText('( {}, {} )'.format(str(x), str(y)))
		self.currentXLabel.setText('X: ' + str(x))
		self.currentYLabel.setText('Y: ' + str(y))
		#self.redraw()
		
	def refresh_speed(self):
		self.speedLabel.setText('Speed: ' + str(self.speedSlider.value()) + u' steps/click')
		#self.redraw()
		
	def init_buttons(self):
		self.setToZeroButton.clicked.connect(self.steppers_set_to_zero)
		self.moveLeftButton.pressed.connect(lambda: self.stepper_x.step(self.speedSlider.value(), 1, 
																  do_after_step=self.refresh_position))
		self.moveRightButton.pressed.connect(lambda: self.stepper_x.step(self.speedSlider.value(), -1, 
																  do_after_step=self.refresh_position))
		self.moveUpButton.pressed.connect(lambda: self.stepper_y.step(self.speedSlider.value(), -1, 
																  do_after_step=self.refresh_position))
		self.moveDownButton.pressed.connect(lambda: self.stepper_y.step(self.speedSlider.value(), 1, 
																  do_after_step=self.refresh_position))
		
#		self.moveLeftButton.pressed.connect(lambda: self.stepper_x.go_while(1, 
#																	  self.speedSlider.value(), 
#																	  self.moveLeftButton.isDown))
#		self.moveRightButton.pressed.connect(lambda: self.stepper_x.go_while(-1, 
#																	  self.speedSlider.value(), 
#																	  self.moveRightButton.isDown))
#		self.moveUpButton.pressed.connect(lambda: self.stepper_y.go_while(1, 
#																	  self.speedSlider.value(), 
#																	  self.moveUpButton.isDown))
#		self.moveDownButton.pressed.connect(lambda: self.stepper_y.go_while(-1, 
#																	  self.speedSlider.value(), 
#																	  self.moveDownButton.isDown))
		self.pointHeightEdit.textEdited.connect(self.refresh_step_dimentions)
		self.pointWidthEdit.textEdited.connect(self.refresh_step_dimentions)
		self.resolutionEdit.textEdited.connect(self.refresh_point_dimentions)
		self.stepHeightEdit.textEdited.connect(self.refresh_point_dimentions)
		self.stepWidthEdit.textEdited.connect(self.refresh_point_dimentions)
		self.stepHeightEdit.editingFinished.connect(self.refresh_point_dimentions)
		self.stepWidthEdit.editingFinished.connect(self.refresh_point_dimentions)		
		
		self.speedSlider.valueChanged.connect(self.refresh_speed)
		self.scanButton.clicked.connect(self.scan)
		self.moveToButton.clicked.connect(self.move)
		
		self.enableXCheckBox.stateChanged.connect(self.enable_motors)
		self.enableYCheckBox.stateChanged.connect(self.enable_motors)
		
		self.virtualSpecCheckBox.stateChanged.connect(self.change_spec)
	
	def change_spec(self):
		self.spectrometer.close()
		if self.virtualSpecCheckBox.isChecked():
			self.spectrometer = self.virt_spec
		else:
			self.spectrometer = self.real_spec_init()
			
	def enable_motors(self):
		print(self.board.digital_read(self.stop_pin))
		if self.enableXCheckBox.isChecked():
			self.stepper_x.enable()
		else:
			self.stepper_x.disable()
		
		if self.enableYCheckBox.isChecked():
			self.stepper_y.enable()
		else:
			self.stepper_y.disable()

	def refresh_step_dimentions(self):
		res = int(self.resolutionEdit.text())
		n = int(self.pointHeightEdit.text())
		m = int(self.pointWidthEdit.text())
		self.stepHeightEdit.setText(str(n*res))
		self.stepWidthEdit.setText(str(m*res))
		self.refresh_scan_time()
		
	def refresh_point_dimentions(self):
		height = int(self.stepHeightEdit.text())
		width = int(self.stepWidthEdit.text())
		res = int(self.resolutionEdit.text())		
		self.pointHeightEdit.setText(str(height//res))
		self.pointWidthEdit.setText(str(width//res))
		self.refresh_scan_time()
		
	def refresh_scan_time(self):
		n = int(self.pointHeightEdit.text())
		m = int(self.pointWidthEdit.text())
		scan_to_average = int(self.scanToAverageEdit.text())
		integration_time = int(self.integrationTimeEdit.text())
		scan_time = round(n*m*scan_to_average*integration_time / 1e6 /60)
		self.scanButton.setText('Scan ~' + str(scan_time) +'min')

	def move(self):
		target_x = self.targetXEdit.text()
		target_y = self.targetYEdit.text()
		
		#TODO Bad input handling
#		if not (target_x.strip().isdigit() and target_y.strip().isdigit()):
#			print('integer values expected in "Target" field')
#			return
		target_x = int(target_x)
		target_y = int(target_y)
		self.move_to(target_x, target_y)

	def move_to(self, target_x, target_y):
		self.stepper_x.get_to(target_x, do_after_step = self.refresh_position)
		self.stepper_y.get_to(target_y, do_after_step = self.refresh_position)
	
	def scan(self):
		"""
		TODO
		add correct_dark_counts and non-linear correction options checkBoxes
		"""
		self.progressBar.setEnabled(True)
		
		scan_to_average = int(self.scanToAverageEdit.text())
		integration_time = int(self.integrationTimeEdit.text())
		self.spectrometer.integration_time_micros(integration_time)
		wavelengths = self.spectrometer.wavelengths()
		step = int(self.resolutionEdit.text())		
		
		time_appendix = time.strftime("%d_%m_%Y__%H-%M-%S", time.localtime())
		file = open('specs/spec_scan_' + time_appendix + '.txt', 'w')
		file.write('#first line - comment, second - resolution n, m, third - ' +
			 'wavelengths, fourth and further - point coordinates i, j and spectra' +
			 'Integration time us: ' + str(integration_time) + 'Step - ' +
			 str(step) + '\n')
		

		n = int(self.pointHeightEdit.text())*step
		m = int(self.pointWidthEdit.text())*step
		file.write(str(n//step) + ' ' + str(m//step) + '\n')
		file.write(' '.join(['{0:.2f}'.format(x) for x in wavelengths]) + '\n')
		
		start = time.time()
		for i in range(0, n, step):
			for j in range(0, m, step):
				if self.board.digital_read(self.stop_pin):
					file.close()
					return
				self.progressBar.setProperty("value", int( (i*m+j+step)/n/m*100) )
				file.write(str(i//step) + ' ' + str(j//step) + ' ')
				self.refresh_position()
				self.move_to(j, i)
				
				intensities = np.zeros_like(wavelengths)
				for k in range(scan_to_average):
					intensities += self.spectrometer.intensities(correct_dark_counts = True)
				intensities /= scan_to_average
				file.write(' '.join(['{0:.2f}'.format(x) for x in intensities]) + '\n')
		file.close()
		scan_time = time.time() - start
		total_steps = (n//step)*(m//step)
		print('Scanning time - ', scan_time, 'sec.', total_steps,
		'steps. Speed - ', total_steps/scan_time, 'sps')
		
	def closeEvent(self, event):
		self.stepper_x.disable()
		self.stepper_y.disable()
		print('yooo')
#		if self.spectrometer != self.virt_spec:
#			self.change_spec()
		self.spectrometer.close()
		event.accept() # let the window close



class VirtualSpec():
	def __init__(self):
		self.intensities_const = [1, 2, 3]
		self.wavelengths_const = [4, 5, 6]
		self.int_time = 0.1
	def close(self):
		pass
	def intensities(self, *args, **kwargs):
		time.sleep(self.int_time)
		return self.intensities_const
	def wavelengths(self, *args, **kwargs):
		return self.wavelengths_const
	def integration_time_micros(self, time_micros, *args, **kwargs):
		self.int_time = time_micros/10e6

def spec_init():
	devices = sb.list_devices()
	print(devices)
	spec = sb.Spectrometer(devices[0])
	return spec

if __name__ == '__main__':
	
	if not 'board' in locals():
		board = PyMata3(arduino_wait = 5)

	a = StepperDrive(board, 11, 8, 9, 10, speed_limit_steps_per_sec = 30)
	b = StepperDrive(board, 2, 3, 4, 5)
	
#	if 'virtual' in sys.argv:
#		print('virtual spectrometer is being used')
#		sys.argv.remove('virtual')
#		spec = VirtualSpec()
#	elif 'virt_spec' in locals():
#		spec = VirtualSpec()
#	else:
#		devices = sb.list_devices()
#		print(devices)
#		spec = sb.Spectrometer(devices[0])
	
	virt_spec = VirtualSpec()
	
	if not QtWidgets.QApplication.instance():
		app = QtWidgets.QApplication(sys.argv)
	else:
		app = QtWidgets.QApplication.instance() 
	#app = QApplication(sys.argv)
	ex = Stepper_manager(board, 6, b, a, virt_spec, spec_init)
	#sys.exit(app.exec_())
	app.exec_()
	