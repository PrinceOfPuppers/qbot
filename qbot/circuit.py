import numpy as np

import qbot.qgates as gates
import qbot.density as d
from qbot.helpers import stateVecStr
import qbot.basis as basis 

def makeStateVec(stateList,coeff=1):
    return coeff*np.array(stateList,dtype=complex)

#TODO: make common elements inherit from this struct
class CircuitElement:
    __slots__ = (
        'x',
        'preNumQubits',
        'postNumQubits',
    )
    def __init__(self, x: int, preNumQubits: int, postNumQubits: int):
        self.x = x
        self.preNumQubits = preNumQubits
        self.postNumQubits = postNumQubits

class Measurement(CircuitElement):
    __slots__ =(
        'basis',
        'firstTargetQubit',
        'numTargetQubits',
        'preShiftGate',
        'postShiftGate',
        'ascii',
    )
    def __init__(self, x: int, preNumQubits: int, firstTargetQubit: int, numTargetQubits: int, basis: basis.Basis):
        postNumQubits = preNumQubits - numTargetQubits
        super().__init__(x, preNumQubits, postNumQubits)
        self.basis = basis
        self.firstTargetQubit = firstTargetQubit
        self.numTargetQubits = numTargetQubits

        self.preShiftGate = gates.genShiftGate(preNumQubits,True,firstTargetQubit)

        if postNumQubits != 0:
            self.postShiftGate = gates.genShiftGate(postNumQubits,False,firstTargetQubit)
        else:
            self.postShiftGate = np.array([],dtype=complex)

        #TODO: ASCII
    
    def apply(self,density: np.ndarray) -> d.MeasurementResult:
        shifted = self.preShiftGate @ density

        result = d.measureTopNQubits(shifted ,self.basis.density, self.numTargetQubits)
        
        result.unMeasuredDensity = self.postShiftGate @ result.unMeasuredDensity
        return result




class Gate:
    __slots__ = (
        'numQubits',
        'controlQubits',    # list of ints 
        'firstTargetQubit', # start of target bits (int)
        'lastTargetQubit',   # end of target bits
        'operator',      # np.ndarray(2 dimensional) reperesenting the gate
        'ascii'        # np.ndarray of chars representing the gate
    )
    def __init__(self, x: int, numQubits: int, matrix: np.ndarray, firstTargetQubit: int = 0, controlQubits: [int] = None):
        
        if(controlQubits == None):
            controlQubits = []

        for controlQubit in controlQubits:
            if(numQubits < controlQubit):
                raise Exception("Control Qubits must be <= numQubits")
        
        if(len(controlQubits) != len(set(controlQubits))):
            raise Exception("controlQubits must not contain duplicates")

        super().__init__(x, numQubits, numQubits)

        numTargetQubits = gates._checkGate(matrix) // 2
        numControlQubits = len(controlQubits)

        if(numQubits < numTargetQubits + numControlQubits):
            raise Exception("numControlQubits + numTargetQubits(inferred from gate size) must be <= numQubits")

        self.numQubits = numQubits
        
        self.lastTargetQubit = firstTargetQubit + numTargetQubits - 1
        self.controlQubits = controlQubits.sort()
        
        if(len(controlQubits) == 0):
            self.operator = gates.genGateForFullHilbertSpace(numQubits,firstTargetQubit,matrix)
        else:
            self.operator = gates.genMultiControlledGate(numQubits,controlQubits,firstTargetQubit,matrix)
        
        #TODO: ascii instantiation
    
    def apply(self,density):
        return self.operator @ density @ self.operator.conj().T


def main():
    
    initalStates = [
        makeStateVec([1,1j],2**(-1/2))
    ]

    initalProbs = [
        1
    ]
    
    initalDensity = d.ketsToDensity(initalStates,initalProbs)
    numQubits = 2
    circuit = [
    ]

if __name__ == "__main__":
    main()