import numpy as np
import sounddevice as sd
import RPi.GPIO as GPIO

def GrabarDatos(duration, fs = 44100):
	sd.default.device = 'dmic_sv'
	sd.default.samplerate = fs
	sd.default.channels = 1
	GPIO.output(12,GPIO.HIGH)
	data = sd.rec(int((duration + 1) * fs))
	print( "Grabando...")

	sd.wait()
	GPIO.output(12,GPIO.LOW)
	print ( "Fin Grabacion.")

	data = data[fs:]
	data = data - np.mean(data)
	return data
