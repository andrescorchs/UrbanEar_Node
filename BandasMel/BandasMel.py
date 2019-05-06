import numpy as np
from scipy.signal import stft


def calcFiltBanks(nfilt, freclow, frechigh, NFFT, fs = 44100, normMel = True):

        low_freq_mel = (2595 * np.log10(1 + (freclow) / 700))
        high_freq_mel = (2595 * np.log10(1 + (frechigh) / 700))  # Convert Hz to Mel

        mel_points = np.linspace(low_freq_mel, high_freq_mel, nfilt + 2)  # Equally spaced in Mel scale
        hz_points = (700 * (10**(mel_points / 2595) - 1))  # Convert Mel to Hz
        bin = np.floor((NFFT + 1) * hz_points/fs)


        # Defino los filtros mel
        fbank = np.zeros((nfilt, int(np.floor(NFFT / 2 + 1))))
        # Altura 1 #
        for m in range(1, nfilt + 1):
                f_m_minus = int(bin[m - 1])   # left
                f_m = int(bin[m])             # center
                f_m_plus = int(bin[m + 1])    # right
                norm = 2.0 / (hz_points[m + 1] - hz_points[m - 1])
                for k in range(f_m_minus, f_m):
                        if (normMel):
                                fbank[m - 1, k] = norm * (k - bin[m - 1]) / (bin[m] - bin[m - 1])
                        else:
                                fbank[m - 1, k] = (k - bin[m - 1]) / (bin[m] - bin[m - 1])
                for k in range(f_m, f_m_plus):
                        if (normMel):
                                fbank[m - 1, k] = norm * (bin[m + 1] - k) / ( bin[m + 1] - bin[m] )
                        else:
                                fbank[m - 1, k] = (bin[m + 1] - k) / (bin[m + 1] - bin[m])
        return np.float32(fbank)



def calcPotAudio(data, frame_length, frame_step, NFFT, fs = 44100, ventana = 'hann', pre_enf = True, alpha = 0.97):

        if (pre_enf):
                data = np.append( data[0], data[1:] - alpha * data[:-1] ) #aplico el filtro de primer orden (X[n] - alpha*X[n-1])
        else:
                data = np.append(data[0], data[1:])

        f, t, Zxxnorm = stft(data, fs, nperseg=frame_length, noverlap=(frame_length-frame_step), nfft = NFFT, window= ventana)

        win = get_window(ventana, int(round(frame_length)))
        Zxx = Zxxnorm*np.sum(win)
        
        return (np.abs(Zxx) ** 2) #Obtengo la densidad de potencia, podria ir multiplicada por un factor de 1/NFFT ?



def MelBandas(data, fs = 44100, f_size = 0.025, f_stride = 0.0125, nfft = 0, pre_enf = True, alpha = 0.97,
    ventana = 'hann', freclow = 0, frechigh = 22050, nfilt = 60, normMel = False):
        
	frame_length, frame_step = ( np.ceil(f_size * fs), np.ceil(f_stride * fs) )

	if (nfft == 0):
		fl = int(round(frame_length))

		NFFT = 1 << (fl-1).bit_length()
	else:
		NFFT = nfft

	pow_frames_norm =  calcPotAudio(data, frame_length, frame_step, NFFT, fs, ventana, pre_enf, alpha) #Obtengo la densidad de potencia, podria ir multiplicada por un factor de 1/NFFT ?

    win = get_window(ventana, int(round(frame_length)))
    pow_frames = pow_frames_norm/np.sum(win)
	# Defino los filtros mel
	fbank = calcFiltBanks(nfilt, freclow, frechigh, NFFT, fs, normMel)

	### Multiplico los filtros por las STFT
	filter_banks1 = np.dot(fbank, pow_frames)
	filter_banks2 = np.where(filter_banks1 == 0, np.finfo(float).eps, filter_banks1)  # Numerical Stability
	filter_banks3 = 20 * np.log10(filter_banks2)  # dB


	return filter_banks3
