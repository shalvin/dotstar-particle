#!/usr/bin/python

import time
import threading
from dotstar import Adafruit_DotStar
from colour import Color


NUM_PIXELS 	= 120
FPS			= 20.0
DATAPIN   	= 10
CLOCKPIN	= 11

s_run 		= True

class Strip(threading.Thread):
	pixelBuffer = [Color()] * NUM_PIXELS
	pixelBufferLock = threading.Lock()

	def init(self):
		self.strip = Adafruit_DotStar(NUM_PIXELS, DATAPIN, CLOCKPIN)
		self.strip.begin()
		self.strip.setBrightness(64)
		self.strip.clear()

	def run(self):
		while s_run:
			self.pixelBufferLock.acquire()
			for i in range(0, len(self.pixelBuffer)):
				c = self.pixelBuffer[i]
				r = int(c.red * 255)
				g = int(c.green * 255)
				b = int(c.blue * 255)
				rgb = ((r & 0xff) << 16) | ((g & 0xff) << 8) | (b & 0xff)
				self.strip.setPixelColor(i, rgb)
			self.pixelBufferLock.release()
			self.strip.show()
			time.sleep(1.0 / FPS)

	def setBuffer(self, value, index, length=0, step=1):
		self.pixelBufferLock.acquire()
		for i in range(index, index + length, step):
			self.pixelBuffer[i] = value
		self.pixelBufferLock.release()

	def getBuffer(self):
		self.pixelBufferLock.acquire()
		outStr = ''
		for i in range(0, len(self.pixelBuffer)):
			outStr += '-' if self.pixelBuffer[i] == 0 else '+'
		self.pixelBufferLock.release()
		return outStr

strip = Strip()
strip.init()
strip.start()


def tryStrToInt(stringValue, defaultValue):
	try:
		ret = int(stringValue)
	except ValueError:
		return defaultValue
	return ret

def tryStrToFloat(stringValue, defaultValue):
	try:
		ret = float(stringValue)
	except ValueError:
		return defaultValue
	return ret

s_color = Color()

while s_run:
	input = raw_input('8==D ~ ')
	input = input.lower()
	input = input.strip()
	inputSplit = input.split()

	if len(inputSplit) < 1:
		continue

	func = inputSplit[0]
	argv = inputSplit[1:] if len(inputSplit) > 1 else []
	argc = len(argv) 

	if func == 'q' or func == 'stop' or func == 'exit':
		s_run = False
		strip.join()
	elif func == 's' or func == 'set':
		if argc < 1:
			print "set <index> [length=1] [step=1]"
			continue
		index = tryStrToInt(argv[0], 0)
		length = 1
		step = 1
		if argc > 1:
			length = tryStrToInt(argv[1], length)
		if argc > 2:
			step = tryStrToInt(argv[2], step)
		strip.setBuffer(s_color, index, length, step)
		print strip.getBuffer()
	elif func == 'c' or func == 'color' or func == 'colour':
		if argc == 3:
			r = tryStrToFloat(argv[0], 0.0)
			g = tryStrToFloat(argv[1], 0.0)
			b = tryStrToFloat(argv[2], 0.0)
			s_color = Color(rgb=(r, g, b))
			print str(s_color)
		else:
			print "color <r> <g> <b>"
			continue
	else:
		print "Not a function"
