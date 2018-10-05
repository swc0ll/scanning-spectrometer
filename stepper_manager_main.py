# -*- coding: utf-8 -*-
"""
Created on Tue Oct  2 23:59:10 2018

@author: aq
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
		
	def refresh_position(self):
		x = self.stepper_x.position
		#y = self.stepper_y.position
		y = 0
		self.joystickXYLabel.setText('( {}, {} )'.format(str(x), str(y)))
		self.currentXLabel.setText('X: ' + str(x))
		#self.currentYLabel.setText('Y: ' + str(y))
		#self.redraw()
		
	def refresh_speed(self):
		self.speedLabel.setText('Speed: ' + str(self.speedSlider.value()) + u' steps/sec')
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
		self.speedSlider.valueChanged.connect(self.refresh_speed)
		self.scanButton.clicked.connect(lambda: print(self.speedSlider.value()))
		self.moveToButton.clicked.connect(self.move)
		
	def move(self):
		target_x = self.targetXEdit.text()
		target_y = self.targetYEdit.text()
		#TODO Bad input handling
#		if not (target_x.strip().isdigit() and target_y.strip().isdigit()):
#			print('integer values expected in "Target" field')
#			return
		target_x = int(target_x)
		target_y = int(target_y)
		self.stepper_x.get_to(target_x, do_after_step = self.refresh_position)
		self.stepper_y.get_to(target_y, do_after_step = self.refresh_position)
	
	
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

	a = StepperDrive(board, 11, 9, 10)
	if not QtWidgets.QApplication.instance():
		app = QtWidgets.QApplication(sys.argv)
	else:
		app = QtWidgets.QApplication.instance() 
	#app = QApplication(sys.argv)
	ex = Stepper_manager(a)
	#sys.exit(app.exec_())
	app.exec_()