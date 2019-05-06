import numpy as np
import scipy.signal
import math

alfa = np.array([[100, 99.1], [98.3, 97.3]])  #matriz factor de calibracion: curvaAfreq, curvaCfreq; curvaAdig, curvaCdig

def pow2_old(a):
    if a > 1:
        for i in range(1, a):
            if  (2**i >= a):
                return 2**i
            else:
                return 1

def pow2(a):
    return 1<<(a-1).bit_length()

def bilinear_zpk(z,p,k,fs):
    z=np.atleast_1d(z)
    p=np.atleast_1d(p)
    degree= len(p) - len(z)
    fs2 = 2.0*fs
    z_z= (fs2 +z)/(fs2-z)
    p_z= (fs2 +p)/(fs2-p)
    z_z= np.append(z_z, -np.ones(degree))
    k_z= k*np.real(np.prod(fs2-z)/np.prod(fs2-p))
    return z_z, p_z, k_z

def curva_A_digital(fs = 44100):
    f1 = 20.6
    f4 = 12200.0
    f2 = 107.7
    f3 = 737.9

    w1c = 2*np.pi*f1*(-1)
    w4c = 2*np.pi*f4*(-1)
    w2c = 2*np.pi*f2*(-1)
    w3c = 2*np.pi*f3*(-1)

    z = np.array([0, 0, 0, 0], dtype=np.float64)
    p = np.array([w1c, w1c, w4c, w4c, w2c, w3c])
    k = (2*np.pi*f4)**2

    #no se puede usar en raspberry, no esta disponible en la version de scipy
    #se definio la funcion de scipy de forma local como bilinear_zpk()
    zd, pd, kd = bilinear_zpk(z,p,k,fs)
    sos_a = scipy.signal.zpk2sos(zd,pd,kd)

    return sos_a

def curva_C_digital(fs = 44100):
    f1 = 20.6
    f4 = 12200.0

    w1c = 2*np.pi*f1*(-1)
    w4c = 2*np.pi*f4*(-1)

    z = np.array([0, 0], dtype=np.float64)
    p = np.array([w1c, w1c, w4c, w4c])
    k = (2*np.pi*f4)**2

    #no se puede usar en la raspberry, no esta disponible en la version de scipy
    #se definio la funcion de scipy de forma local como bilinear_zpk()
    zd, pd, kd = bilinear_zpk(z,p,k,fs)
    sos_c = scipy.signal.zpk2sos(zd,pd,kd)

    return sos_c


def SPL(signal, coef, cant, curva):
    # calcula el SPL
    global alfa
    leq = np.zeros(cant)
    ventana = int(signal.size/cant)

    for k in range(cant):
        sig_k = signal[k*ventana : (k+1)*ventana]
        filtrado = scipy.signal.sosfilt(coef, sig_k )
        N = float(ventana)
        pot = np.sum(np.square(filtrado))
        if (curva == 'A'):
            leq[k] = alfa[0, 1] + 10*math.log10(pot/N)
        else:
            leq[k] = alfa[1, 1] + 10*math.log10(pot/N)
    return leq
