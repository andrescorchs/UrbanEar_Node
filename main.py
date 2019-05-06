from BandasMel.BandasMel import MelBandas
from Grabacion.Grabacion import GrabarDatos
import SPL.filtro_calculos as spl
import FiltroComp as filtro
from Comunicacion.config import levantar_configuracion
from scipy.io.wavfile import write
import numpy as np
import time
import os
import RPi.GPIO as GPIO

config = levantar_configuracion()

coefA = spl.curva_A_digital(config['fs'])
coefC = spl.curva_C_digital(config['fs'])

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(12,GPIO.OUT)

G = np.load('GComp.npy')
frecs = np.load('frecsComp.npy')
htiempo = filtro.constructefir( G, frecs, config['ncomp'], config['fs'])

### GComp es el filtro de compensacion en ganancia ###
### htiempo son los coeficientes ###

while True:
	etime = time.time()
	timestr = time.strftime("%Y%m%d-%H%M%S", time.localtime())

	audio = GrabarDatos(config['duration'], config['fs'])
	audio_np = np.reshape(audio, len(audio))

	audio_filt = filtro.overlap_add( audio_np, htiempo)

	if (config['save_audio']):
		lstAud = np.array([])
		countAud = 0
		for item in os.listdir("Audios/"):
			if not item.startswith(".") and os.path.isfile(os.path.join("Audios/", item)):
				countAud = countAud + 1
				lstAud = np.append(lstAud, item)
		if (countAud < config['cantAudios']):
			write(os.path.join("Audios/", timestr) + '.wav', config['fs'], audio_filt)
		else:
			lstAud.sort()
			os.remove(os.path.join("Audios/", lstAud[0]))
			write(os.path.join("Audios/", timestr) + '.wav', config['fs'], audio_filt)
		### Audio WAV, 10MB por minuto aprox. ###

	if (config['calcSPL'] > 0):
		A = spl.SPL(audio_filt, coefA, config['cant_SPL'], 'A')
		C = spl.SPL(audio_filt, coefC, config['cant_SPL'], 'C')

		spl_dato = np.array([np.float32(A), np.float32(C)])

		lstSPL = np.array([])
		countSPL = 0
		for item in os.listdir("ArchivosSPL/"):
			if not item.startswith(".") and os.path.isfile(os.path.join("ArchivosSPL/", item)):
				countSPL = countSPL + 1
				lstSPL = np.append(lstSPL, item)
		if (countSPL < config['CantArchSPL']):
			np.save(os.path.join("ArchivosSPL/" ,timestr + '-SPL'), spl_dato)
		else:
			lstSPL.sort()
			os.remove(os.path.join("ArchivosSPL/", lstSPL[0]))
			np.save(os.path.join("ArchivosSPL/" ,timestr + '-SPL'), spl_dato)


	if (config['calcMel'] > 0):
		mel = MelBandas(audio_filt, config['fs'], config['f_size'], config['f_stride'], config['nfft'], config['pre_enf'], 
		config['alpha'], config['ventana'], config['freclow'], config['frechigh'], config['nfilt'], config['normMel'] )

		lstMel = np.array([])
		countMel = 0

		for item in os.listdir("ArchivosMel/"):
			if not item.startswith(".") and os.path.isfile(os.path.join("ArchivosMel/", item)):
				countMel = countMel + 1
				lstMel = np.append(lstMel, item)
		if (countMel < config['CantArchMel']):
			np.save(os.path.join("ArchivosMel/", timestr + '-Mel'), mel)
		else:
			lstMel.sort()
			os.remove(os.path.join("ArchivosMel/", lstMel[0]))
			np.save(os.path.join("ArchivosMel/", timestr + '-Mel'), mel)

	endtime = time.time() - etime
	timebuffer = config['delay'] - endtime
	if (timebuffer > 0):
		time.sleep(timebuffer)

	config = levantar_configuracion()
