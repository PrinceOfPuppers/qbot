import unittest

import numpy as np
import qbot.qgates as gates
from qbot.evaluation import globalNameSpace
import qbot.density as density
import qbot.basis as basis

################################################################
# NOTE: all static control gates are only used for unittesting #
#       control gates used in actual application are generated #
################################################################

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

        createdCnot = gates.genControlledGate(2,0,1,globalNameSpace['pauliX'])
        
        areEqual = np.array_equal(cnot,createdCnot)

        self.assertTrue(areEqual)


    def test_swapCnotHadamard(self):
        # test exploits the fact a cnot with the target and control swapped is the same as the cnot 
        # in the hadamard transformed basis        
        createdCnot = gates.genControlledGate(2,0,1,globalNameSpace['pauliX'])
        H2 = np.kron(globalNameSpace['hadamard'],globalNameSpace['hadamard'])
        
        createdCnotHadamardBasis = H2 @ createdCnot @ H2
        
        # we compare the above with simply a swapped cnot
        s = gates.genSwapGate(2,0,1)
        swappedCnot = s @ cnot @ s

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
        createdCnot = gates.genControlledGate(2,0,1,globalNameSpace['pauliX'])

        createdToffoli = gates.genControlledGate(3,0,1,createdCnot)

        areEqual = np.array_equal(toffoli,createdToffoli)

        self.assertTrue(areEqual)
    
    def test_toffoli_genMultiControledGate(self):
        createdToffoli = gates.genMultiControlledGate(3,[0,1],2,globalNameSpace['pauliX'])
        areEqual = np.array_equal(toffoli,createdToffoli)

        self.assertTrue(areEqual)

    def test_upsideDownToffoli(self):
        createdCnot = gates.genControlledGate(2,1,0,globalNameSpace['pauliX'])

        upsideDownToffoli = gates.genControlledGate(3,2,0,createdCnot)

        swap = gates.genSwapGate(3,0,2)
        
        createdToffoli = swap @ upsideDownToffoli @ swap
        #generate another upsidedown toffoli using genMultiControlledGate
        multiToffoli = gates.genMultiControlledGate(3,[1,2],0,globalNameSpace['pauliX'])
        multiToffoli = swap @ multiToffoli @ swap

        areEqual = np.array_equal(toffoli,createdToffoli) and np.array_equal(toffoli,multiToffoli)
        self.assertTrue(areEqual)
    

class testPartialTrace(unittest.TestCase):
    def test_compareMethods1(self):
        state = density.ketsToDensity([
                np.array([0,1,0,0,0,0,0,0],dtype = complex),
                np.array([0,0,0,0,0,1,0,0],dtype = complex),
                np.array([0,0,1/(2**(1/2)),0,0,1/(2**(1/2)),0,0],dtype = complex),
            ],
            [0.5,0.25,0.25]
        )
        a1,b1 = density.partialTraceBoth(state, 2, 1)
        a2,b2 = density.partialTraceArbitrary(state, 3, [0,1])

        self.assertTrue(np.array_equal(a1, a2))
        self.assertTrue(np.array_equal(b1, b2))

    def test_compareMethods2(self):
        state = density.ketsToDensity([
                np.array([0,1,0,0,0,0,0,0],dtype = complex),
                np.array([0,0,0,0,0,0,0,1],dtype = complex),
                np.array([0,0,1,0,0,0,0,0],dtype = complex),
            ],
            [0.5, 0.15, 0.35]
        )
        a1,b1 = density.partialTraceBoth(state,1,2)
        a2,b2 = density.partialTraceArbitrary(state, 3, [0])
        self.assertTrue(np.array_equal(a1, a2))
        self.assertTrue(np.array_equal(b1, b2))

    def test_compareMethods3(self):
        state = density.ketsToDensity([
                np.array([0,1,0,0,0,0,0,0],dtype = complex),
                np.array([0,0,0,0,0,0,0,1],dtype = complex),
                np.array([0,0,1,0,0,0,0,0],dtype = complex),
            ],
            [0.5, 0.15, 0.35]
        )
        b1,a1 = density.partialTraceBoth(state,1,2)
        a2,b2 = density.partialTraceArbitrary(state, 3, [1,2])
        self.assertTrue(np.array_equal(a1, a2))
        self.assertTrue(np.array_equal(b1, b2))

    def test_replaceArbitrary(self):
        bell00 = basis.bell.density[0]
        comp0 = basis.computation.density[0]
        state = density.normalizeDensity(density.replaceArbitrary(bell00,comp0, [1]))

        solution = density.ketsToDensity([
                np.array([1,0,0,0],dtype = complex),
                np.array([0,0,1,0],dtype = complex),
            ],
            [0.5, 0.5]
        )

        self.assertTrue(np.array_equal(state, solution))


#class testMeasurement(unittest.TestCase):
#    def test_computationComputation1(self):
#        state = density.ketsToDensity([basis.computation.kets[0]])
#        measurementResult = density.measureTopNQubits(state,basis.computation.density,1)
#        self.assertListEqual(measurementResult.probs,[1.0,0])
#
#    def test_computationComputation2(self):
#        state = density.ketsToDensity(basis.computation.kets,[0.5,0.5])
#        measurementResult = density.measureTopNQubits(state,basis.computation.density,1)
#        self.assertListEqual(measurementResult.probs,[0.5,0.5])
#
#    def test_hadamardComputation(self):
#        state = density.ketsToDensity([basis.hadamard.kets[0]])
#        measurementResult = density.measureTopNQubits(state,basis.computation.density,1)
#        self.assertListEqual(measurementResult.probs,[0.5,0.5])
#
#    def test_bellBell(self):
#        state = density.ketsToDensity([basis.bell.kets[0]])
#        measurementResult = density.measureTopNQubits(state,basis.bell.density,2)
#        self.assertListEqual(measurementResult.probs,[1.0,0,0,0])
#
#    def test_measureArbitrary1(self):
#        state = density.ketsToDensity([basis.bell.kets[0]])
#        measurementResult = density.measureArbitrary(state, basis.hadamard.density, [0])
#        self.assertListEqual(measurementResult.probs,[0.5,0.5])
#    
#    def test_measureArbitrary2(self):
#        state = density.ketsToDensity([basis.bell.kets[0]])
#        measurementResult = density.measureArbitrary(state, basis.bell.density, [1,0])
#        self.assertListEqual(measurementResult.probs,[1.0,0,0,0])
#
#    def test_measureArbitrary3(self):
#        state = density.ketsToDensity([basis.bell.kets[0]])
#        measurementResult = density.measureArbitrary(state, basis.hadamard.density, [1])
#        self.assertListEqual(measurementResult.probs,[0.5, 0.5])
#    
#    def test_measureArbitrary4(self):
#        state = density.ketsToDensity([
#                np.array([0,1,0,0,0,0,0,0],dtype = complex),
#            ]
#        )
#        measurementResult = density.measureArbitrary(state, basis.computation2D.density, [1, 2])
#        self.assertListEqual(measurementResult.probs,[0, 1, 0, 0])
#
#    def test_measureArbitrary5(self):
#        state = density.ketsToDensity([
#                np.array([0,0,1,0,0,0,0,0],dtype = complex),
#            ]
#        )
#        measurementResult = density.measureArbitrary(state, basis.computation2D.density, [0, 2])
#        self.assertListEqual(measurementResult.probs,[1, 0, 0, 0])

    # def test_removeFirstNQubits1(self):
    #     rmGate = gates.genRemoveFirstNQubitsGate(3,2)
    #     ket = np.array([1,0,0,0,0,0,0,0], dtype = complex)
    #     correctResult = np.array([1,0],dtype = complex)

    #     areEqual = np.array_equal(correctResult, rmGate.dot(ket))
    #     self.assertTrue(areEqual)

    # def test_removeFirstNQubits2(self):
    #     rmGate = gates.genRemoveFirstNQubitsGate(3,2)
    #     ket = np.array([0,0,0,0,0,0,0,1], dtype = complex)
    #     correctResult = np.array([0,1],dtype = complex)
    #     generatedResult = rmGate.dot(ket)
    #     areEqual = np.array_equal(correctResult, generatedResult)
    #     self.assertTrue(areEqual)
    
    # def test_removeFirstNQubitsDensity1(self):
    #     rmGate = gates.genRemoveFirstNQubitsGate(2,1)
    #     bellDensity = basis.bell.density[0]
    #     state = rmGate @ bellDensity @ rmGate.T
    #     print(bellDensity.shape,rmGate.shape)
    #     print("\n",density.densityToStateEnsable(state))
    #     # generatedResult = rmGate.dot(ket)
    #     # areEqual = np.array_equal(correctResult, generatedResult)
    #     # self.assertTrue(areEqual)


if __name__ == "__main__":
    unittest.main()
