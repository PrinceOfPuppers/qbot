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
        createdCnot = gates.genControlledGate(2,0,1,gates.pauliX)
        
        areEqual = np.array_equal(gates.cnot,createdCnot)

        self.assertTrue(areEqual)


    def test_swapCnotHadamard(self):
        # test exploits the fact a cnot with the target and control swapped is the same as the cnot 
        # in the hadamard transformed basis        
        createdCnot = gates.genControlledGate(2,0,1,gates.pauliX)
        H2 = np.kron(gates.Hadamard,gates.Hadamard)
        
        createdCnotHadamardBasis = H2 @ createdCnot @ H2
        
        # we compare the above with simply a swapped cnot
        s = gates.genSwapGate(2,0,1)
        swappedCnot = s @ gates.cnot @ s

        areEqual = np.allclose(createdCnotHadamardBasis,swappedCnot)
        self.assertTrue(areEqual)
    
    def test_shiftUpGate1(self):
        
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
    
    def test_shiftUpGate2(self):
        numQubits = 4
        hilbertDim = 2 ** numQubits
        swaps = np.eye(hilbertDim ,dtype=complex)
        for i in range(0,numQubits):
            swaps = swaps @ gates.genSwapGate(numQubits, i, numQubits - 1)
        
        shiftUp = gates.genShiftGate(numQubits,True)
        
        self.assertTrue(np.array_equal(swaps,shiftUp))

    
    def test_shiftDownGate1(self):
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

    def test_shiftDownGate2(self):
        numQubits = 4
        hilbertDim = 2 ** numQubits
        swaps = np.eye(hilbertDim ,dtype=complex)
        for i in reversed(range(0,numQubits)):
            swaps = swaps @ gates.genSwapGate(numQubits, 0, i)
        
        shiftDown = gates.genShiftGate(numQubits,False)
        
        self.assertTrue(np.array_equal(swaps,shiftDown))

    def test_toffoli(self):
        createdCnot = gates.genControlledGate(2,0,1,gates.pauliX)

        createdToffoli = gates.genControlledGate(3,0,1,createdCnot)

        areEqual = np.array_equal(gates.toffoli,createdToffoli)

        self.assertTrue(areEqual)
    
    def test_toffoli_genMultiControledGate(self):
        createdToffoli = gates.genMultiControlledGate(3,[0,1],2,gates.pauliX)
        areEqual = np.array_equal(gates.toffoli,createdToffoli)

        self.assertTrue(areEqual)

    def test_upsideDownToffoli(self):
        createdCnot = gates.genControlledGate(2,1,0,gates.pauliX)

        upsideDownToffoli = gates.genControlledGate(3,2,0,createdCnot)

        swap = gates.genSwapGate(3,0,2)
        
        createdToffoli = swap @ upsideDownToffoli @ swap
        #generate another upsidedown toffoli using genMultiControlledGate
        multiToffoli = gates.genMultiControlledGate(3,[1,2],0,gates.pauliX)
        multiToffoli = swap @ multiToffoli @ swap

        areEqual = np.array_equal(gates.toffoli,createdToffoli) and np.array_equal(gates.toffoli,multiToffoli)
        self.assertTrue(areEqual)



if __name__ == "__main__":
    unittest.main()