import numpy as np

import qbot.basis as basis
from qbot.probVal import ProbVal, funcWrapper
from qbot.evaluation import evaluateWrapper
from qbot.measurement import measureArbitraryMultiState, MeasurementResult, MeasurementIndexError
import qbot.density as density
import qbot.qgates as gates
import qbot.errors as err

from typing import Union



def hilbertSpaceNumQubits(hilbertSpace):
    if len(hilbertSpace.shape) == 0 or hilbertSpace.size == 0:
        return 0
    return int(np.log2(hilbertSpace.shape[0]))


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

    err.raiseFormattedError(err.customTypeError(lines, lineNum, ['str'], type(res).__name__))


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
class OpReturnVal:
    jumpLineNum: Union[int, ProbVal, None]
    joinLineNum: Union[int, None]
    halt: Union[bool, ProbVal]
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

    expr:str = tokens[1]

    x = evaluateWrapper(lines, lineNum, expr, localNameSpace)
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
        targetInst = targets.instance()
        if isinstance(targetInst, list) or isinstance(targetInst, tuple) or isinstance(targetInst, set):
            val = funcWrapper(_disc, localNameSpace, lines, lineNum, numQubits, targets)
            setVal(localNameSpace, lines, lineNum, 'state', convertToDensity(lines, lineNum, val), qset = True)
            return
        err.raiseFormattedError(err.customTypeError(lines, lineNum, ['list', 'tuple', 'set'], targets.typeString()))

    if isinstance(targets, list) or isinstance(targets, tuple) or isinstance(targets, set):
        val = _disc(localNameSpace, lines, lineNum, numQubits, targets)
        setVal(localNameSpace, lines, lineNum, 'state', convertToDensity(lines, lineNum, val), qset = True)
        return
    err.raiseFormattedError(err.customTypeError(lines, lineNum, ['list', 'tuple', 'set'], type(targets).__name__))


def jump(localNameSpace, lines, lineNum, tokens) -> OpReturn:
    return OpReturnVal(getMarkLineNum(localNameSpace, lines, lineNum, tokens[1]))


def cjmp(localNameSpace, lines, lineNum, tokens) -> OpReturn:
    markLineNum = getMarkLineNum(localNameSpace, lines, lineNum, tokens[1])
    cond = evaluateWrapper(lines, lineNum, tokens[2], localNameSpace)
    if isinstance(cond, ProbVal):
        if not isinstance(cond.instance(), bool):
            err.raiseFormattedError(err.customTypeError(lines, lineNum, ['bool', 'ProbVal<bool>'], cond.typeString()))

        if cond.values[0]:
            trueProb = cond.probs[0]
            falseProb = cond.probs[1]

            assert not cond.values[1]
        else:
            trueProb = cond.probs[1]
            falseProb = cond.probs[0]

            assert not cond.values[0]
            assert cond.values[1]

        if not len(tokens) == 4:
            err.raiseFormattedError(err.customProbValCjmpError(lines, lineNum))
        joinLineNum = getMarkLineNum(localNameSpace, lines, lineNum, tokens[3])

        jumpLineNum = ProbVal.fromUnzipped([trueProb, falseProb], [markLineNum, lineNum + 1])
        return OpReturnVal(jumpLineNum, joinLineNum)

    elif isinstance(cond, bool):
        if cond:
            return OpReturnVal(markLineNum)
        return

    else:
        err.raiseFormattedError( err.customTypeError(lines, lineNum, ['bool', 'ProbVal<bool>'], type(cond).__name__) )


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

    firstTarget = evaluateWrapper(lines, lineNum, tokens[2], localNameSpace)

    if isinstance(firstTarget, int):
        pass
    elif isinstance(firstTarget, ProbVal):
        if not isinstance(firstTarget.instance(), int):
            err.raiseFormattedError(err.customTypeError(lines, lineNum, ['int'], type(firstTarget).__name__))
    else:
        err.raiseFormattedError(err.customTypeError(lines, lineNum, ['int'], type(firstTarget).__name__))

    # no controls
    if len(tokens) < 4:
        try:
            g = funcWrapper( _gate, lines, lineNum, numQubits, [], firstTarget, gate )

        except Exception as e:
            err.raiseFormattedError(err.pythonError(lines, lineNum ,e))

    # controls
    else: 
        controls = ensureContainer(lines, lineNum, evaluateWrapper(lines, lineNum, tokens[3], localNameSpace))
        # TODO ensure controls and targets dont overlap

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

    setVal(localNameSpace, lines, lineNum, 'state', val, qset = True)


def perm(localNameSpace, lines, lineNum, tokens) -> OpReturn:
    raise NotImplementedError()


def meas(localNameSpace, lines, lineNum, tokens, changeState = True) -> OpReturn:
    varName = getVarName(lines, lineNum, tokens[1])

    measBasis = evaluateWrapper(lines, lineNum, tokens[2], localNameSpace)
    # TODO allow for probval basis
    if not isinstance(measBasis, basis.Basis):
        err.raiseFormattedError(err.customTypeError(lines, lineNum, ['Basis'], type(measBasis).__name__))

    try:
        if len(tokens) < 4:
            result = measureArbitraryMultiState(localNameSpace['state'], measBasis, changeState)
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

    if isinstance(val, ProbVal):
        if not isinstance(val.instance(), bool):
            err.raiseFormattedError(err.customTypeError(lines, lineNum, ['bool', 'ProbVal<bool>'], val.typeString()))
        return OpReturnVal(halt = val)

    err.raiseFormattedError(err.customTypeError(lines, lineNum, ['bool', 'ProbVal<bool>'], type(val).__name__))




# "op_name: (func, arg_range_start, arg_range_end),
operations = {
    'qset': (qset, 1, 2),
    'disc': (disc, 1, 1),
    'jump': (jump, 1, 1),
    'cjmp': (cjmp, 2, 3),
    #'qjmp': (qjmp, 2, 2),
    'cdef': (cdef, 2, 2),
    'qdef': (qdef, 2, 2),
    'gate': (gate, 2, 3),
    'perm': (perm, 1, 1),
    'meas': (meas, 2, 3),
    'peek': (peek, 2, 3),
    #'mark': (mark, 1, 1),
    'cout': (cout, 1, 1),
    'halt': (halt, 0, 1),
}

