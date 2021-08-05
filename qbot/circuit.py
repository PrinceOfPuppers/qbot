import numpy as np

import qbot.qgates as gates
import qbot.density as d
from qbot.helpers import stateVecStr

def makeStateVec(stateList,coeff=1):
    return coeff*np.array(stateList,dtype=complex)


class Measurement:
    __slots__ =(
        'nQubits',
        'mQubits',
        'measuringTop', # boolean denoting if top n are measured or bottom n
        'postNumQubits'
    )
    def __init__(self,nQubits,mQubits,measuringTop):
        self.nQubits = nQubits
        self.mQubits = mQubits
        self.measuringTop = measuringTop

        if measuringTop:
            self.postNumQubits = mQubits
        else:
            self.postNumQubits = nQubits

class Gate:
    __slots__ = (
        'numQubits',
        'controlQubits',    # list of ints 
        'firstTargetQubit', # start of target bits (int)
        'lastTargetQubit',   # end of target bits
        'matrix',      # np.ndarray(2 dimensional) reperesenting the gate
        'ascii'        # np.ndarray of chars representing the gate
    )
    def __init__(self, numQubits, matrix: np.ndarray, firstTargetQubit: int = 0, controlQubits: [int] = None):
        
        for controlQubit in controlQubits:
            if(numQubits < controlQubit):
                raise Exception("Control Qubits must be <= numQubits")
        
        if(len(controlQubits) != len(set(controlQubits))):
            raise Exception("controlQubits must not contain duplicates")

        if(controlQubits == None):
            controlQubits = []
        
        numTargetQubits = gates._checkGate(matrix) // 2
        numControlQubits = len(controlQubits)

        if(numQubits < numTargetQubits + numControlQubits):
            raise Exception("numControlQubits + numTargetQubits(inferred from gate size) must be <= numQubits")

        self.numQubits = numQubits
        
        self.lastTargetQubit = firstTargetQubit + numTargetQubits - 1
        self.controlQubits = controlQubits.sort()
        
        if(len(controlQubits) != 0):
            gates.genMultiControlledGate(numQubits,controlQubits,firstTargetQubit,matrix)
        
        self.matrix = matrix

        #TODO: ascii instantiation

def main():
    
    initalStates = [
        makeStateVec([1,1j],2**(-1/2))
    ]

    initalProbs = [
        1
    ]
    
    initalDensity = d.statesToDensity(initalStates,initalProbs)
    numQubits = 2
    circuit = [
        Gate(numQubits, gates.cnot)
    ]

if __name__ == "__main__":
    main()