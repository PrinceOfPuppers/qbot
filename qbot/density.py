import numpy as np
import numpy.linalg as linalg
from qbot.helpers import ensureSquare, log2
import qbot.qgates as gates
from typing import List, Tuple

def tensorProd(*args):
    if len(args) == 0:
        return np.array([], dtype = complex)

    x = None
    i = 0
    while i < len(args):
        if args[i].size != 0:
            x = args[i]
            i+=1
            break
        i+=1
    while i < len(args):
        if args[i].size != 0:
            x = np.kron(x, args[i])
        i+=1

    return x if x is not None else np.array([], dtype = complex)

def tensorExp(state, n):
    return tensorProd(*n*[state])

def ketToDensity(ket: np.ndarray) -> np.ndarray:
    return np.outer(ket,ket)

def ketsToDensity(kets:list[np.ndarray],probs: list[float] = None) -> np.ndarray:
    '''converts set of kets to a density matrix'''
    if probs == None:
        return ketToDensity(kets[0])

    if len(kets) != len(probs):
        raise Exception("number of state vectors an number of probabilites must equal")

    result = np.zeros( (kets[0].shape[0],kets[0].shape[0]),dtype=complex )

    for i,ket in enumerate(kets):
        result += probs[i]* np.outer(ket,ket)

    return result

def densityEnsambleToDensity(probs: list[float], densities: list[np.ndarray]):
    if len(probs) != len(densities):
        raise Exception("number of state vectors an number of probabilites must equal")

    result = np.zeros( densities[0].shape ,dtype=complex )

    for i,density in enumerate(densities):
        result += probs[i]* density

    return result


def ketsToDensityZipped(pairs: List[Tuple[float, np.ndarray]]) -> np.ndarray:
    '''converts set of kets to a density matrix'''
    if len(pairs) == 0:
        return np.array([], dtype = complex)

    if len(pairs) == 1:
        return ketToDensity(pairs[0][1])

    
    result = np.zeros( (pairs[0][1].shape[0], pairs[0][1].shape[0]),dtype=complex )

    for prob, ket in pairs:
        result += prob* np.outer(ket,ket)
    return result

def normalizeDensity(density: np.ndarray):
    return density / np.trace(density)

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
    if systemAQubits[0] < 0 or systemAQubits[-1] > numQubits-1:
        raise IndexError()

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

def replaceArbitrary(density: np.ndarray, newDensity: np.ndarray, qubitsToReplace: list[int]):
    size = ensureSquare(density)
    numQubits = log2(size)
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
                mask = 1 << numQubits -1 - newQubitsOffset - qubitsToReplaceOffset
                res |= ((mask & state)!= 0) << (numQubits-1 - i)

                qubitsToReplaceOffset+=1
            else:
                mask = 1 << numQubits-1 - i + qubitsToReplaceOffset
                res |= ((mask & state)!= 0) << (numQubits-1 - i)
        return res

    swapGate = gates.genArbitrarySwap(size, stateMap)

    swappedDensity = swapGate @ density @ swapGate.conj().T

    return swappedDensity


    

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
            print(f"{i}")
            if qubitsToReplaceOffset < len(qubitsToReplace) and i == qubitsToReplace[qubitsToReplaceOffset]:
                x= numQubits -1 - newQubitsOffset - qubitsToReplaceOffset
                print(f'here1 {x}')
                mask = 1 << x
                print(f"mask {mask:0{numQubits}b}")
                res |= ((mask & state)!= 0) << (numQubits-1 - i)

                qubitsToReplaceOffset+=1
            else:
                print('here2')
                mask = 1 << numQubits-1 - i + qubitsToReplaceOffset
                print(f"mask {mask:0{numQubits}b}")
                res |= ((mask & state)!= 0) << (numQubits-1 - i)
        return res

    numQubits = 2
    qubitsToReplace = [0]
    state = 0b01
    x = stateMap(numQubits, qubitsToReplace, state)
    print(f"{state:0{numQubits}b}")
    print(f"{x:0{numQubits}b}")

if __name__ == "__main__":
    tmp()
    exit()
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
