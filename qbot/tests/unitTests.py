import unittest

import numpy as np
import qbot.qgates as gates

class testGates(unittest.TestCase):
    def test_swapCreationInverse(self):
        for numQubits in range(2,5):
            identity = gates.genIdentity(numQubits)
            for q1 in range(0,numQubits):
                for q2 in range(0,numQubits):
                    s = gates.genSwapGate(numQubits,q1,q2)
                    areEqual = np.array_equal(identity,s@s)
                    self.assertTrue(areEqual)

    def test_conditionalCreation(self):
        createdCnot = gates.genControledGate(2,0,1,gates.pauliX)
        
        areEqual = np.array_equal(gates.cnot,createdCnot)

        self.assertTrue(areEqual)


    def test_swapCnotHadamard(self):
        # test exploits the fact a cnot with the target and control swapped is the same as the cnot 
        # in the hadamard transformed basis        
        createdCnot = gates.genControledGate(2,0,1,gates.pauliX)
        H2 = np.kron(gates.Hadamard,gates.Hadamard)
        
        createdCnotHadamardBasis = H2 @ createdCnot @ H2
        
        # we compare the above with simply a swapped cnot
        s = gates.genSwapGate(2,0,1)
        swappedCnot = s @ gates.cnot @ s

        areEqual = np.allclose(createdCnotHadamardBasis,swappedCnot)
        self.assertTrue(areEqual)
    
    def test_shiftUpGate(self):
        
        stateMap = lambda state: 2*state%hilbertDim | 2*state // hilbertDim

        for numQubits in range(2,6):
            hilbertDim = 2**numQubits
            shiftUp = gates.genShiftGate(numQubits,True)
            for i in range(0,hilbertDim):
                vec = np.zeros(hilbertDim)
                vec[i]=1
                shifted = shiftUp.dot(vec)
                index = np.where(shifted==1)[0][0]
                self.assertEqual(index,stateMap(i))
    
    def test_shiftDownGate(self):
        stateMap = lambda state,numQubits: (state >> 1) | (state & 1) << (numQubits-1)
        for numQubits in range(2,6):
            hilbertDim = 2**numQubits
            shiftDown= gates.genShiftGate(numQubits,False)
            for i in range(0,hilbertDim):
                vec = np.zeros(hilbertDim)
                vec[i]=1
                shifted = shiftDown.dot(vec)
                index = np.where(shifted==1)[0][0]
                self.assertEqual(index,stateMap(i,numQubits))

    #TODO: create general version of genControlled gate which works on N qubit gates
    #def test_toffoli(self):
    #    createdCnot = gates.genControledGate(2,0,1,gates.pauliX)
    #    createdToffoli = gates.genControledGate(3,0,1,createdCnot)
#
    #    areEqual = np.array_equal(gates.toffoli,createdToffoli)
#
    #    print(createdToffoli.astype('float'))
    #    self.assertTrue(areEqual)


if __name__ == "__main__":

    for numQubits in range(2,5):
        identity = np.eye(2**numQubits)
        for q1 in range(0,numQubits):
            for q2 in range(0,numQubits):
                print("qs: ",q1,q2)
                s = gates.genSwapGate(numQubits,q1,q2)
                print(numQubits, s.shape)
                #areEqual = np.array_equal(identity,s@s)
                #print(s, s@s)
                #self.assertTrue(areEqual)