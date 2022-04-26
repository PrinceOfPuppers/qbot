import numpy as np
import numpy.linalg as linalg
from qbot.helpers import ensureSquare, log2
import qbot.qgates as gates
from typing import List, Tuple

def tensorProd(*args):
    if len(args) == 0:
        return np.ndarray([], dtype = complex)

    x = args[0]
    for i in range(1, len(args)):
        x = np.kron(x, args[i])
    return x

def ketToDensity(ket: np.ndarray) -> np.ndarray:
    return np.outer(ket,ket)

def ketsToDensity(pairs: List[Tuple[float, np.ndarray]]) -> np.ndarray:
    '''converts set of kets to a density matrix'''
    if len(pairs) == 0:
        return np.ndarray([], dtype = complex)

    if len(pairs) == 1:
        return ketToDensity(pairs[0][1])

    
    result = np.zeros( (pairs[0][1].shape[0], pairs[0][1].shape[0]),dtype=complex )

    for prob, ket in pairs:
        result += prob* np.outer(ket,ket)
    return result

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
    systemAQubits = list(set(systemAQubits))
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

def replaceArbitrary(density: np.ndarray, newDensity: np.ndarray, qubitsToReplace: list[int], numQubits: int):
    size = ensureSquare(density)
    newSize = ensureSquare(newDensity)
    newQubits = log2(newSize)
    if len(qubitsToReplace) != newQubits:
        raise ValueError(f'number of target qubits {len(qubitsToReplace)} does not equal number of provided qubits {newQubits}')

    _, density = partialTraceArbitrary(density, numQubits, qubitsToReplace)
    density = np.kron(density, newDensity)

    newQubitsOffset = numQubits - len(qubitsToReplace)
    def stateMap(state):
        res = 0

        qubitsToReplaceOffset = 0
        for i in range(numQubits):
            if qubitsToReplaceOffset < len(qubitsToReplace) and i == qubitsToReplace[qubitsToReplaceOffset]:
                mask = 1 << newQubitsOffset + qubitsToReplaceOffset
                res |= ((mask & state)!= 0) << (numQubits-1 - i)

                qubitsToReplaceOffset+=1
            else:
                mask = 1 << numQubits-1 - i + qubitsToReplaceOffset
                res |= ((mask & state)!= 0) << (numQubits-1 - i)
        return res

    swapGate = gates.genArbitrarySwap(size, stateMap)

    swappedDensity = swapGate @ density @ swapGate.conj().T

    return swappedDensity


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

def measureArbitrary(density: np.ndarray, basisDensity: List[np.ndarray], toMeasure: List[int]) -> MeasurementResult:
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

    

def densityToStateEnsable(density:np.ndarray) -> List[Tuple[float, np.ndarray]]:
    '''Returns Eiganvalue pairs corrisponding which represent probability, state pairs'''
    _ = ensureSquare(density)
    eigVals,eigVecs = linalg.eig(density)
    eigPair = []
    for i,eigVal in enumerate(eigVals):
        if eigVal != 0:
            eigPair.append( (abs(eigVal),eigVecs[i]) )
    return eigPair


def tmp():
    def stateMap(numQubits, qubitsToReplace, state):
        newQubitsOffset = numQubits - len(qubitsToReplace)
        res = 0

        qubitsToReplaceOffset = 0
        for i in range(numQubits):
            if qubitsToReplaceOffset < len(qubitsToReplace) and i == qubitsToReplace[qubitsToReplaceOffset]:
                mask = 1 << newQubitsOffset + qubitsToReplaceOffset
                res |= ((mask & state)!= 0) << (numQubits-1 - i)

                qubitsToReplaceOffset+=1
            else:
                mask = 1 << numQubits-1 - i + qubitsToReplaceOffset
                res |= ((mask & state)!= 0) << (numQubits-1 - i)
        return res

    numQubits = 5
    qubitsToReplace = [1,2]
    state = 0b10101
    x = stateMap(numQubits, qubitsToReplace, state)
    print(f"{state:0{numQubits}b}")
    print(f"{x:0{numQubits}b}")

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
