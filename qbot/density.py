import numpy as np
import numpy.linalg as linalg
from qbot.helpers import ensureSquare
import qbot.qgates as gates

def ketsToDensity(kets:[np.ndarray],probs: [float] = None):
    '''converts a state vector to a density matrix'''
    probs = [1] if probs == None else probs

    if len(kets) != len(probs):
        raise Exception("number of state vectors an number of probabilites must equal")

    result = np.zeros( (kets[0].shape[0],kets[0].shape[0]),dtype=complex )

    for i,ket in enumerate(kets):
        result += probs[i]* np.outer(ket,ket)

    return result


def partialTrace(density:np.ndarray, nQubits, mQubits, traceN = True):
    '''
    traces nQubits if traceN is true, leaving you with the density matrix for the latter mQubits
    '''

    dimN = 2**nQubits
    dimM = 2**mQubits
    
    size = ensureSquare(density)
    
    if(dimN + dimM != size):
        raise Exception("incorrect number of qubits")
    
    axis1,axis2 = (0,2) if traceN else (1,3)

    return  np.trace(
                density.reshape(dimN,dimM,dimN,dimM), 
                axis1=axis1, axis2=axis2
            )

def partialTraceBoth(density,nQubits,mQubits):
    '''
    traces out n and m qubits seperatly (used for measurement simulation)
    '''

    dimN = 2**nQubits
    dimM = 2**mQubits
    
    size = ensureSquare(density)
    
    if(dimN + dimM != size):
        raise Exception("incorrect number of qubits")

    return (
        np.trace(
            density.reshape(dimN,dimM,dimN,dimM), 
            axis1=0, axis2=2
        ),          
        np.trace(
            density.reshape(dimN,dimM,dimN,dimM), 
            axis1=1, axis2=3
        )
    )

class MeasurementResult:
    __slots__ = (
        'unMeasuredDensity', # [np.ndarray] state of the unmeasured qubits after the measurement
        'toMeasureDensity',  # [np.ndarray] state of the qubits to measure, before measurement 
        'probs',     # [float]      probabilities of getting each of the basis states
    )
    def __init__(self, unMeasuredDensity, toMeasureDensity, probs):
        self.unMeasuredDensity = unMeasuredDensity 
        self.toMeasureDensity = toMeasureDensity 
        self.probs = probs
    def __repr__(self):
        return (
            f'MeasurementResult:\n'
            f'unMeasuredDensity: \n{np.array_repr(self.unMeasuredDensity)}\n'
            f'toMeasureDensity: \n{np.array_repr(self.toMeasureDensity)}\n'
            f'probs: \n{self.probs.__repr__()}\n'
        )

def measureTopNQubits(density: np.ndarray, basisDensity: [np.ndarray], N: int) -> MeasurementResult:
    '''
    Measures the top N Qubits with respect to the provided basis (must also be density matrices)
    '''
    numQubits = density.shape[0] // 2

    if (numQubits == N):
        toMeasureDensity = density
        unMeasuredDensity = np.array([],dtype=complex)
    else:
        toMeasureDensity, unMeasuredDensity = partialTraceBoth(density, N, numQubits - N)
    
    probs = []

    for b in basisDensity:
        probs.append(
            abs(np.trace(np.matmul(density, b)))
        )
    
    return MeasurementResult(unMeasuredDensity,toMeasureDensity,probs)


    

def densityToStateEnsable(density:np.ndarray) -> [(float, np.ndarray)]:
    '''Returns Eiganvalue pairs corrisponding which represent probability, state pairs'''
    _ = ensureSquare(density)
    eigVals,eigVecs = linalg.eig(density)
    eigPair = []
    for i,eigVal in enumerate(eigVals):
        if eigVal != 0:
            eigPair.append( (abs(eigVal),eigVecs[i]) )
    return eigPair

if __name__ == "__main__":
    density = ketsToDensity([ np.array([1j,0],dtype=complex),np.array([0,1j],dtype=complex) ],[3/4,1/4])

    print(density)
    #print(partialTrace(density,1,1,False))

    reconstructed = np.zeros((density.shape[0],density.shape[1]),dtype=complex)
    for pair in densityToStateEnsable(density):
        print(pair)
        reconstructed += pair[0] * np.outer(pair[1],pair[1])

    print(reconstructed)
    density = reconstructed

    reconstructed = np.zeros((density.shape[0],density.shape[1]),dtype=complex)
    for pair in densityToStateEnsable(density):
        print(pair)
        reconstructed += pair[0] * np.outer(pair[1],pair[1])

    print(reconstructed)