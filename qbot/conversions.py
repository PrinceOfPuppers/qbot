import numpy as np
import numpy.linalg as linalg
from qbot.helpers import ensureSquare

def statesToDensity(stateVecs:[np.ndarray],probs: [float]):
    '''converts a state vector to a density matrix'''
    result = np.zeros( (stateVecs[0].shape[0],stateVecs[0].shape[0]),dtype=complex )

    for i,stateVec in enumerate(stateVecs):
        result += probs[i]* np.outer(stateVec,stateVec)

    return result


def partialTrace(array:np.ndarray, nQubits, mQubits, traceN = True):
    '''
    traces nQubits if traceN is true, leaving you with the density matrix for the latter mQubits
    '''
    shape = array.shape

    dimN = 2**nQubits
    dimM = 2**mQubits
    
    size = ensureSquare(array)
    
    if(dimN + dimM != size):
        raise Exception("incorrect number of qubits")
    
    axis1,axis2 = (0,2) if traceN else (1,3)

    return  np.trace(
                array.reshape(dimN,dimM,dimN,dimM), 
                axis1=axis1, axis2=axis2
            )

def densityToStateEnsable(densityMatrix:np.ndarray):
    _ = ensureSquare(densityMatrix)
    eigVals,eigVecs = linalg.eig(densityMatrix)
    eigPair = []
    for i,eigVal in enumerate(eigVals):
        if eigVal != 0:
            eigPair.append( (eigVal,eigVecs[i]) )
    return eigPair


if __name__ == "__main__":
    density = statesToDensity([ np.array([1,0],dtype=complex),np.array([0,1],dtype=complex) ],[3/4,1/4])

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