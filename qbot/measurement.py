import numpy as np

from qbot.basis import Basis
from qbot.probVal import ProbVal
from qbot.density import densityEnsambleToDensity, tensorProd, partialTraceArbitrary, interweaveDensities
from qbot.helpers import ensureSquare, log2

from typing import Union

class MeasurementResult:
    __slots__ = (
        'unMeasuredDensity',
        'probs',
        'basisDensity',
        'basisSymbols',
        'newState'
    )
    def __init__(self, unMeasuredDensity: np.ndarray, probs: list[float], basisDensity: list[np.ndarray], basisSymbols:list[str], newState = None):
        self.unMeasuredDensity = unMeasuredDensity
        self.probs = probs
        self.basisDensity = basisDensity
        self.basisSymbols = basisSymbols
        self.newState = newState

    def __repr__(self):
        s = ''
        for i, prob in enumerate(self.probs):
            s += f'{self.basisSymbols[i]}- {prob} ({prob*100}%)\n'
        return s

    def toDensity(self):
        return densityEnsambleToDensity(self.probs, self.basisDensity)

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
        unMeasuredDensity = densityEnsambleToDensity(pv.probs, [m.unMeasuredDensity for m in pv.values])

        # note we assume that if one MeasurementResult has a newState, then they all do
        if meas.newState is not None:
            newState = densityEnsambleToDensity(pv.probs, [m.newState for m in pv.values])
            return MeasurementResult(unMeasuredDensity, newProbs, meas.basisDensity, meas.basisSymbols, newState)

        return MeasurementResult(unMeasuredDensity, newProbs, meas.basisDensity, meas.basisSymbols)


def tensorPermute(numTensProd: int, n: int, d: Union[list[np.ndarray], Basis]):
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

def permuteBasis(numTensProd: int, n: int, basis: Basis):
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


class MeasurementIndexError(Exception):
    pass

def measureArbitraryMultiState(state: np.ndarray, basis: Basis, toMeasure = None, returnState = True):
    '''measures all targets in toMeasure, if basis states are smaller than the number of targets, will measure in basis of tensorproducts of basis states'''
    numQubits = log2(ensureSquare(state))

    if toMeasure is None:
        numTargets = numQubits
    else:
        if isinstance(toMeasure,set):
            toMeasure = list(toMeasure)
        else:
            toMeasure = list(set(toMeasure))

        for target in toMeasure:
            if target < 0 or target > numQubits - 1:
                raise MeasurementIndexError(f"measurement target {target} outside of valid range [{0}, {numQubits - 1}]", target, 0, numQubits - 1)

        numTargets = len(toMeasure)

    basisQubitSize = log2(ensureSquare(basis.density[0]))

    if numTargets == 0:
        raise ValueError("measurement must have targets")

    if numTargets % basisQubitSize != 0:
        raise ValueError(f"number of qubits to measure {numTargets} must be divisable by the number of qubits in the basis states {basisQubitSize}")


    if toMeasure is None or len(toMeasure) == numQubits:
        systemA = state
        systemB = np.array([], dtype=complex)

    else:
        systemA, systemB = partialTraceArbitrary(state, numQubits, toMeasure)

    numTensProd = numTargets // basisQubitSize

    probs = []
    basisStates = []
    basisSymbols = []
    s = 0
    for i in range(0, len(basis.density)**numTensProd):
        basisState, basisStateSymbol = permuteBasis(numTensProd, i, basis)
        probs.append(
            abs(np.trace(np.matmul(systemA, basisState)))
        )
        basisStates.append(basisState)
        basisSymbols.append(basisStateSymbol)

        s += probs[-1]

    for i in range(0,len(probs)):
        probs[i] /= s

    if returnState:
        measured = densityEnsambleToDensity(probs, basisStates)
        if toMeasure is None:
            return MeasurementResult(systemA, probs, basisStates, basisSymbols, measured)
        return MeasurementResult(systemA, probs, basisStates, basisSymbols, interweaveDensities(measured, systemB, toMeasure))
    return MeasurementResult(systemA, probs, basisStates, basisSymbols)

