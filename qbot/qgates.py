import numpy as np
from qbot.helpers import ensureSquare, log2, nthRootsOfUnity
from typing import Callable


def _checkGate(gate: np.ndarray):
    '''
    Throws error if gate isnt of valid size and shape, used to sanatize funciton input
    '''
    size = ensureSquare(gate)

    if(size & (size-1) != 0):
        raise Exception("gate size must be power of 2")

    return size


def genIdentity(numQubits):
    return np.eye(2**numQubits)


def genSimonsGate(numQubits, f: Callable):
    '''
    unitary for the blackbox function described in simon's algorithm
    U_f: |x>|b> -> |x>|b addmod2 f(x)>
    '''
    size = 2**numQubits
    arr = np.zeros((size,size), dtype = complex)
    for i in range(size):
        x = i // 2
        b = i % 2
        index = (x<<1) + (f(x) + b)%2
        arr[i][index] = 1

    return arr


def genXRotGate(theta):
    stheta = np.sin(theta/2)
    ctheta = np.cos(theta/2)
    return np.array([
        [    ctheta, -1j*stheta],
        [-1j*stheta,     ctheta]
    ], dtype = complex)


def genYRotGate(theta):
    stheta = np.sin(theta/2)
    ctheta = np.cos(theta/2)
    return np.array([
        [ctheta, -stheta],
        [stheta,  ctheta]
    ], dtype = complex)


def genZRotGate(theta):
    return np.array([
        [np.exp(-1j*theta/2), 0              ],
        [0,                   np.exp(1j*theta/2)]
    ], dtype = complex)


def genQFT(numQubits):
    assert isinstance(numQubits, int)
    size = 2**numQubits
    unityDiv = nthRootsOfUnity(size) / np.sqrt(size)
    qft = np.ones((size,size), dtype = complex)
    for i in range(0, size):
        for j in range(i, size):
            index = (i*j)%size
            qft[i][j] = unityDiv[index]
            qft[j][i] = unityDiv[index]

    return qft


def genSwapGate(numQubits, q1, q2):
    if (q1 == q2):
        return np.eye(2**numQubits)

    if(q1 > q2):
        q1, q2 = q2, q1

    if(q2 >= numQubits ):
        raise Exception("getSwapGate Requires numQubits > q2 and q1")

    # n and m in binary are bitmasks which represent the bits being flipped
    # ie) numQubits = 4, q1 = 1 has n = 0100
    n = 2**(numQubits - q1 - 1)
    m = 2**(numQubits - q2 - 1)

    gaps = [0]
    for i in range(0,numQubits):
        if(2**i != n and 2**i != m):
            gaps.append(2**i)

    start = m
    size = n - m

    swapStarts = [start]
    swapEnds = [start+size]

    for i,gap1 in enumerate(gaps):
        for j in range(0,i):
            gap2 = gaps[j]
            swapStarts.append(start+ gap1 + gap2)
            swapEnds.append(start + size + gap1 +gap2)

    swapStartIndex = 0
    swapEndIndex = 0
    swapGate = np.zeros((2**numQubits,2**numQubits),dtype = complex)
    for i in range(0,2**numQubits):
        if swapStartIndex < len(swapStarts) and i == swapStarts[swapStartIndex]:
            swapStart = swapStarts[swapStartIndex]
            swapEnd = swapEnds[swapStartIndex]

            swapGate[ swapStart ][ swapEnd ] = 1

            swapStartIndex += 1

        elif swapEndIndex < len(swapEnds) and i == swapEnds[swapEndIndex]:
            swapStart = swapStarts[swapEndIndex]
            swapEnd = swapEnds[swapEndIndex]

            swapGate[ swapEnd ][ swapStart ] = 1

            swapEndIndex += 1

        else:
            swapGate[i][i] = 1


    return swapGate


def genArbitrarySwap(hilbertDim: int, stateMap: Callable) -> np.ndarray:
    g = np.zeros((hilbertDim,hilbertDim),dtype=complex)
    for i in range(0,hilbertDim):
        g[stateMap(i)][i] = 1

    return g


def genShiftGate(numQubits: int, up:bool, numShifts = 1) -> np.ndarray:
    '''
    PLEASE NOTE: behavior can be counter intuitive, operator shifts rails up/down, not gates

    Can be thought of as many swap gates that have the effect of shifting all rails up or down with wrapping
    aka shifting up causes the 0th rail to become the last, the 1st to become the 0th, the 2nd to become the 1st, etc
    '''
    hilbertDim = 2**numQubits

    if up:
        stateMap = lambda state: (state << numShifts)%hilbertDim | (state << numShifts) // hilbertDim
    else:
        stateMap = lambda state: (state >> numShifts) | (state & (2**(numShifts) - 1)) << (numQubits-numShifts)

    return genArbitrarySwap(hilbertDim, stateMap)


def genGateForFullHilbertSpace(numQubits: int, firstTargetQubit: int, gate: np.ndarray):
    '''
    turns N qubit gate to into on acting on numQubits
    '''
    size = _checkGate(gate)

    gateNumQubits = log2(size)

    if(firstTargetQubit + gateNumQubits - 1 >= numQubits):
        raise IndexError(f"{gateNumQubits} qubit gate does not fit the {numQubits} qubit hilbertspace when started on qubit {firstTargetQubit}")


    result = gate
    if(firstTargetQubit != 0):
        I = np.eye(2**firstTargetQubit)
        result = np.kron(I,result)

    if(numQubits - gateNumQubits != firstTargetQubit):
        I = np.eye(2**( numQubits - firstTargetQubit - gateNumQubits))
        result = np.kron(result,I)

    return result


def genControlledGate(numQubits,controlQubit,firstTargetQubit,gate):
    size = _checkGate(gate)

    # size+1 qubit c-U gate, where qubit 0 is control and 1 is the first target qubit out of size target qubits
    g = np.zeros((2*size,2*size),dtype=complex)

    for i in range(0,size):
        g[i][i] = 1
    g[size:,size:] = gate


    if(firstTargetQubit != 0):

        # generates gate to effect the whole hilbertspace, where the target of the gate is in the correct place
        # however the contorl bit must be swapped before and after the gate
        g = genGateForFullHilbertSpace(numQubits,firstTargetQubit-1,g)

        #bits to swap
        q1 = firstTargetQubit - 1
        q2 = controlQubit

    else:

        # generates gate to effect the whole hilbertspace, where the target of the gate is in the correct place
        # however the contorl bit must be swapped before and after the gate
        g = genGateForFullHilbertSpace(numQubits,0,g)

        # shift down gate has the same effect as moving the g gate upwards with wrapping
        # such that the target is now qbit 0 and the control is numQubits-1
        shiftDown = genShiftGate(numQubits,False)
        shiftUp = genShiftGate(numQubits,True)
        g = shiftUp @ g @ shiftDown

        #bits to swap
        q1 = numQubits -1
        q2 = controlQubit


    swapGate = genSwapGate(numQubits,q1,q2)

    return swapGate @ g @ swapGate


def genMultiControlledGate(numQubits:int, controlQubits:list[int], firstTargetQubit:int, gate:np.ndarray):
    targetSize = _checkGate(gate)

    numControls = len(controlQubits)
    numTargets = log2(targetSize)

    controlSize = (2**numControls-1)*targetSize
    newSize = controlSize + targetSize

    # size+1 qubit c-U gate, where qubit 0 is control and 1 is the first target qubit out of size target qubits
    g = np.zeros((newSize, newSize),dtype=complex)
    for i in range(0,controlSize):
        g[i][i] = 1
    g[controlSize:,controlSize:] = gate

    if(firstTargetQubit != 0):
        # generates gate to effect the whole hilbertspace, where the target of the gate is in the correct place
        # however the contorl bit must be swapped before and after the gate
        g = genGateForFullHilbertSpace(numQubits,firstTargetQubit-numControls,g)

        for i,controlQubit in enumerate(controlQubits):
            #bits to swap
            q1 = firstTargetQubit - numControls + i
            q2 = controlQubit

            swapGate = genSwapGate(numQubits,q1,q2)
            g = swapGate @ g @ swapGate

    else:
        # generates gate to effect the whole hilbertspace, where the target of the gate is in the correct place
        # however the contorl bit must be swapped before and after the gate
        g = genGateForFullHilbertSpace(numQubits,0,g)

        # shift down gate has the same effect as moving the g gate upwards with wrapping
        # such that the target is now qbit 0 and the control is numQubits-1
        shiftDown = genShiftGate(numQubits,False,numControls)
        shiftUp = genShiftGate(numQubits,True,numControls)
        g = shiftUp @ g @ shiftDown

        for i,controlQubit in enumerate(controlQubits):
            #bits to swap
            q1 = numQubits - numControls + i
            q2 = controlQubit

            swapGate = genSwapGate(numQubits,q1,q2)
            g = swapGate @ g @ swapGate

    return g


def applyGate(gate, density) -> np.ndarray:
    return gate @ density @ gate.conj().T

