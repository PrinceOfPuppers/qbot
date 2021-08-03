import numpy as np
from qbot.helpers import ensureSquare

# static 1 qubit gates
Identity = np.eye(2)

Hadamard = (1/np.sqrt(2)) * np.array(
    [
        [1, 1],
        [1, -1]
    ]
    ,dtype = complex
)

pauliX =  np.array(
    [
        [0, 1],
        [1, 0]
    ]
    ,dtype = complex
)

pauliY =  np.array(
    [
        [0, -1j],
        [1j, -0]
    ]
    ,dtype = complex
)

pauliZ =  np.array(
    [
        [1, 0],
        [0, -1]
    ]
    ,dtype = complex
)

# static 2 qubit gates
cnot = np.array(
    [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0 ,0, 0, 1],
        [0 ,0, 1, 0]
    ]
    ,dtype = complex
)


#static 3 qubit gates
toffoli = np.array(
    [
        [1, 0, 0, 0, 0, 0 ,0, 0],
        [0, 1, 0, 0, 0, 0 ,0, 0],
        [0, 0, 1, 0, 0, 0 ,0, 0],
        [0, 0, 0, 1, 0, 0 ,0, 0],
        [0, 0, 0, 0, 1, 0 ,0, 0],
        [0, 0, 0, 0, 0, 1 ,0, 0],
        [0, 0, 0, 0, 0, 0 ,0, 1],
        [0, 0, 0, 0, 0, 0 ,1, 0],
    ]
    ,dtype = complex
)

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


def genShiftGate(numQubits,up:bool):
    '''
    PLEASE NOTE: behavior can be counter intuitive, operator shifts rails up/down, not gates

    Can be thought of as many swap gates that have the effect of shifting all rails up or down with wrapping
    aka shifting up causes the 0th rail to become the last, the 1st to become the 0th, the 2nd to become the 1st, etc
    '''
    hilbertDim = 2**numQubits

    if up:
        stateMap = lambda state: 2*state%hilbertDim | 2*state // hilbertDim
    else:
        stateMap = lambda state: (state >> 1) | (state & 1) << (numQubits-1)

    g = np.zeros((hilbertDim,hilbertDim),dtype=complex)
    for i in range(0,hilbertDim):
        g[stateMap(i)][i] = 1
    
    return g

def genGateForFullHilbertSpace(numQubits: int, firstTargetQubit: int, gate: np.ndarray):
    '''
    turns N qubit gate to into on acting on numQubits
    '''
    size = _checkGate(gate)

    gateNumQubits = int(round(np.log2(size)))


    if(firstTargetQubit + gateNumQubits - 1 >= numQubits):
        raise Exception("numQubits must be > firstTargetQubit + size - 1")

    result = gate
    if(firstTargetQubit != 0):
        I = np.eye(2**firstTargetQubit)
        result = np.kron(I,result)
    
    if(numQubits - gateNumQubits != firstTargetQubit):
        I = np.eye(2**( numQubits - firstTargetQubit - gateNumQubits))
        result = np.kron(result,I)

    return result


#def genControledGate(numQubits, controlQubit, targetQubit, singleQubitGate):
#
#    if(targetQubit != 0):
#        # 2 qubit c-U gate, where qubit 0 is control and 1 is target
#        g = np.array(
#            [
#                [1,0,0,0],
#                [0,1,0,0],
#                [0,0,singleQubitGate[0][0], singleQubitGate[0][1]],
#                [0,0,singleQubitGate[1][0], singleQubitGate[1][1]]
#            ]
#            ,dtype = complex
#        )
#        # generates gate to effect the whole hilbertspace, where the target of the gate is in the correct place
#        # however the contorl bit must be swapped before and after the gate
#        g = genGateForFullHilbertSpace(numQubits,targetQubit-1,g)
#        #bits to swap
#        q1 = targetQubit - 1
#        q2 = controlQubit
#    else:
#        # 2 qubit c-U gate, where qubit 1 is control and 0 is target
#        g = np.array(
#            [
#                [1,0,0,0],
#                [0,singleQubitGate[0][0],0,singleQubitGate[0][1]],
#                [0,0,1,0],
#                [0,singleQubitGate[1][0],0, singleQubitGate[1][1]]
#            ]
#            ,dtype = complex
#        )
#        # generates gate to effect the whole hilbertspace, where the control of the gate is in the correct place
#        # however the target bit must be swapped before and after the gate
#        g = genGateForFullHilbertSpace(numQubits,controlQubit-1,g)
#        #bits to swap
#        q1 = controlQubit -1
#        q2 = targetQubit
#    
#
#    swapGate = genSwapGate(numQubits,q1,q2)
#
#    return swapGate @ g @ swapGate


def genControledGate(numQubits,controlQubit,firstTargetQubit,gate):
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





def genMultiControledGate(numQubits, controlQubits, targetQubit, singleQubitGate):
    pass




if __name__ == "__main__":
    numQubits = 4
    hilbertDim = 2**numQubits
    up = lambda state: 2*state%hilbertDim | 2*state // hilbertDim
    down = lambda state: (state >> 1) | (state & 1) << (numQubits-1)

    for i in range(0,hilbertDim):
        print(f"{i:04b}",f"{up(i):04b}",f"{down(i):04b}",up(down(i))==i,down(up(i))==i )