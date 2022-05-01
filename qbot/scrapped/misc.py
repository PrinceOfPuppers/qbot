import numpy as np
def compNth_ket(numQubits, n):
    x = np.zeros(2**numQubits, dtype = complex)
    x[n] = 1
    return x

def compNth_density(numQubits, n):
    size = 2**numQubits
    x = np.zeros((size,size), dtype = complex)
    x[n][n] = 1
    return x
