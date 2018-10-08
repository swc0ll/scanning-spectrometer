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
	def __init__(self, stepper_x = None, stepper_y = None, spectrometer = None):
		super().__init__()
		self.setupUi(self)
		
		self.stepper_x = stepper_x
		self.stepper_y = stepper_y
		self.spectrometer = spectrometer
		
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
		self.moveUpButton.pressed.connect(lambda: self.stepper_y.step(self.speedSlider.value(), 1, 
																  do_after_step=self.refresh_position))
		self.moveDownButton.pressed.connect(lambda: self.stepper_y.step(self.speedSlider.value(), -1, 
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
		self.resolutionEdit.textEdited.connect(self.refresh_step_dimentions)
		self.stepHeightEdit.textEdited.connect(self.refresh_point_dimentions)
		self.stepWidthEdit.textEdited.connect(self.refresh_point_dimentions)
		self.stepHeightEdit.editingFinished.connect(self.refresh_step_dimentions)
		self.stepWidthEdit.editingFinished.connect(self.refresh_step_dimentions)		
		
		self.speedSlider.valueChanged.connect(self.refresh_speed)
		self.scanButton.clicked.connect(self.scan)
		self.moveToButton.clicked.connect(self.move)
		
		self.enableXCheckBox.stateChanged.connect(self.enable_motors)
		self.enableYCheckBox.stateChanged.connect(self.enable_motors)
		
	def enable_motors(self):
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
		
	def refresh_point_dimentions(self):
		height = int(self.stepHeightEdit.text())
		width = int(self.stepWidthEdit.text())
		res = int(self.resolutionEdit.text())		
		self.pointHeightEdit.setText(str(height//res))
		self.pointWidthEdit.setText(str(width//res))

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
		
		integration_time = int(self.integrationTimeEdit.text())
		self.spectrometer.integration_time_micros(integration_time)
		wavelengths = self.spectrometer.wavelengths()
		
		time_appendix = time.strftime("%d_%b_%Y_%H-%M-%S", time.gmtime())
		file = open('spec_scan_' + time_appendix + '.txt', 'w')
		file.write('#first line - comment, second - resolution n, m, third - ' +
			 'wavelengths, fourth and further - point coordinates i, j and spectra\n')
		
		step = int(self.resolutionEdit.text())
		n = int(self.pointHeightEdit.text())*step
		m = int(self.pointWidthEdit.text())*step
		file.write(str(n) + ' ' + str(m) + '\n')
		file.write(' '.join([str(x) for x in wavelengths]) + '\n')
		for i in range(0, n, step):
			for j in range(0, m, step):
				self.progressBar.setProperty("value", int( (i*n+(j+1)*step)/n/m*100) )
				file.write(str(i//step) + ' ' + str(j//step) + ' ')
				self.refresh_position()
				self.move_to(j, i)
				intensities = self.spectrometer.intensities(correct_dark_counts = True)
				file.write(' '.join([str(x) for x in intensities]) + '\n')
		file.close()
	
	def closeEvent(self, event):
		print('yooo')
		self.spectrometer.close()
		event.accept() # let the window close

		
#		self.pushButton_3.clicked.connect(lambda: self.switch(self.comboBox, self.comboBox_2))
#		self.pushButton.clicked.connect(lambda: self.switch(self.comboBox_2, self.comboBox_3))
#		self.pushButton_2.clicked.connect(lambda: self.switch(self.comboBox_3, self.comboBox))
		
#	def switch(self, a, b):
#		t = a.currentIndex()
#		a.setCurrentIndex( b.currentIndex() )
#		b.setCurrentIndex( t )
#		self.redraw()
		
#	def setcolor(self):
#		print(self.checkBox.checkState())
#		op = self.db['SEM (РЭМ)'].copy()
#		print(op, 1)
#		if not self.checkBox.checkState():
#			op = ~op.isnull()
#		print(op)
#		c_cold = min(self.db['mkm/h'])
#		c_hot = max(self.db['mkm/h'])
#		
#		for i in range(0, len(self.db['mkm/h'])):
#			print(i)
#			self.colors[i] = [0, (self.db['mkm/h'].values[i] - c_cold)/(c_hot - c_cold), 0, 1*op.values[i]]
#		print(self.colors)
#		self.redraw()
#		
#	def redraw(self):		
#		self.sc.compute_figure(self.db[self.comboBox.currentText()], 
#						 self.db[self.comboBox_2.currentText()], 
#						 self.db[self.comboBox_3.currentText()], 
#						 self.colors,
#						 self.comboBox.currentText(), 
#						 self.comboBox_2.currentText(), 
#						 self.comboBox_3.currentText())
		

if __name__ == '__main__':
	#board = PyMata3(arduino_wait = 5)

	a = StepperDrive(board, 11, 8, 9, 10)
	b = StepperDrive(board, 2, 3, 4, 5)
	
	devices = sb.list_devices()
	print(devices)
	spec = sb.Spectrometer(devices[0])
	
	if not QtWidgets.QApplication.instance():
		app = QtWidgets.QApplication(sys.argv)
	else:
		app = QtWidgets.QApplication.instance() 
	#app = QApplication(sys.argv)
	ex = Stepper_manager(a, b, spec)
	#sys.exit(app.exec_())
	app.exec_()
	