import numpy as np


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



def genGateForFullHilbertSpace(numQubits: int, firstTargetQubit: int, gate: np.ndarray):
    '''
    turns N qubit gate to into on acting on numQubits
    '''
    if(gate.ndim!=2):
        raise Exception("gate must be 2 dimensional")
    shape = gate.shape
    
    if(shape[0]!=shape[1]):
        raise Exception("gate must be square")
    
    if(shape[0] & (shape[0]-1) != 0):
        raise Exception("gate size must be power of 2")

    size = round(np.log2(shape[0]))

    if(firstTargetQubit + size - 1 >= numQubits):
        raise Exception("numQubits must be > firstTargetQubit + size - 1")

    result = gate
    if(firstTargetQubit != 0):
        I = np.eye(2**firstTargetQubit)
        result = np.kron(I,result)
    
    if(numQubits - size != firstTargetQubit):
        I = np.eye(2**( numQubits - firstTargetQubit - size))
        result = np.kron(result,I)

    return result


def genControledGate(numQubits, controlQubit, targetQubit, singleQubitGate):

    if(targetQubit != 0):
        # 2 qubit c-U gate, where qubit 0 is control and 1 is target
        g = np.array(
            [
                [1,0,0,0],
                [0,1,0,0],
                [0,0,singleQubitGate[0][0], singleQubitGate[0][1]],
                [0,0,singleQubitGate[1][0], singleQubitGate[1][1]]
            ]
            ,dtype = complex
        )
        # generates gate to effect the whole hilbertspace, where the target of the gate is in the correct place
        # however the contorl bit must be swapped before and after the gate
        g = genGateForFullHilbertSpace(numQubits,targetQubit-1,g)
        #bits to swap
        q1 = targetQubit - 1
        q2 = controlQubit
    else:
        # 2 qubit c-U gate, where qubit 1 is control and 0 is target
        g = np.array(
            [
                [1,0,0,0],
                [0,singleQubitGate[0][0],0,singleQubitGate[0][1]],
                [0,0,1,0],
                [0,singleQubitGate[1][0],0, singleQubitGate[1][1]]
            ]
            ,dtype = complex
        )
        # generates gate to effect the whole hilbertspace, where the control of the gate is in the correct place
        # however the target bit must be swapped before and after the gate
        g = genGateForFullHilbertSpace(numQubits,controlQubit-1,g)
        #bits to swap
        q1 = controlQubit -1
        q2 = targetQubit
    

    swapGate = genSwapGate(numQubits,q1,q2)

    return swapGate @ g @ swapGate

def genMultiControledGate(numQubits, controlQubits, targetQubit, singleQubitGate):
    pass


def main():
    # 2 qubit example
    qubits = np.array([1,0,0,0],dtype=complex)


    #print(genSingleQubitGate(2,0,H))

    #sI = genSwapGate(3,0,1)
    s = genSwapGate(2,0,1)
    #print(s)
    #also_sI = genTwoQubitGate(3,0,s)
    #print(sI == also_sI)
    #for i in range(3,7):
    #    for j in range(0,i-1):
    #        H3 = genGateForFullHilbertSpace(i,j,H)
            #print(np.array_equal(H3))
    #print(Icnot)
    #print(sI@ Icnot @sI)
    #genControledGate(3,1,1,pauliY)

    
    #genGateForFullHilbertSpace(3,1,s)
#
    #for i in range(0,)

if __name__ == "__main__":
    main()