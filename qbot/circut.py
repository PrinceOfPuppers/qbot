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


class CircutElement:
    __slots__ = (
        'type',     # str: 'gate' or 'measurement'
        'operator', # array or measurement struct
    )

    def __init__(self, operator, args=()):
        self.type = 'array' if type(operator) == np.ndarray else 'funcPointer'
        self.operator = operator
    

def main():
    
    initalStates = [
        makeStateVec([1,1j],2**(-1/2))
    ]
    initalProbs = [
        1
    ]
    
    initalDensity = d.statesToDensity(initalStates,initalProbs)

    circut = [
        CircutElement(gates.cnot)
    ]

    for ele in circut:
        print(ele.type)

if __name__ == "__main__":
    main()