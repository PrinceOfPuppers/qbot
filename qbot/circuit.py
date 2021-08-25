import numpy as np

import qbot.qgates as gates
import qbot.density as d
from qbot.helpers import boundsOverlap, log2, stateVecStr
import qbot.basis as basis 

def makeStateVec(stateList,coeff=1):
    return coeff*np.array(stateList,dtype=complex)

#TODO: make common elements inherit from this struct
class CircuitElement:
    __slots__ = (
        'x',
        'firstTargetQubit',
        'numTargetQubits',
        'lastTargetQubit',
        'preNumQubits',
        'postNumQubits',
    )
    def __init__(self, x: int, firstTargetQubit: int, numTargetQubits: int, preNumQubits: int, postNumQubits: int):
        self.x = x
        self.firstTargetQubit = firstTargetQubit
        self.numTargetQubits = numTargetQubits
        self.lastTargetQubit = firstTargetQubit + numTargetQubits - 1
        self.preNumQubits = preNumQubits
        self.postNumQubits = postNumQubits

class Measurement(CircuitElement):
    __slots__ =(
        'basis',
        'preShiftGate',
        'postShiftGate',
    )
    def __init__(self, x: int, preNumQubits: int, firstTargetQubit: int, basis: basis.Basis):
        numTargetQubits = basis.numQubits
        postNumQubits = preNumQubits - numTargetQubits

        if(firstTargetQubit < 0):
            raise Exception("First Target Qubit Must be at Least 0")
        if(numTargetQubits+firstTargetQubit > preNumQubits):
            raise Exception("All Inputs to Measurement Must be on Qubits")

        super().__init__(x, firstTargetQubit, numTargetQubits, preNumQubits, postNumQubits)
        self.basis = basis

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


class Gate(CircuitElement):
    __slots__ = (
        'numQubits',
        'controlQubits',    # list of ints 
        'operator',      # np.ndarray(2 dimensional) reperesenting the gate
    )
    def __init__(self, x: int, numQubits: int, matrix: np.ndarray, firstTargetQubit: int = 0, controlQubits: [int] = None):
        if(controlQubits == None):
            controlQubits = []

        if(firstTargetQubit < 0):
            raise Exception("First Target Qubit Must be at Least 0")

        numTargetQubits = log2(gates._checkGate(matrix))
        if(numTargetQubits+firstTargetQubit > numQubits):
            print(f"{numTargetQubits=}")
            print(f"{firstTargetQubit=}")
            print(f"{numQubits=}")
            raise Exception("All Inputs of Gate Must Be on Qubits")

        for controlQubit in controlQubits:

            if(numQubits <= controlQubit):
                raise Exception("Control Qubit Indices Must be < numQubits")

            if(firstTargetQubit <= controlQubit and controlQubit < firstTargetQubit + numTargetQubits):
                raise Exception("Control Qubit Must Not Be Target Qubit")
        
        if(len(controlQubits) != len(set(controlQubits))):
            raise Exception("controlQubits must not contain duplicates")

        super().__init__(x, firstTargetQubit, numTargetQubits, numQubits, numQubits)
        self.numQubits = numQubits
        
        self.controlQubits = controlQubits.sort()
        
        if(len(controlQubits) == 0):
            self.operator = gates.genGateForFullHilbertSpace(numQubits,firstTargetQubit,matrix)
        else:
            self.operator = gates.genMultiControlledGate(numQubits,controlQubits,firstTargetQubit,matrix)
        
        #TODO: ascii instantiation
    
    def apply(self,density):
        return self.operator @ density @ self.operator.conj().T


# final type is for valist of control qubits (optional)
_types = [str, int, int, int, str, str, int]
_maxIndexTypes = len(_types) - 1

def deserializeCircuitElement(eleType: str, x: int, preNumQubits: int, firstTargetQubit: int, 
                              basisName: str, baseGateName: str, *args: int):

    if ( eleType == "Gate" ):
        try:
            gate = gates.gateDict[baseGateName]
        except:
            raise Exception(f"Invalid Gate Type {baseGateName}") from None
        controlQubits = [*args]

        return Gate(x, preNumQubits, gate, firstTargetQubit, controlQubits)

    elif (eleType == "Measurement"):
        try:
            measurementBasis = basis.basisDict[basisName]
        except:
            raise Exception(f"Invalid Basis {basisName}") from None

        return Measurement(x, preNumQubits, firstTargetQubit, measurementBasis)

    else:
        raise Exception("Invalid Circuit Element Type")

def addElementToCircuit(circuit: [CircuitElement], element: CircuitElement):
    '''
    Appends element to circuit, throws error if element placement violates placement conditions
    '''
    for ele in circuit:
        if ele.x == element.x:
            raise Exception(f"Circuit Elements Cannot Share X pos {ele.x}")

    circuit.append(element)


def deserializeCircuit(circuitStr: str):
    circuitEleStrs = circuitStr.strip('\n').split('\n')
    circuit = []
    for circuitEleStr in circuitEleStrs:
        try:
            args = [_types[min(i,_maxIndexTypes)](s) for i,s in enumerate(circuitEleStr.strip(' ').split(' '))]
        except:
            raise Exception(f"Error Parsing Serialized Circuit Element {circuitEleStr}") from None

        if (len(args) < len(_types) - 1):
            raise Exception(f"Not Enough Args in Serialized Circuit Element: {args}")

        addElementToCircuit(circuit, deserializeCircuitElement(*args))
    return circuit


def main():
    print(deserializeCircuit("Gate 3 5 1 - H\nGate 4 5 2 - X 0 1\n"))
    

if __name__ == "__main__":
    main()