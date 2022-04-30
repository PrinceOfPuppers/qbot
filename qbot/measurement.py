import numpy as np

from qbot.basis import Basis
from qbot.density import densityEnsambleToDensity, tensorProd, partialTraceArbitrary
from qbot.helpers import ensureSquare, log2

class MeasurementResult:
    __slots__ = (
        'unMeasuredDensity',
        'toMeasureDensity',
        'probs',
        'basisDensity',
        'basisSymbols'
    )
    def __init__(self, unMeasuredDensity: np.ndarray, toMeasureDensity: np.ndarray, probs: list[float], basisDensity: list[np.ndarray], basisSymbols:list[str]):
        self.unMeasuredDensity = unMeasuredDensity 
        self.toMeasureDensity = toMeasureDensity 
        self.probs = probs
        self.basisDensity = basisDensity
        self.basisSymbols = basisSymbols

    def __repr__(self):
        s = ''
        for i, prob in enumerate(self.probs):
            s += f'{prob} ({prob*100}%) - {self.basisSymbols[i]}\n'
        return s

    def toDensity(self):
        return densityEnsambleToDensity(self.basisDensity, self.probs)



def indexBasisStatePermutation(basis: Basis, n: int, numTensProd: int):
    state = np.ndarray([], dtype=complex)
    s = ''

    remainingIndex = n
    i = 0
    while i < numTensProd:
        index = remainingIndex%len(basis.density)
        state = tensorProd(basis.density[index], state)
        s = basis.ketSymbols[index] + s
        remainingIndex //= len(basis.density)
        i+=1

    return state, s


def measureArbitraryMultiState(density: np.ndarray, basis: Basis, toMeasure: list[int]):
    '''measures all targets in toMeasure, if basis states are smaller than the number of targets, will measure in basis of tensorproducts of basis states'''
    numQubits = log2(ensureSquare(density))

    numQubits = log2(ensureSquare(density))
    toMeasure = list(set(toMeasure))

    numTargets = len(toMeasure)
    basisQubitSize = log2(ensureSquare(basis.density[0]))

    if numTargets == 0:
        raise ValueError("measurement must have targets")

    if numTargets % basisQubitSize != 0:
        raise ValueError(f"number of qubits to measure {numTargets} must be divisable by the number of qubits in the basis states {basisQubitSize}")


    if len(toMeasure) == numQubits:
        toMeasureDensity = density
        unMeasuredDensity = np.array([],dtype=complex)
    else:
        toMeasureDensity, unMeasuredDensity = partialTraceArbitrary(density, numQubits, toMeasure)


    numTensProd = numTargets // basisQubitSize

    probs = []
    basisStates = []
    basisSymbols = []
    s = 0
    for i in range(0, len(basis.density)**numTensProd):
        basisState, basisStateSymbol = indexBasisStatePermutation(basis, i, numTensProd)
        probs.append(
            abs(np.trace(np.matmul(toMeasureDensity, basisState)))
        )
        basisStates.append(basisState)
        basisSymbols.append(basisStateSymbol)

        s += probs[-1]

    for i in range(0,len(probs)):
        probs[i] /= s
    
    return MeasurementResult(unMeasuredDensity,toMeasureDensity,probs, basisStates, basisSymbols)
