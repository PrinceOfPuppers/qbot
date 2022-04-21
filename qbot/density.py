import numpy as np
import numpy.linalg as linalg
from qbot.helpers import ensureSquare, log2
import qbot.qgates as gates

def ketsToDensity(kets:[np.ndarray],probs: [float] = None) -> np.ndarray:
    '''converts set of kets to a density matrix'''
    if probs == None:
        return ketToDensity(kets[0])

    if len(kets) != len(probs):
        raise Exception("number of state vectors an number of probabilites must equal")

    result = np.zeros( (kets[0].shape[0],kets[0].shape[0]),dtype=complex )

    for i,ket in enumerate(kets):
        result += probs[i]* np.outer(ket,ket)

    return result

def ketToDensity(ket: np.ndarray) -> np.ndarray:
    return np.outer(ket,ket)

# def normalizeDensity(density: np.ndarray):
#     density /= np.trace(density)

def partialTrace(density:np.ndarray, nQubits, mQubits, traceN = True):
    '''
    traces nQubits if traceN is true, leaving you with the density matrix for the latter mQubits
    '''

    dimN = 2**nQubits
    dimM = 2**mQubits
    
    size = ensureSquare(density)
    
    if(dimN + dimM != size):
        raise Exception("incorrect number of qubits")
    
    axis1,axis2 = (1,3) if traceN else (0,2)

    return  np.trace(
                density.reshape(dimN,dimM,dimN,dimM), 
                axis1=axis1, axis2=axis2
            )

def partialTraceBoth(density,nQubits,mQubits):
    '''
    traces out n and m qubits seperatly (used for measurement simulation)
    '''
    numQubits = log2(ensureSquare(density))

    if(nQubits + mQubits != numQubits):
        raise Exception("incorrect number of qubits")

    dimN = 2**nQubits
    dimM = 2**mQubits
    
    return (
        np.trace(
            density.reshape(dimN,dimM,dimN,dimM), 
            axis1=1, axis2=3
        ),
        np.trace(
            density.reshape(dimN,dimM,dimN,dimM), 
            axis1=0, axis2=2
        )          
    )

def partialTraceArbitrary(density: np.ndarray, numQubits: int, systemAQubits: list[int]):
    size = ensureSquare(density)
    systemAQubits.sort()

    systemBQubits = [i for i in range(0,numQubits) if i not in systemAQubits]

    numSysAQubits = len(systemAQubits)
    numSysBQubits = len(systemBQubits)

    def stateMap(state):
        res = 0
        for i,aQubit in enumerate(systemAQubits):
            mask = 1 << numQubits - aQubit - 1
            res |= ((mask & state)!= 0) << (numQubits - 1 - i)
        for i,bQubit in enumerate(systemBQubits):
            mask = 1 << numQubits - bQubit - 1
            res |= ((mask & state) != 0) << numSysBQubits - i - 1
        return res

    swapGate = gates.genArbitrarySwap(size, stateMap)

    swappedDensity = swapGate @ density @ swapGate.conj().T

    return partialTraceBoth(swappedDensity,numSysAQubits,numSysBQubits)

def combineDensity(d1: np.ndarray, d2: np.ndarray):
    return np.kron(d1,d2)


class MeasurementResult:
    __slots__ = (
        'unMeasuredDensity', # [np.ndarray] state of the unmeasured qubits after the measurement
        'toMeasureDensity',  # [np.ndarray] state of the qubits to measure, before measurement 
        'probs',             # [float]      probabilities of getting each of the basis states
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

def measureTopNQubits(density: np.ndarray, basisDensity: list[np.ndarray], N: int) -> MeasurementResult:
    '''
    Measures the top N Qubits with respect to the provided basis (must also be density matrices)
    '''
    numQubits = log2(ensureSquare(density))

    if (numQubits == N):
        toMeasureDensity = density
        unMeasuredDensity = np.array([],dtype=complex)
    else:
        toMeasureDensity, unMeasuredDensity = partialTraceBoth(density, N, numQubits - N)
    
    probs = []
    s = 0

    for b in basisDensity:
        probs.append(
            abs(np.trace(np.matmul(toMeasureDensity, b)))
        )
        s += probs[-1]

    for i in range(0,len(probs)):
        probs[i] /= s
    
    return MeasurementResult(unMeasuredDensity,toMeasureDensity,probs)

def measureArbitrary(density: np.ndarray, basisDensity: [np.ndarray], toMeasure: [int]) -> MeasurementResult:
    '''
    Measures all qubits in toMeasure
    '''
    numQubits = log2(ensureSquare(density))

    if len(toMeasure) == numQubits:
        toMeasureDensity = density
        unMeasuredDensity = np.array([],dtype=complex)
    else:
        toMeasureDensity, unMeasuredDensity = partialTraceArbitrary(density, numQubits, toMeasure)
    
    probs = []
    s = 0

    for b in basisDensity:
        probs.append(
            abs(np.trace(np.matmul(toMeasureDensity, b)))
        )
        s += probs[-1]

    for i in range(0,len(probs)):
        probs[i] /= s
    
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
