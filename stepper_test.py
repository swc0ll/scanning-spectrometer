# -*- coding: utf-8 -*-
"""
Created on Tue Oct  2 19:21:49 2018

@author: aq
"""

from StepperMotor import *
from pymata_aio.pymata3 import PyMata3
from pymata_aio.constants import Constants

board = PyMata3(arduino_wait = 5)

a = StepperDrive(board, 11, 9, 10)

a.enable()
a.get_to(100)
#board.shutdown()
