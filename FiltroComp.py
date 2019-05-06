import scipy.signal
from scipy.io import wavfile
from scipy.optimize import fmin
import matplotlib.pyplot as plt
import numpy as np

def constructefir(H,f,N=1024,fs=44100.0, norm=1):
    #defino un intervalo de frecuencias lineal e interpolo a partir de eso

    wlin = np.pi*f/(fs/2) #mapeo al intervalo 0 pi 
    wk = np.pi*np.arange(0, N/2 + 1) /(N/2+1)
    Hw = np.interp(wk,wlin,H)

    h = np.real(np.fft.irfft(Hw)) #FIR muestreado a partir de ift

    if norm:
        h = h/np.max(h)
    return h


def overlap_add(x, b, norm=0):

    #power of 2 immediately higher than 2*M for optimizing fft process
    M = b.shape[0]
    N = 2<<(M-1).bit_length()
    L = N - M
    Nx = x.shape[0]
    offsets = range(0, Nx, L)

    res = np.zeros(Nx+N)

    H = np.fft.rfft(b, n=N)
    if norm:
        H = H/np.amax(H)

    # overlap and add
    for i in offsets:
        yt = np.fft.rfft( x[i:i+L], n=N ) * H
        iyt = np.real( np.fft.irfft(yt , n=N))
        res[i:i+N] += iyt
    return np.float32(res[ int(M/2) : Nx + int(M/2) ])
