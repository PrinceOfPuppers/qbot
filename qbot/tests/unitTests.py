import unittest

import numpy as np
import os
import qbot.qgates as gates
from qbot.evaluation import globalNameSpace
from qbot.interpreter import executeTxt, executeFile
import qbot.density as density
import qbot.basis as basis
import qbot.measurement as meas
from qbot.probVal import ProbVal

################################################################
# NOTE: all static control gates are only used for unittesting #
#       control gates used in actual application are generated #
################################################################

# static 2 qubit gates
cnot = np.array(
    [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 1],
        [0, 0, 1, 0]
    ]
    ,dtype = complex
)

qft2 = 0.5*np.array(
    [
        [1,  1,  1,  1],
        [1, 1j, -1, -1j],
        [1, -1,  1, -1],
        [1,-1j,- 1,  1j]
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

        createdCnot = gates.genControlledGate(2,0,1,globalNameSpace['pauliXGate'])
        
        areEqual = np.array_equal(cnot,createdCnot)

        self.assertTrue(areEqual)


    def test_swapCnotHadamard(self):
        # test exploits the fact a cnot with the target and control swapped is the same as the cnot 
        # in the hadamard transformed basis        
        createdCnot = gates.genControlledGate(2,0,1,globalNameSpace['pauliXGate'])
        H2 = density.tensorExp(globalNameSpace['hadamardGate'],2)
        
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
        createdCnot = gates.genControlledGate(2,0,1,globalNameSpace['pauliXGate'])

        createdToffoli = gates.genControlledGate(3,0,1,createdCnot)

        areEqual = np.array_equal(toffoli,createdToffoli)

        self.assertTrue(areEqual)
    
    def test_toffoli_genMultiControledGate(self):
        createdToffoli = gates.genMultiControlledGate(3,[0,1],2,globalNameSpace['pauliXGate'])
        areEqual = np.array_equal(toffoli,createdToffoli)

        self.assertTrue(areEqual)

    def test_upsideDownToffoli(self):
        createdCnot = gates.genControlledGate(2,1,0,globalNameSpace['pauliXGate'])

        upsideDownToffoli = gates.genControlledGate(3,2,0,createdCnot)

        swap = gates.genSwapGate(3,0,2)
        
        createdToffoli = swap @ upsideDownToffoli @ swap
        #generate another upsidedown toffoli using genMultiControlledGate
        multiToffoli = gates.genMultiControlledGate(3,[1,2],0,globalNameSpace['pauliXGate'])
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

    def test_replaceArbitrary1(self):
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

    def test_replaceArbitrary2(self):
        bell00 = basis.bell.density[0]
        comp0 = basis.computation.density[0]
        state = density.normalizeDensity(density.replaceArbitrary(bell00,comp0, [0]))

        solution = density.ketsToDensity([
                np.array([1,0,0,0],dtype = complex),
                np.array([0,1,0,0],dtype = complex),
            ],
            [0.5, 0.5]
        )

        self.assertTrue(np.array_equal(state, solution))

    def test_replaceArbitrary3(self):
        bell00 = basis.bell.density[0]
        hadamardPlus = basis.hadamard.density[0]
        comp0 = basis.computation.density[0]
        combined = density.tensorProd(hadamardPlus, bell00)
        state = density.normalizeDensity(density.replaceArbitrary(combined,comp0, [0]))
        solution = density.normalizeDensity(density.tensorProd(comp0, bell00))

        self.assertTrue(np.array_equal(state, solution))


class testMeasurment(unittest.TestCase):
    def test_interweaveDensities(self):
        systemA = basis.computation[0]
        systemB = density.tensorProd(basis.hadamard[0], basis.hadamard[1])
        result = density.interweaveDensities(systemA, systemB, [1])
        expectedState = density.tensorProd(basis.hadamard[0], basis.computation[0], basis.hadamard[1])
        self.assertTrue(np.allclose(result, expectedState))

    def test_computationComputation1(self):
        measurementResult = meas.measureArbitraryMultiState(basis.computation[0], basis.computation,[0])
        self.assertListEqual(measurementResult.probs,[1.0,0])
        self.assertTrue(np.allclose(measurementResult.newState, basis.computation[0]))

    def test_computationComputation2(self):
        state = density.ketsToDensity(basis.computation.kets,[0.5,0.5])
        measurementResult = meas.measureArbitraryMultiState(state, basis.computation)
        self.assertListEqual(measurementResult.probs,[0.5,0.5])
        self.assertTrue(np.allclose(measurementResult.newState, state))

    def test_hadamardComputation(self):
        measurementResult = meas.measureArbitraryMultiState(basis.hadamard[0], basis.computation,[0])
        self.assertListEqual(measurementResult.probs,[0.5,0.5])
        self.assertTrue(np.allclose(measurementResult.newState, density.densityEnsambleToDensity([0.5, 0.5], basis.computation.density)))

    def test_bellBell(self):
        measurementResult = meas.measureArbitraryMultiState(basis.bell[0], basis.bell)
        self.assertListEqual(measurementResult.probs,[1.0,0,0,0])
        self.assertTrue(np.allclose(measurementResult.newState, basis.bell[0]))

    def test_measureArbitrary1(self):
        state = density.ketsToDensity([basis.bell.kets[0]])
        measurementResult = meas.measureArbitraryMultiState(state, basis.hadamard, [0])
        self.assertListEqual(measurementResult.probs,[0.5,0.5])
        self.assertTrue(np.allclose( measurementResult.newState, density.tensorExp(density.densityEnsambleToDensity([0.5, 0.5], basis.hadamard.density), 2) ))
    
    def test_measureArbitrary2(self):
        state = basis.bell[0]
        measurementResult = meas.measureArbitraryMultiState(state, basis.bell, [1,0])
        self.assertListEqual(measurementResult.probs,[1.0,0,0,0])

        self.assertTrue(np.allclose(measurementResult.newState, basis.bell[0]))

    def test_measureArbitrary3(self):
        state = basis.bell[0]
        measurementResult = meas.measureArbitraryMultiState(state, basis.hadamard, [1])
        self.assertListEqual(measurementResult.probs,[0.5, 0.5])
        self.assertTrue(np.allclose( measurementResult.newState, density.tensorExp(density.densityEnsambleToDensity([0.5, 0.5], basis.hadamard.density), 2) ))
    
    def test_measureArbitrary4(self):
        state = density.ketsToDensity([
                np.array([0,1,0,0,0,0,0,0],dtype = complex),
            ]
        )
        measurementResult = meas.measureArbitraryMultiState(state, basis.computation, [1, 2])
        self.assertListEqual(measurementResult.probs,[0, 1, 0, 0])

        self.assertTrue(np.allclose( measurementResult.newState, meas.tensorPermute(3, 1, basis.computation) ))

    def test_measureArbitrary5(self):
        state = density.ketsToDensity([
                np.array([0,0,1,0,0,0,0,0],dtype = complex),
            ]
        )
        measurementResult = meas.measureArbitraryMultiState(state, basis.computation, [0, 2])
        self.assertListEqual(measurementResult.probs,[1, 0, 0, 0])
        self.assertTrue(np.allclose( measurementResult.newState, meas.tensorPermute(3, 2, basis.computation) ))

    def test_measureArbitrary6(self):
        state = basis.bell[0]
        measurementResult = meas.measureArbitraryMultiState(state, basis.computation, [0])

        mixedComp = density.densityEnsambleToDensity([0.5, 0.5], basis.hadamard.density)
        expectedState = density.tensorProd(mixedComp, density.densityEnsambleToDensity([0.5, 0.5], basis.hadamard.density))

        self.assertTrue(measurementResult.probs == [0.5, 0.5])
        self.assertTrue(np.allclose(measurementResult.newState, expectedState))


class testOperations(unittest.TestCase):
    def test_gate(self):
        localNameSpace = executeTxt(
            '''
            qset computation.density[0]
            gate hadamardGate ; 0
            '''
        )
        self.assertTrue(np.array_equal(localNameSpace['state'], globalNameSpace['hadamard'].density[0]))

    def test_controlledGate1(self):
        localNameSpace = executeTxt(
            '''
            qset tensorExp(computation.density[0], 2)
            gate hadamardGate ; 0 ; [1]
            '''
        )
        expectedState = density.tensorExp(globalNameSpace['computation'].density[0], 2)
        self.assertTrue(np.array_equal(localNameSpace['state'], expectedState))

    def test_controlledGate2(self):
        localNameSpace = executeTxt(
            '''
            qset tensorPermute(2, 1, computation)
            gate hadamardGate ; 0 ; [1]
            '''
        )
        expectedState = density.tensorProd(globalNameSpace['hadamard'].density[0], globalNameSpace['computation'].density[1])
        self.assertTrue(np.array_equal(localNameSpace['state'], expectedState))

    def test_controlledGate3(self):
        localNameSpace = executeTxt(
            '''
            qset tensorPermute(2, 1, computation)
            gate hadamardGate ; 0 ; 1
            '''
        )
        expectedState = density.tensorProd(globalNameSpace['hadamard'].density[0], globalNameSpace['computation'].density[1])
        self.assertTrue(np.array_equal(localNameSpace['state'], expectedState))

    def test_largerGate(self):
        localNameSpace = executeTxt(
            '''
            qset tensorProd(hada[0], hada[0])
            gate tensorProd(identityGate, hadamardGate) ; 0
            '''
        )

        expectedState = density.tensorProd(globalNameSpace['hada'][0], globalNameSpace['comp'][0])
        self.assertTrue(np.allclose(localNameSpace['state'], expectedState))

    def test_gateProbVals1(self):
        localNameSpace = executeTxt(
            '''
            qset tensorProd(comp[0], comp[0])
            gate ProbValZipped( [(0.5, tensorProd(identityGate, hadamardGate)), (0.5, tensorProd(hadamardGate, identityGate))] ) ; 0
            '''
        )
        comp0 = globalNameSpace['computation'][0]
        hadaPlus = globalNameSpace['hadamard'][0]
        expectedState = density.densityEnsambleToDensity([0.5, 0.5], [
            density.tensorProd(hadaPlus, comp0),
            density.tensorProd(comp0, hadaPlus)
        ])

        self.assertTrue(np.allclose(localNameSpace['state'], expectedState))

    def test_gateProbVals2(self):
        localNameSpace = executeTxt(
            '''
            qset tensorPermute(3, 1, comp)
            gate hadamardGate ; ProbValZipped([(0.5, 0), (0.5, 1)]) ; [2]
            '''
        )
        comp0 = globalNameSpace['computation'][0]
        comp1 = globalNameSpace['computation'][1]
        hadaPlus = globalNameSpace['hadamard'][0]
        expectedState = density.densityEnsambleToDensity([0.5, 0.5], [
            density.tensorProd(hadaPlus, comp0, comp1),
            density.tensorProd(comp0, hadaPlus, comp1)
        ])

        self.assertTrue(np.allclose(localNameSpace['state'], expectedState))

    def test_gateProbVals3(self):
        localNameSpace = executeTxt(
            '''
            qset tensorPermute(3, 1, comp)
            gate hadamardGate ; 0 ; ProbVal([0.5, 0.5], [1, 2])
            '''
        )
        comp0 = globalNameSpace['computation'][0]
        comp1 = globalNameSpace['computation'][1]
        hadaPlus = globalNameSpace['hadamard'][0]
        expectedState = density.densityEnsambleToDensity([0.5, 0.5], [
            density.tensorProd(hadaPlus, comp0, comp1),
            density.tensorProd(comp0, comp0, comp1)
        ])

        self.assertTrue(np.allclose(localNameSpace['state'], expectedState))

    def test_discVal(self):
        localNameSpace = executeTxt(
            '''

            qset tensorExp(comp[0], 2)
            gate hadamardGate ; 0
            disc [1]
            '''
        )
        self.assertTrue(np.array_equal(localNameSpace['state'], globalNameSpace['hadamard'].density[0]))

    def test_discProbVal(self):
        localNameSpace = executeTxt(
            '''
            qset tensorExp(comp[0], 2)
            gate hadamardGate ; 0
            disc ProbValZipped([(0.5, [1]), (0.5, [0])])
            '''
        )
        expectedState = density.densityEnsambleToDensity([0.5, 0.5], [globalNameSpace['hadamard'].density[0], globalNameSpace['computation'].density[0]])
        self.assertTrue(np.allclose(localNameSpace['state'], expectedState))

    def test_qset1(self):
        localNameSpace = executeTxt(
            '''
            qset tensorExp(comp[0], 3)
            qset hada[0] ; [1]
            '''
        )
        expectedState = density.tensorProd(basis.computation[0], basis.hadamard[0], basis.computation[0])
        self.assertTrue(np.allclose(localNameSpace['state'], expectedState))

    def test_qset2(self):
        localNameSpace = executeTxt(
            '''
            qset tensorExp(comp[0], 3)
            qset hada[0] ; ProbVal([0.5, 0.5], [[1], [2]])
            '''
        )
        s1 = density.tensorProd(basis.computation[0], basis.hadamard[0], basis.computation[0])
        s2 = density.tensorProd(basis.computation[0], basis.computation[0], basis.hadamard[0])
        expectedState = density.densityEnsambleToDensity([0.5, 0.5], [s1, s2])
        self.assertTrue(np.allclose(localNameSpace['state'], expectedState))

    def test_qset3(self):
        localNameSpace = executeTxt(
            '''
            qset tensorExp(comp[0], 3)
            qset hada[0] ; 1
            '''
        )
        expectedState = density.tensorProd(basis.computation[0], basis.hadamard[0], basis.computation[0])
        self.assertTrue(np.allclose(localNameSpace['state'], expectedState))

    def test_qset4(self):
        localNameSpace = executeTxt(
            '''
            qset tensorExp(comp[0], 3)
            qset hada[0] ; ProbVal([0.5, 0.5], [1, 2])
            '''
        )
        s1 = density.tensorProd(basis.computation[0], basis.hadamard[0], basis.computation[0])
        s2 = density.tensorProd(basis.computation[0], basis.computation[0], basis.hadamard[0])
        expectedState = density.densityEnsambleToDensity([0.5, 0.5], [s1, s2])
        self.assertTrue(np.allclose(localNameSpace['state'], expectedState))

    def test_cdef(self):
        localNameSpace = executeTxt(
            '''
            cdef abc ; 5
            cdef x_1234 ; ProbVal([0.5, 0.5], [comp[0], hada[0]])
            qset x_1234
            '''
        )
        expectedState = density.densityEnsambleToDensity([0.5, 0.5], [basis.computation[0], basis.hadamard[0]])
        self.assertTrue(np.allclose(localNameSpace['x_1234'].toDensityMatrix(), expectedState))
        self.assertTrue(np.allclose(localNameSpace['state'], expectedState))
        self.assertTrue(localNameSpace['abc'] == 5)

    def test_qdef(self):
        localNameSpace = executeTxt(
            '''
            qdef x_1234 ; ProbVal([0.5, 0.5], [comp[0], hada[0]])
            qset x_1234
            '''
        )
        expectedState = density.densityEnsambleToDensity([0.5, 0.5], [basis.computation[0], basis.hadamard[0]])
        self.assertTrue(np.allclose(localNameSpace['x_1234'], expectedState))
        self.assertTrue(np.allclose(localNameSpace['state'], expectedState))


    def test_meas1(self):
        localNameSpace = executeTxt(
            '''
            qset tensorExp(comp[0], 3)
            meas x; comp ; 1
            '''
        )
        expectedState = density.tensorExp(basis.computation[0], 3)
        self.assertTrue(localNameSpace['x'].probs == [1, 0])
        self.assertTrue(np.allclose(localNameSpace['state'], expectedState))

    def test_meas2(self):
        localNameSpace = executeTxt(
            '''
            qset tensorProd(hada[0], comp[0], hada[0])
            meas x; comp ; 2
            '''
        )
        expectedState = density.tensorProd(basis.hadamard[0], basis.computation[0], density.densityEnsambleToDensity([0.5, 0.5], basis.computation.density))
        self.assertTrue(localNameSpace['x'].probs == [0.5, 0.5])
        self.assertTrue(np.allclose(localNameSpace['state'], expectedState))

    def test_meas3(self):
        localNameSpace = executeTxt(
            '''
            qset tensorProd(bell[0], comp[0], hada[0])
            meas x; comp ; (0, 3)
            '''
        )
        mixedComp = density.densityEnsambleToDensity([0.5, 0.5], basis.computation.density)
        expectedState = density.tensorProd(mixedComp, density.densityEnsambleToDensity([0.5, 0.5], basis.hadamard.density), basis.computation[0], mixedComp)
        self.assertTrue(localNameSpace['x'].probs == [0.25, 0.25, 0.25, 0.25])
        self.assertTrue(np.allclose(localNameSpace['state'], expectedState))

    def test_meas4(self):
        localNameSpace = executeTxt(
            '''
            qset tensorProd(bell[0], comp[0], hada[0])
            meas x; comp ; {0, 3}
            '''
        )
        mixedComp = density.densityEnsambleToDensity([0.5, 0.5], basis.computation.density)
        expectedState = density.tensorProd(mixedComp, density.densityEnsambleToDensity([0.5, 0.5], basis.hadamard.density), basis.computation[0], mixedComp)
        self.assertTrue(localNameSpace['x'].probs == [0.25, 0.25, 0.25, 0.25])
        self.assertTrue(np.allclose(localNameSpace['state'], expectedState))

    def test_peek(self):
        localNameSpace = executeTxt(
            '''
            qset tensorProd(bell[0], comp[0], hada[0])
            peek x; comp ; {0, 3}
            '''
        )
        expectedState = density.tensorProd(basis.bell[0], basis.computation[0], basis.hadamard[0])
        self.assertTrue(localNameSpace['x'].probs == [0.25, 0.25, 0.25, 0.25])
        self.assertTrue(np.allclose(localNameSpace['state'], expectedState))

    def test_halt1(self):
        localNameSpace = executeTxt(
            '''
            cdef x ; 1234
            halt
            cdef x ; "hello"
            '''
        )
        self.assertEqual(localNameSpace['x'], 1234)

    def test_halt2(self):
        localNameSpace = executeTxt(
            '''
            cdef x ; 1234
            halt 1 == 1
            cdef x ; "hello"
            '''
        )
        self.assertEqual(localNameSpace['x'], 1234)

    def test_halt3(self):
        localNameSpace = executeTxt(
            '''
            cdef x ; 1234
            halt False
            cdef x ; "hello"
            '''
        )
        self.assertEqual(localNameSpace['x'], "hello")

    # MARK: removed probval control flow
    # def test_halt4(self):
    #     localNameSpace = executeTxt(
    #         '''
    #         cdef x ; 1234
    #         halt ProbVal([0.25, 0.75], [True, False])
    #         cdef x ; "hello"
    #         '''
    #     )
    #     val = localNameSpace['x']
    #     correctVal = ProbVal([0.25, 0.75], [1234, "hello"])
    #     self.assertTrue(isinstance(val, ProbVal))
    #     self.assertTrue(val.isEquivalent(correctVal))

    # def test_halt5(self):
    #     localNameSpace = executeTxt(
    #         '''
    #         cdef x ; ProbVal([0.25, 0.75], [True, False])
    #         halt x
    #         halt not x
    #         cdef x ; "shouldNeverReach"
    #         '''
    #     )
    #     val = localNameSpace['x']
    #     self.assertTrue(isinstance(val, ProbVal))
    #     for value in val.values:
    #         if value == "shouldNeverReach":
    #             self.fail()

    def test_jump1(self):
        localNameSpace = executeTxt(
            '''
            cdef x ; 1234
            jump end
            cdef x ; "hello"
            mark end
            '''
        )
        self.assertEqual(localNameSpace['x'], 1234)

    def test_jump2(self):
        localNameSpace = executeTxt(
            '''
            cdef x ; 0
            mark beforeHalt
            halt x == 2
            cdef x ; x + 1
            jump beforeHalt
            '''
        )
        self.assertEqual(localNameSpace['x'], 2)

    def test_cjmp1(self):
        localNameSpace = executeTxt(
            '''
            cdef x ; 1234
            cjmp end ; True
            cdef x ; "hello"
            mark end
            '''
        )
        self.assertEqual(localNameSpace['x'], 1234)

    def test_cjmp2(self):
        localNameSpace = executeTxt(
            '''
            cdef x ; 1234
            cjmp end ; False
            cdef x ; "hello"
            mark end
            '''
        )
        self.assertEqual(localNameSpace['x'], "hello")

    def test_cjmp3(self):
        localNameSpace = executeTxt(
            '''
            cdef x ; 0
            mark inc
            cdef x ; x + 1
            cjmp inc ; x < 2
            '''
        )
        self.assertEqual(localNameSpace['x'], 2)

    # MARK: removed probval control flow
    # def test_cjmp4(self):
    #     localNameSpace = executeTxt(
    #         '''
    #         cdef x ; ProbVal([0.5, 0.5], [0, 1])
    #         mark inc
    #         cdef x ; x + 1
    #         cjmp inc ; x < 2 ; end
    #         mark end
    #         '''
    #     )
    #     self.assertEqual(localNameSpace['x'], 2)

    # def test_cjmp5(self):
    #     localNameSpace = executeTxt(
    #         '''
    #         cdef x ; ProbVal([0.5, 0.5], [0, 1])
    #         mark inc
    #         cdef x ; x + 1
    #         cjmp inc ; x < 2 or x == 1; end
    #         mark end
    #         '''
    #     )
    #     print(localNameSpace['x'])
    #     self.assertTrue( localNameSpace['x'].isEquivalent(ProbVal([0.5, 0.5], [1, 2])) )

    def test_retr1(self):
        localNameSpace = executeTxt(
            '''
            cdef x ; 0

            mark loop
            jump incX 
            cjmp loop ; x < 3
            halt

            mark incX
            cdef x ; x + 1
            retr
            '''
        )
        self.assertEqual(localNameSpace['x'], 3)

    def test_retr2(self):
        localNameSpace = executeTxt(
            '''
            cdef x ; 0

            mark loop
            cjmp incX ; x < 3
            halt

            mark incX
            cdef x ; x + 1
            retr
            '''
        )
        self.assertEqual(localNameSpace['x'], 1)

    def test_retr3(self):
        localNameSpace = executeTxt(
            '''
            cdef x ; 0

            mark loop
            jump incX
            jump loop

            mark incX
            cdef x ; x + 1
            retr x < 3
            '''
        )
        self.assertEqual(localNameSpace['x'], 3)


    def test_swap1(self):
        localNameSpace = executeTxt(
            '''
            qset tensorProd(hada[0], comp[0])
            swap 0 ; 1
            '''
        )
        self.assertTrue(np.allclose(localNameSpace['state'], density.tensorProd(basis.computation[0], basis.hadamard[0])))

    def test_swap2(self):
        localNameSpace = executeTxt(
            '''
            qset tensorProd(hada[0], comp[0], comp[1])
            swap 0 ; ProbVal([0.5, 0.5], [1, 2])
            '''
        )
        expectedState = density.densityEnsambleToDensity(
                [0.5, 0.5],
                [
                    density.tensorProd(basis.computation[0], basis.hadamard[0], basis.computation[1]),
                    density.tensorProd(basis.computation[1], basis.computation[0], basis.hadamard[0]),
                ])
        self.assertTrue(np.allclose(localNameSpace['state'], expectedState))

   # def test_perm1(self):
   #     localNameSpace = executeTxt(
   #         '''
   #         qset tensorProd(hada[0], comp[0])
   #         perm lambda i: (i+1)%2
   #         '''
   #     )
   #     print('\n', localNameSpace['state'])
   #     print(density.tensorProd(basis.hadamard[0], basis.computation[0]))
   #     expectedState = density.tensorProd(basis.hadamard[0], basis.computation[0])
   #     self.assertTrue(np.allclose(localNameSpace['state'], expectedState))

   # def test_perm2(self):
   #     localNameSpace = executeTxt(
   #         '''
   #         qset tensorProd(hada[0], comp[0], comp[1])
   #         perm lambda i: (i+1)%3
   #         '''
   #     )
   #     expectedState = density.tensorProd(basis.computation[1], basis.hadamard[0], basis.computation[0])
   #     self.assertTrue(np.allclose(localNameSpace['state'], expectedState))

class testSpecialGates(unittest.TestCase):
    def test_qft1(self):
        self.assertTrue(np.allclose(globalNameSpace['hadamardGate'], gates.genQFT(1)))

    def test_qft2(self):
        self.assertTrue(np.allclose(qft2, gates.genQFT(2)))

    def test_rotx(self):
        self.assertTrue(np.allclose(-1j*globalNameSpace['pauliXGate'], gates.genXRotGate(np.pi)))

    def test_roty(self):
        self.assertTrue(np.allclose(-1j*globalNameSpace['pauliYGate'], gates.genYRotGate(np.pi)))

    def test_rotz(self):
        self.assertTrue(np.allclose(-1j*globalNameSpace['pauliZGate'], gates.genZRotGate(np.pi)))

    def test_simonsGate1(self):
        localNameSpace = executeTxt(
            '''
            qset tensorProd(comp[0], comp[0])
            qdef x ; simonsGate(2, lambda x: 1)
            gate x
            '''
        )
        self.assertTrue(np.allclose(localNameSpace['state'], density.tensorProd(basis.computation[0], basis.computation[1])))

    def test_simonsGate2(self):
        localNameSpace = executeTxt(
            '''
            qset tensorProd(hada[0], comp[0], comp[0])
            qdef x ; simonsGate(3, lambda x: x & 0b01)
            gate x
            '''
        )
        self.assertTrue(np.allclose(localNameSpace['state'], density.tensorProd(basis.hadamard[0], basis.computation[0], basis.computation[0])))

    def test_simonsGate3(self):
        localNameSpace = executeTxt(
            '''
            qset tensorProd(hada[1], comp[0], comp[0])
            qdef x ; simonsGate(3, lambda x: x & 0b01)
            gate x
            '''
        )
        self.assertTrue(np.allclose(localNameSpace['state'], density.tensorProd(basis.hadamard[1], basis.computation[0], basis.computation[0])))

    def test_simonsGate4(self):
        localNameSpace = executeTxt(
            '''
            qset tensorProd(hada[1], comp[1], comp[0])
            qdef x ; simonsGate(3, lambda x: x & 0b01)
            gate x
            '''
        )
        self.assertTrue(np.allclose(localNameSpace['state'], density.tensorProd(basis.hadamard[1], basis.computation[1], basis.computation[1])))

    def test_simonsGate5(self):
        localNameSpace = executeTxt(
            '''
            qset tensorProd(comp[1], comp[0], comp[0])
            qdef x ; simonsGate(3, lambda x: (x & 0b10) !=0 )
            gate x
            '''
        )
        expectedState = density.tensorProd(basis.computation[1], basis.computation[0], basis.computation[1])
        self.assertTrue(np.allclose(localNameSpace['state'], expectedState))

    def test_simonsGate6(self):
        localNameSpace = executeTxt(
            '''
            qset tensorProd(comp[0], comp[0], comp[0])
            qdef x ; simonsGate(3, lambda x: (x & 0b10) !=0 )
            gate x
            '''
        )
        expectedState = density.tensorProd(basis.computation[0], basis.computation[0], basis.computation[0])
        self.assertTrue(np.allclose(localNameSpace['state'], expectedState))

    def test_simonsGate7(self):
        localNameSpace = executeTxt(
            '''
            qset tensorProd(hada[0], comp[0], comp[0])
            qdef x ; simonsGate(3, lambda x: (x & 0b10) != 0 )
            gate x
            '''
        )
        comp0 = basis.computation.kets[0]
        comp1 = basis.computation.kets[1]
        a=meas.tensorProd(comp0, comp0, comp0)
        b=meas.tensorProd(comp1, comp0, comp1)
        state = 2**(-1/2) * (a + b)
        expectedState = density.ketToDensity(state)

        self.assertTrue(np.allclose(localNameSpace['state'], expectedState))


class testAlgorithms(unittest.TestCase):

    def test_superDenseCoding1(self):
        localNameSpace = executeTxt(
            '''
            cdef results ; []
            cdef index ; 0

            mark loop
            qset bell[0]
            gate tensorExp(pauliXGate, (index & 0b01) != 0)
            gate tensorExp(pauliZGate, (index & 0b10) != 0)
            meas result ; bell
            pydo results.append(result.probs)
            cdef index ; index + 1
            cjmp loop ; index < 4
            '''
        )
        results = localNameSpace['results']
        for i,result in enumerate(results):
            for j,prob in enumerate(result):
                if i == j:
                    self.assertEqual(prob, 1.0)
                else:
                    self.assertEqual(prob, 0.0)

    def test_superDenseCoding2(self):
        localNameSpace = executeTxt(
            '''
            cdef results ; []
            cdef index ; 0

            mark loop
            qset bell[0]
            gate pauliXGate ; 0 ; [] ; (index & 0b01) != 0
            gate pauliZGate ; 0 ; [] ; (index & 0b10) != 0
            meas result ; bell
            pydo results.append(result.probs)
            cdef index ; index + 1
            cjmp loop ; index < 4
            '''
        )
        results = localNameSpace['results']
        for i,result in enumerate(results):
            for j,prob in enumerate(result):
                if i == j:
                    self.assertEqual(prob, 1.0)
                else:
                    self.assertEqual(prob, 0.0)


    def test_phaseKickback(self):
        localNameSpace = executeTxt(
            '''
            cdef results ; []

            note eiganValue is 1
            qset tensorProd(comp[0], hada[0])
            jump checkPhase

            note eiganValue is -1
            qset tensorProd(comp[0], hada[1])
            jump checkPhase
            halt

            mark checkPhase
            gate hadamardGate ; 0
            gate pauliXGate   ; 1 ; 0
            gate hadamardGate ; 0
            meas tmp ; comp ; 0
            pydo results.append(tmp)
            retr
            '''
        )
        self.assertTrue(localNameSpace['results'][0].probs == [1.0, 0.0])
        self.assertTrue(localNameSpace['results'][1].probs == [0.0, 1.0])

    def test_deutschAlgorithm(self):
        localNameSpace = executeTxt(
            '''
            cdef results ; []

            note constant f (should return |0>)
            cdef f ; lambda x: 1
            jump check

            note balanced f (should return |1>)
            cdef f ; lambda x: x
            jump check

            halt

            mark check
            qset tensorProd(comp[0], hada[1])
            gate hadamardGate ; 0
            gate simonsGate(2, f)
            gate hadamardGate ; 0
            meas tmp ; comp ; 0
            pydo results.append("constant" if np_isclose(tmp.probs[0], 1.0) else "balanced")
            retr
            '''
        )
        self.assertEqual(localNameSpace['results'][0], "constant")
        self.assertEqual(localNameSpace['results'][1], "balanced")


class testFileParsing(unittest.TestCase):
    def test_deutschAlgorithmFromFile(self):
        filePath = os.path.join(os.path.dirname(__file__), 'test.qb')
        with open(filePath, 'r') as f:
            localNameSpace = executeFile(f)
        self.assertEqual(localNameSpace['results'][0], "constant")
        self.assertEqual(localNameSpace['results'][1], "balanced")


if __name__ == "__main__":
    unittest.main()

