# -*- coding: utf-8 -*-
"""
Created on Fri Sep 28 00:56:23 2018

@author: aq
"""

from pymata_aio.pymata3 import PyMata3
from pymata_aio.constants import Constants
import time

class StepperDrive:
	"""
	Класс для управления шаговыми двигателями
	board - экземпляр класса PyMata3
	enable_pin, step_pin, direction_pin 
	direction = +1/-1 - направление вращения
	position - текущая позиция ш/д в шагах
	
	TODO
	direction can be only +1 or -1: protect from 0
	ENABLE/DISABLE variables
	"""

	
	def __init__(self, board, enable_pin, sleep_pin, step_pin, direction_pin, 
			  direction = 1, reverse_direction = False, position = 0, 
			  speed_limit_steps_per_sec = None):
		"""
		Инициализация переменных, настройка пинов ардуино
		"""
		self.ENABLE = 0
		self.DISABLE = 1
		
		self.board = board
		
		self.enable_pin = enable_pin
		self.motor_enabled = 1		
		self.board.set_pin_mode( self.enable_pin, Constants.OUTPUT)
		self.board.digital_write( self.enable_pin, self.ENABLE)
						  
		self.sleep_pin = sleep_pin
		self.motor_awake = 1		
		self.board.set_pin_mode( self.sleep_pin, Constants.OUTPUT)
		self.board.digital_write( self.sleep_pin, 1)		
		
		self.step_pin = step_pin
		self.board.set_pin_mode( self.step_pin, Constants.OUTPUT)
		self.board.digital_write( self.step_pin, 0)		
		
		self.direction_pin = direction_pin
		self.direction = direction
		self.board.set_pin_mode( self.direction_pin, Constants.OUTPUT)
		self.board.digital_write( self.direction_pin, self.direction)
		
		self.position = position
		self.speed_limit_sps = speed_limit_steps_per_sec
		
		
	def enable(self):
		"""
		Включение драйвера двигателя (включен по умолчанию)
		"""
		self.motor_enabled = 1
		self.board.digital_write( self.enable_pin, self.ENABLE)
		
	def disable(self):
		"""
		Выключение драйвера двигателя
		"""
		self.motor_enabled = 0
		self.board.digital_write( self.enable_pin, self.DISABLE)
		
	def awake(self):
		"""

		"""
		self.motor_awake = 1
		self.board.digital_write( self.sleep_pin, 1)
		
	def sleep(self):
		"""

		"""
		self.motor_awake = 0
		self.board.digital_write( self.sleep_pin, 0)
	
	def one_step(self, direction, do_after_step = None):
		if direction != self.direction:
			self.direction = direction
			self.board.digital_write( self.direction_pin, self.direction > 0)
		self.board.digital_write( self.step_pin, 1)	
		self.board.digital_write( self.step_pin, 0)
		self.position += self.direction
		if do_after_step:
			do_after_step()
	
	def step(self, number_of_steps, direction, stop_signal = lambda : False, 
		  do_after_step = None):
		
		if direction != self.direction:
			self.direction = direction
			self.board.digital_write( self.direction_pin, self.direction > 0)
			
		if not self.speed_limit_sps:
			for i in range(number_of_steps):
				if stop_signal():
					return
				self.board.digital_write( self.step_pin, 1)	
				self.board.digital_write( self.step_pin, 0)
				self.position += self.direction
				if do_after_step:
					do_after_step()
		else:
			#TODO add stop signal
			self.get_to(self.position+number_of_steps*direction)
			if do_after_step:
				do_after_step()		
				
	def get_to(self, target, stop_signal = lambda : False, do_after_step = None):
		"""
		target аналогично position измеряется в шагах
		"""			
		shift = target - self.position		
		direction = (1, -1)[shift < 0]
		shift = abs(shift)
		if not self.speed_limit_sps:
			self.step(shift, direction, stop_signal, do_after_step)
		else:
			#TODO do after step
			condition = lambda x: x != target
			self.go_while(direction, self.speed_limit_sps, condition)
			if do_after_step:
				do_after_step()		
		
	def set_position_to_zero(self):
		self.position = 0
		
	def go_while(self, direction, steps_per_second, condition):
		"""
		Заставляет двигатель шагать с заданной скоростью, пока не выполнится 
		условие condition (callback функция). Позволяет реализовать остановку 
		по нажатию кнопки в приложении или по срабатыванию концевого датчика.
		def my_condition(position):
		"""
		interval = 1/steps_per_second
		while condition(self.position):
			self.one_step(direction)
			self.board.sleep(interval)
			
	def go_for_some_time(self, direction, steps_per_second, period):
		start = time.time()
		start_position = self.position
		self.go_while(direction, steps_per_second, lambda x: period > time.time() - start)
		end_position = self.position
		return (end_position - start_position)/period
	