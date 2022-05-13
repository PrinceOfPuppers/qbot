import numpy as np

import qbot.basis as basis
from qbot.probVal import ProbVal, funcWrapper
from qbot.evaluation import evaluateWrapper
from qbot.measurement import measureArbitraryMultiState, MeasurementResult, MeasurementIndexError
import qbot.density as density
import qbot.qgates as gates
import qbot.errors as err

from typing import Union, Callable


def hilbertSpaceNumQubits(state):
    if len(state.shape) == 0 or state.size == 0:
        return 0
    return int(np.log2(state.shape[0]))

def hilbertSpaceDim(state):
    if len(state.shape) == 0 or state.size == 0:
        return 0
    return int(state.shape[0])


def getVarName(lines, lineNum, token):
    if not token.isidentifier():
        err.raiseFormattedError(err.customInvalidVariableName(lines, lineNum, token))
    return token


def getMarkLineNum(localNameSpace, lines, lineNum, token) -> int:
    if token.isidentifier() and token in localNameSpace['__marks'].keys():
        return localNameSpace['__marks'][token]

    res = evaluateWrapper(lines, lineNum, token, localNameSpace)
    if isinstance(res, str):
        try:
            return localNameSpace['__marks'][res]
        except KeyError:
            err.raiseFormattedError(err.customUnknownMarkName(lines, lineNum, token))

    if isinstance(res, ProbVal):
        typeStr = res.typeString()
    else:
        typeStr = type(res).__name__

    err.raiseFormattedError(err.customTypeError(lines, lineNum, ['str'], typeStr))


def assertProbValType(lines, lineNum, pv, t):
    if isinstance(pv, t):
        return
    if isinstance(pv, ProbVal):
        if not isinstance(pv.instance(), t):
            err.raiseFormattedError(err.customTypeError(lines, lineNum, [t.__name__, f"ProbVal<{t.__name__}>"], pv.typeString()))
        return
    err.raiseFormattedError(err.customTypeError(lines, lineNum, [t.__name__, f"ProbVal<{t.__name__}>"], type(pv).__name__))


def convertToDensity(lines, lineNum, val):
    if isinstance(val, ProbVal):
        try:
            return val.toDensityMatrix()
        except:
            err.raiseFormattedError(err.customTypeError(lines, lineNum, ['np.ndarray', 'ProbVal<np.ndarray>'], val.typeString()))

    if not isinstance(val, np.ndarray):
        err.raiseFormattedError(err.customTypeError(lines, lineNum, ['np.ndarray', 'ProbVal<np.ndarray>'], type(val).__name__))

    if len(val.shape) == 1:
        np.outer(val, val)
    return val


def setVal(localNameSpace, lines, lineNum, key, value, qset = True):
    if qset:
        localNameSpace[key] = convertToDensity(lines, lineNum, value)
        localNameSpace[f'__is_q_{key}'] = True
    else:
        localNameSpace[key] = value
        localNameSpace[f'__is_q_{key}'] = False

    localNameSpace[f'__updated_{key}'] = True


def _ensureContainerErr(lines, lineNum, val, requiredType):
    a = [f'{x}<{str(requiredType)}>' for x in ('list', 'set', 'tuple')]
    a.append(requiredType)
    b = [f'ProbVal<{x}>' for x in a]
    a.extend(b)
    err.raiseFormattedError(err.customTypeError(lines, lineNum, b, type(val).__name__))

def ensureContainer(lines, lineNum, val, requiredType = int):
    '''puts value in a container if it isnt already, also typechecks value'''
    if isinstance(val,list) or isinstance(val, set) or isinstance(val, tuple):
        for item in val:
            if not isinstance(item, requiredType):
                _ensureContainerErr(lines, lineNum, val, requiredType)
        return val

    if isinstance(val, ProbVal):
        for i,pvItem in enumerate(val.values):
            if isinstance(pvItem,list) or isinstance(pvItem, set) or isinstance(pvItem, tuple):
                for item in pvItem:
                    if not isinstance(item, requiredType):
                        _ensureContainerErr(lines, lineNum, val, requiredType)
                continue

            if not isinstance(pvItem, requiredType):
                _ensureContainerErr(lines, lineNum, val, requiredType)
            val.values[i] = [pvItem]
        return val

    if not isinstance(val, requiredType):
        _ensureContainerErr(lines, lineNum, val, requiredType)
    return [val]


# operations
# MARK: removed probval control flow
class OpReturnVal:
    jumpLineNum: Union[int, None]#, ProbVal]
    joinLineNum: Union[int, None]
    halt: Union[bool]#, ProbVal]
    def __init__(self, jumpLineNum = None, joinLineNum = None, halt = False):
        self.jumpLineNum = jumpLineNum
        self.joinLineNum = joinLineNum
        self.halt = halt

OpReturn = Union[OpReturnVal, None]


def _qset(val, localNameSpace, lines, lineNum, numQubits, targets):
    for target in targets:
        if target < 0 or target > numQubits - 1:
            err.raiseFormattedError(err.customIndexError(lines, lineNum, 'target', target, numQubits - 1))

    try:
        return density.replaceArbitrary(localNameSpace['state'], val, targets)
    except ValueError as e:
        err.raiseFormattedError(err.pythonError(lines,lineNum, e))

def qset(localNameSpace, lines, lineNum, tokens) -> OpReturn:
    '''sets current hilbertspace (or some subspace of it) to a specific value'''

    numQubits = hilbertSpaceNumQubits(localNameSpace['state'])

    x = evaluateWrapper(lines, lineNum, tokens[1], localNameSpace)
    val = convertToDensity(lines, lineNum, x)

    if len(tokens) == 2:
        setVal(localNameSpace, lines, lineNum, 'state', val, qset = True)
        return
    else:
        targets = ensureContainer(lines, lineNum, evaluateWrapper(lines, lineNum, tokens[2], localNameSpace))

        if isinstance(targets, ProbVal):
            density = funcWrapper(_qset, val, localNameSpace, lines, lineNum, numQubits, targets)
            if isinstance(density, ProbVal):
                density = density.toDensityMatrix()
            setVal(localNameSpace, lines, lineNum, 'state', density, qset = True)
            return

        density = _qset(val, localNameSpace, lines, lineNum, numQubits, targets)
        setVal(localNameSpace, lines, lineNum, 'state', density, qset = True)
        return


def _disc(localNameSpace, lines, lineNum, numQubits, targets):
    for target in targets:
        if target < 0 or target > numQubits - 1:
            err.raiseFormattedError(err.customIndexError(lines, lineNum, 'target', target, numQubits - 1))

    _, val = density.partialTraceArbitrary(localNameSpace['state'], numQubits, targets)
    return val

def disc(localNameSpace, lines, lineNum, tokens) -> OpReturn:
    numQubits = hilbertSpaceNumQubits(localNameSpace['state'])

    targets = ensureContainer(lines, lineNum, evaluateWrapper(lines, lineNum, tokens[1], localNameSpace))

    if isinstance(targets, ProbVal):
        val = funcWrapper(_disc, localNameSpace, lines, lineNum, numQubits, targets)
        setVal(localNameSpace, lines, lineNum, 'state', convertToDensity(lines, lineNum, val), qset = True)
        return

    val = _disc(localNameSpace, lines, lineNum, numQubits, targets)
    setVal(localNameSpace, lines, lineNum, 'state', convertToDensity(lines, lineNum, val), qset = True)


def jump(localNameSpace, lines, lineNum, tokens) -> OpReturn:
    localNameSpace['__prev_jump'] = lineNum
    return OpReturnVal(getMarkLineNum(localNameSpace, lines, lineNum, tokens[1]))


def cjmp(localNameSpace, lines, lineNum, tokens) -> OpReturn:
    markLineNum = getMarkLineNum(localNameSpace, lines, lineNum, tokens[1])
    cond = evaluateWrapper(lines, lineNum, tokens[2], localNameSpace)
    if isinstance(cond, ProbVal):
        # MARK: removed probval control flow
        err.raiseFormattedError(err.customTypeError(lines, lineNum, ['bool'], cond.typeString()))
        #if not isinstance(cond.instance(), bool):
        #    err.raiseFormattedError(err.customTypeError(lines, lineNum, ['bool', 'ProbVal<bool>'], cond.typeString()))
        #if cond.values[0]:
        #    trueProb = cond.probs[0]
        #    falseProb = cond.probs[1]

        #    assert not cond.values[1]
        #else:
        #    trueProb = cond.probs[1]
        #    falseProb = cond.probs[0]

        #    assert not cond.values[0]
        #    assert cond.values[1]

        #if not len(tokens) == 4:
        #    err.raiseFormattedError(err.customProbValCjmpError(lines, lineNum))
        #joinLineNum = getMarkLineNum(localNameSpace, lines, lineNum, tokens[3])

        #jumpLineNum = ProbVal.fromUnzipped([trueProb, falseProb], [markLineNum, lineNum + 1])
        #return OpReturnVal(jumpLineNum, joinLineNum)

    elif isinstance(cond, bool):
        if cond:
            localNameSpace['__prev_jump'] = lineNum
            return OpReturnVal(markLineNum)
        return

    else:
        # MARK: removed probval control flow
        err.raiseFormattedError( err.customTypeError(lines, lineNum, ['bool'], type(cond).__name__) )
        #err.raiseFormattedError( err.customTypeError(lines, lineNum, ['bool', 'ProbVal<bool>'], type(cond).__name__) )


def qjmp(localNameSpace, lines, lineNum, tokens) -> OpReturn:
    raise NotImplementedError()


def cdef(localNameSpace, lines, lineNum, tokens) -> OpReturn:
    varName = getVarName(lines, lineNum, tokens[1])

    val = evaluateWrapper(lines, lineNum, tokens[2], localNameSpace)
    setVal(localNameSpace, lines, lineNum, varName, val, qset = False)


def qdef(localNameSpace, lines, lineNum, tokens) -> OpReturn:
    varName = getVarName(lines, lineNum, tokens[1])

    expr = tokens[2]
    val = convertToDensity(lines, lineNum, evaluateWrapper(lines, lineNum, expr, localNameSpace))
    localNameSpace[varName] = val
    setVal(localNameSpace, lines, lineNum, varName, val, qset = True)


def _gate(lines, lineNum, numQubits, contorls, firstTarget, gate):
    gateSize = hilbertSpaceNumQubits(gate)
    lastTarget = firstTarget+gateSize - 1
    if firstTarget < 0 or lastTarget > numQubits - 1:
        err.raiseFormattedError(err.customIndexError(lines, lineNum, 'target', firstTarget, numQubits - gateSize))

    if len(contorls) == 0:
        return gates.genGateForFullHilbertSpace(numQubits, firstTarget, gate)

    for control in contorls:
        if control < 0 or control > numQubits-1:
            err.raiseFormattedError(err.customIndexError(lines, lineNum, 'control', control, numQubits-1))

        if control >= firstTarget and control <= lastTarget:
            err.raiseFormattedError(err.customControlTargetOverlapError(lines, lineNum, control, firstTarget, lastTarget))

    return gates.genMultiControlledGate(numQubits, contorls, firstTarget, gate)


def gate(localNameSpace, lines, lineNum, tokens) -> OpReturn:
    
    numQubits = hilbertSpaceNumQubits(localNameSpace['state'])

    gate = evaluateWrapper(lines, lineNum, tokens[1], localNameSpace)

    # no targets
    if len(tokens) < 3:
        firstTarget = 0
    # target specified
    else:
        firstTarget = evaluateWrapper(lines, lineNum, tokens[2], localNameSpace)
        assertProbValType(lines, lineNum, firstTarget, int)

    # no controls
    if len(tokens) < 4:
        controls = []
    # controls
    else:
        controls = ensureContainer(lines, lineNum, evaluateWrapper(lines, lineNum, tokens[3], localNameSpace))

    # no conditional application
    if len(tokens) < 5:
        applicationCondition = True
    # conditional application
    else:
        applicationCondition  = evaluateWrapper(lines, lineNum, tokens[4], localNameSpace)
        assertProbValType(lines, lineNum, applicationCondition, bool)

    # early exit
    if not isinstance(applicationCondition, ProbVal) and not applicationCondition:
        return

    try:
        g = funcWrapper( _gate, lines, lineNum, numQubits, controls, firstTarget, gate )
    except Exception as e:
        err.raiseFormattedError(err.pythonError(lines, lineNum ,e))


    if isinstance(g, ProbVal):
        for i in range(len(g.values)):
            g.values[i] = gates.applyGate(g.values[i], localNameSpace['state'])
        val = g.toDensityMatrix()
    elif isinstance(g, np.ndarray):
        val = gates.applyGate(g, localNameSpace['state'])
    else:
        raise Exception("gate is not array or ProbVal")


    if isinstance(applicationCondition, ProbVal):
        if applicationCondition.values[0]:
            val = density.densityEnsambleToDensity(applicationCondition.probs, [val, localNameSpace['state']])
        else:
            val = density.densityEnsambleToDensity(applicationCondition.probs, [localNameSpace['state'], val])

    setVal(localNameSpace, lines, lineNum, 'state', val, qset = True)


def perm(localNameSpace, lines, lineNum, tokens) -> OpReturn:
    raise NotImplementedError("Convert this to using qubit map instead of statemap")
    hilbertDim = hilbertSpaceDim(localNameSpace['state'])
    numQubits = hilbertSpaceNumQubits(localNameSpace['state'])


    func = evaluateWrapper(lines, lineNum, tokens[1], localNameSpace)
    assertProbValType(lines, lineNum, func, Callable)

    try:
        permGate = funcWrapper( gates.genArbitrarySwap, hilbertDim, func )
    except Exception as e:
        err.raiseFormattedError(err.pythonError(lines, lineNum, e))

    try:
        g = funcWrapper( _gate, lines, lineNum, numQubits, [], 0, permGate )

    except Exception as e:
        err.raiseFormattedError(err.pythonError(lines, lineNum ,e))

    if isinstance(g, ProbVal):
        for i in range(len(g.values)):
            g.values[i] = gates.applyGate(g.values[i], localNameSpace['state'])
        val = g.toDensityMatrix()
    elif isinstance(g, np.ndarray):
        val = gates.applyGate(g, localNameSpace['state'])
    else:
        raise Exception("permGate is not array or ProbVal")

    setVal(localNameSpace, lines, lineNum, 'state', val, qset = True)


def _swap(lines, lineNum, numQubits, qubitA, qubitB):
    if qubitA < 0 or qubitA >= numQubits:
        err.raiseFormattedError(err.customIndexError(lines, lineNum, 'target', qubitA, numQubits - 1))
    if qubitB < 0 or qubitB >= numQubits:
        err.raiseFormattedError(err.customIndexError(lines, lineNum, 'target', qubitB, numQubits - 1))

    return gates.genSwapGate(numQubits, qubitA, qubitB)

def swap(localNameSpace, lines, lineNum, tokens) -> OpReturn:
    numQubits = hilbertSpaceNumQubits(localNameSpace['state'])

    a = evaluateWrapper(lines, lineNum, tokens[1], localNameSpace)
    b = evaluateWrapper(lines, lineNum, tokens[2], localNameSpace)
    assertProbValType(lines, lineNum, a, int)
    assertProbValType(lines, lineNum, b, int)
    try:
        swapGate = funcWrapper( _swap, lines, lineNum, numQubits, a, b )
    except Exception as e:
        err.raiseFormattedError(err.pythonError(lines, lineNum, e))

    if isinstance(swapGate, ProbVal):
        for i in range(len(swapGate.values)):
            swapGate.values[i] = gates.applyGate(swapGate.values[i], localNameSpace['state'])
        val = swapGate.toDensityMatrix()
    elif isinstance(swapGate, np.ndarray):
        val = gates.applyGate(swapGate, localNameSpace['state'])
    else:
        raise Exception("swapGate is not array or ProbVal")

    setVal(localNameSpace, lines, lineNum, 'state', val, qset = True)


def meas(localNameSpace, lines, lineNum, tokens, changeState = True) -> OpReturn:
    varName = getVarName(lines, lineNum, tokens[1])

    measBasis = evaluateWrapper(lines, lineNum, tokens[2], localNameSpace)
    # TODO allow for probval basis
    if not isinstance(measBasis, basis.Basis):
        err.raiseFormattedError(err.customTypeError(lines, lineNum, ['Basis'], type(measBasis).__name__))

    try:
        if len(tokens) < 4:
            result = measureArbitraryMultiState(localNameSpace['state'], measBasis, None, changeState)
        else:
            targets = ensureContainer(lines, lineNum, evaluateWrapper(lines, lineNum, tokens[3], localNameSpace))

            if isinstance(targets, ProbVal):
                result = funcWrapper(measureArbitraryMultiState, localNameSpace['state'], measBasis, targets, changeState)
            else:
                result = measureArbitraryMultiState(localNameSpace['state'], measBasis, targets, changeState)

    except MeasurementIndexError as e:
        err.raiseFormattedError(err.customIndexError(lines, lineNum, 'target', e.args[1], e.args[3]))
    except Exception as e:
        err.raiseFormattedError(err.pythonError(lines, lineNum, e))

    if isinstance(result, ProbVal):
        result = MeasurementResult.fromProbVal(result)

    localNameSpace[varName] = result
    if changeState:
        setVal(localNameSpace, lines, lineNum, 'state', result.newState, qset = True)

def peek(localNameSpace, lines, lineNum, tokens) -> OpReturn:
    return meas(localNameSpace, lines, lineNum, tokens, changeState = False)


def cout(localNameSpace, lines, lineNum, tokens) -> OpReturn:
    print(evaluateWrapper(lines, lineNum, tokens[1], localNameSpace))


def halt(localNameSpace, lines, lineNum, tokens) -> OpReturn:
    if len(tokens) < 2:
        return OpReturnVal(halt = True)

    val = evaluateWrapper(lines, lineNum, tokens[1], localNameSpace)

    if isinstance(val, bool):
        return OpReturnVal(halt = val)

    # MARK: removed probval control flow
    if isinstance(val, ProbVal):
        err.raiseFormattedError(err.customTypeError(lines, lineNum, ['bool'], val.typeString()))
    err.raiseFormattedError( err.customTypeError(lines, lineNum, ['bool'], type(val).__name__) )
    #if isinstance(val, ProbVal):
    #    if not isinstance(val.instance(), bool):
    #        err.raiseFormattedError(err.customTypeError(lines, lineNum, ['bool', 'ProbVal<bool>'], val.typeString()))
    #    return OpReturnVal(halt = val)

    #err.raiseFormattedError(err.customTypeError(lines, lineNum, ['bool', 'ProbVal<bool>'], type(val).__name__))

def retr(localNameSpace, lines, lineNum, tokens) -> OpReturn:
    if len(tokens) < 2:
        return OpReturnVal(jumpLineNum = localNameSpace['__prev_jump'] + 1)

    val = evaluateWrapper(lines, lineNum, tokens[1], localNameSpace)

    if isinstance(val, bool):
        if val:
            return OpReturnVal(jumpLineNum = localNameSpace['__prev_jump'] + 1)
        return

    if isinstance(val, ProbVal):
        err.raiseFormattedError(err.customTypeError(lines, lineNum, ['bool'], val.typeString()))
    err.raiseFormattedError( err.customTypeError(lines, lineNum, ['bool'], type(val).__name__) )


def pydo(localNameSpace, lines, lineNum, tokens) -> OpReturn:
    _ = evaluateWrapper(lines, lineNum, tokens[1], localNameSpace)



# "op_name: (func, arg_range_start, arg_range_end),
operations = {
    # Defines
    'cdef': (cdef, 2, 2),
    'qdef': (qdef, 2, 2),

    # State Manipulation
    'qset': (qset, 1, 2),
    'gate': (gate, 1, 4),
    'disc': (disc, 1, 1),
    'swap': (swap, 2, 2),
    #'perm': (perm, 1, 1),

    # Measurement
    'meas': (meas, 2, 3),
    'peek': (peek, 2, 3),

    # Control Flow
    'jump': (jump, 1, 1),
    # MARK: removed probval control flow
    'cjmp': (cjmp, 2, 2),#3),
    #'qjmp': (qjmp, 2, 2),
    'halt': (halt, 0, 1),
    'retr': (retr, 0, 1),
    # also includes mark

    # Misc
    'pydo': (pydo, 1, 1),
    'cout': (cout, 1, 1),
    # also includes note
}

