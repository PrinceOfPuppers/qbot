import numpy as np

from qbot.basis import Basis
from qbot.probVal import ProbVal
from qbot.density import densityEnsambleToDensity, tensorProd, partialTraceArbitrary
from qbot.helpers import ensureSquare, log2

from typing import Union

class MeasurementResult:
    __slots__ = (
        'unMeasuredDensity',
        'probs',
        'basisDensity',
        'basisSymbols'
    )
    def __init__(self, unMeasuredDensity: np.ndarray, probs: list[float], basisDensity: list[np.ndarray], basisSymbols:list[str]):
        self.unMeasuredDensity = unMeasuredDensity 
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

    @staticmethod
    def fromProbVal(pv: ProbVal):
        assert len(ProbVal.probs) > 0

        newProbs = []
        meas = pv.values[0]
        assert isinstance(meas, MeasurementResult)
        newProbs = meas.probs.copy()
        for i in range(1, len(pv.probs)):
            prob = pv.probs[i]
            meas = pv.values[i]
            assert isinstance(meas, MeasurementResult)
            assert len(meas.probs) == len(newProbs)
            for measProb in meas.probs:
                newProbs[i] += prob*measProb

        s = sum(newProbs)
        for i in range(len(newProbs)):
            newProbs[i] /= s

        # note we are assuming that the basis for all measurements in probval are the same, asserting this would require alot of comparisons
        unMeasuredDensity = densityEnsambleToDensity([m.unMeasuredDensity for m in pv.values], pv.probs)

        # TODO: normalize?

        return MeasurementResult(unMeasuredDensity, newProbs, meas.basisDensity, meas.basisSymbols)





def tensorPermute(d: Union[list[np.ndarray], Basis], n: int, numTensProd: int):
    state = np.array([], dtype=complex)

    if isinstance(d, Basis):
        d = d.density

    remainingIndex = n
    i = 0
    while i < numTensProd:
        index = remainingIndex%len(d)
        state = tensorProd(d[index], state)
        remainingIndex //= len(d)
        i+=1

    return state

def permuteBasis(basis: Basis, n: int, numTensProd: int):
    state = np.array([], dtype=complex)
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


def measureArbitraryMultiState(density: np.ndarray, basis: Basis, toMeasure: list[int] = None):
    '''measures all targets in toMeasure, if basis states are smaller than the number of targets, will measure in basis of tensorproducts of basis states'''
    numQubits = log2(ensureSquare(density))

    numQubits = log2(ensureSquare(density))

    if toMeasure is None:
        numTargets = numQubits
    else:
        numTargets = len(toMeasure)

    basisQubitSize = log2(ensureSquare(basis.density[0]))

    if numTargets == 0:
        raise ValueError("measurement must have targets")

    if numTargets % basisQubitSize != 0:
        raise ValueError(f"number of qubits to measure {numTargets} must be divisable by the number of qubits in the basis states {basisQubitSize}")


    if toMeasure is None or len(toMeasure) == numQubits:
        toMeasureDensity = density
    else:
        toMeasure = list(set(toMeasure))
        toMeasureDensity, _ = partialTraceArbitrary(density, numQubits, toMeasure)


    numTensProd = numTargets // basisQubitSize

    probs = []
    basisStates = []
    basisSymbols = []
    s = 0
    for i in range(0, len(basis.density)**numTensProd):
        basisState, basisStateSymbol = permuteBasis(basis, i, numTensProd)
        probs.append(
            abs(np.trace(np.matmul(toMeasureDensity, basisState)))
        )
        basisStates.append(basisState)
        basisSymbols.append(basisStateSymbol)

        s += probs[-1]

    for i in range(0,len(probs)):
        probs[i] /= s
    
    return MeasurementResult(toMeasureDensity,probs, basisStates, basisSymbols)
