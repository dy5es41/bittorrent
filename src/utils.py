#!/usr/bin/env python3
import sys
from hexdump import hexdump
from termcolor import colored

def hexdumpwithname(payload : bytes, name : str):
  """hexdump payload with name, for easy read on cli"""
  name = colored(name, 'red')
  print(name)
  hexdump(payload)
  return

def printc(message, color):
  message = colored(message, color)
  print(message)
  return 
#def printcolor(message : str, color):
#  print(colored(message
