import numpy as np

import qbot.basis as basis
from qbot.probVal import ProbVal, funcWrapper
from qbot.evaluation import evaluateWrapper
from qbot.measurement import measureArbitraryMultiState, MeasurementResult
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
        err.raiseFormattedError(err.InvalidVariableName(lines, lineNum, token))
    return token


def getMarkLineNum(localNameSpace, lines, lineNum, token) -> int:
    if token.isidentifier() and token in localNameSpace['__marks'].keys():
        return localNameSpace['__marks'][token]

    res = evaluateWrapper(lines, lineNum, token, localNameSpace)
    if isinstance(res, str):
        try:
            return localNameSpace['__marks'][res]
        except KeyError:
            err.raiseFormattedError(err.UnknownMarkName(lines, lineNum, token))

    err.raiseFormattedError(err.customTypeError(lines, lineNum, ['str'], type(res)))


def convertToDensity(lines, lineNum, val):
    if isinstance(val, ProbVal):
        try:
            return val.toDensityMatrix()
        except:
            err.raiseFormattedError(err.customTypeError(lines, lineNum, ['np.ndarray', 'ProbVal<np.ndarray>'], val.typeString()))

    if not isinstance(val, np.ndarray):
        err.raiseFormattedError(err.customTypeError(lines, lineNum, ['np.ndarray', 'ProbVal<np.ndarray>'], type(val)))

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



# operations
class OpReturnVal:
    jumpLineNum: Union[int, ProbVal]
    joinLineNum: Union[int, None]
    def __init__(self, jumpLineNum, joinLineNum = None):
        self.jumpLineNum = jumpLineNum
        self.joinLineNum = joinLineNum

OpReturn = Union[OpReturnVal, None]


def _qset(val, localNameSpace, lines, lineNum, numQubits, targets):
    for target in targets:
        if target < 0 or target > numQubits - 1:
            err.raiseFormattedError(err.customIndexError(lines, lineNum, 'target', target, numQubits - 1))

    try:
        setVal(localNameSpace, lines, lineNum, 'state', density.replaceArbitrary(localNameSpace['state'], val, targets), qset = True)
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
        targets = evaluateWrapper(lines, lineNum, tokens[2], localNameSpace)

        if isinstance(targets, ProbVal):
            funcWrapper(_qset, localNameSpace['state'], localNameSpace, lines, lineNum, numQubits, targets)
            return

        if isinstance(targets, list) or isinstance(targets, tuple) or isinstance(targets, set):
            _qset(val, localNameSpace, lines, lineNum, numQubits, targets)
            return
        err.raiseFormattedError(err.customTypeError(lines, lineNum, ['list', 'tuple', 'set'], str(type(targets))))


def _disc(localNameSpace, lines, lineNum, numQubits, targets):
    for target in targets:
        if target < 0 or target > numQubits - 1:
            err.raiseFormattedError(err.customIndexError(lines, lineNum, 'target', target, numQubits - 1))

    _, val = density.partialTraceArbitrary(localNameSpace['state'], numQubits, targets)
    setVal(localNameSpace, lines, lineNum, 'state', val, qset = True)

def disc(localNameSpace, lines, lineNum, tokens) -> OpReturn:
    numQubits = hilbertSpaceNumQubits(localNameSpace['state'])

    targets = evaluateWrapper(lines, lineNum, tokens[1], localNameSpace)
    if isinstance(targets, ProbVal):
        funcWrapper(_disc, localNameSpace['state'], localNameSpace, lines, lineNum, numQubits, targets)
        return
    if isinstance(targets, list) or isinstance(targets, tuple) or isinstance(targets, set):
        _disc(localNameSpace, lines, lineNum, numQubits, targets)
        return
    err.raiseFormattedError(err.customTypeError(lines, lineNum, ['list', 'tuple', 'set'], str(type(targets))))


def jump(localNameSpace, lines, lineNum, tokens) -> OpReturn:
    return OpReturnVal(getMarkLineNum(localNameSpace, lines, lineNum, tokens[1]))


def cjmp(localNameSpace, lines, lineNum, tokens) -> OpReturn:
    markLineNum = getMarkLineNum()
    expr = tokens[2]
    raise NotImplementedError()


def qjmp(localNameSpace, lines, lineNum, tokens) -> OpReturn:
    raise NotImplementedError()


def cdef(localNameSpace, lines, lineNum, tokens) -> OpReturn:
    varName = getVarName(lines, lineNum, tokens[1])

    expr = tokens[2]
    val = evaluateWrapper(lines, lineNum, expr, localNameSpace)
    setVal(localNameSpace, lines, lineNum, varName, val, qset = False)


def qdef(localNameSpace, lines, lineNum, tokens) -> OpReturn:
    varName = getVarName(lines, lineNum, tokens[1])

    expr = tokens[2]
    val = convertToDensity(lines, lineNum, evaluateWrapper(lines, lineNum, expr, localNameSpace))
    localNameSpace[varName] = val
    setVal(localNameSpace, lines, lineNum, varName, val, qset = True)


def gate(localNameSpace, lines, lineNum, tokens) -> OpReturn:
    numQubits = hilbertSpaceNumQubits(localNameSpace['state'])

    gate = convertToDensity(lines, lineNum, evaluateWrapper(lines, lineNum, tokens[1], localNameSpace))
    firstTarget = evaluateWrapper(lines, lineNum, tokens[2], localNameSpace)

    if not (isinstance(firstTarget, ProbVal) or isinstance(firstTarget, int)):
        err.raiseFormattedError(err.customTypeError(lines, lineNum, ['int'], str(type(firstTarget))))

    # no controls
    if len(tokens) < 4:
        try:
            fullGate = convertToDensity(
                    lines, lineNum, 
                    funcWrapper( gates.genGateForFullHilbertSpace, numQubits, firstTarget, gate )
                )

        except Exception as e:
            err.raiseFormattedError(err.pythonError(lines, lineNum ,e))

    # controls
    else: 
        controls = evaluateWrapper(lines, lineNum, tokens[3], localNameSpace)
        # TODO ensure controls and targets dont overlap
        if not (isinstance(controls, ProbVal) or isinstance(controls, list) or isinstance(controls, tuple) or isinstance(controls, set)):
            err.raiseFormattedError(err.customTypeError(lines, lineNum, ['list', 'tuple', 'set'], str(type(firstTarget))))

        try:
            fullGate = convertToDensity(
                    lines, lineNum, 
                    funcWrapper( gates.genMultiControlledGate, numQubits, controls, firstTarget, gate )
                )

        except Exception as e:
            err.raiseFormattedError(err.pythonError(lines, lineNum ,e))

    val = gates.applyGate(fullGate, localNameSpace['state'])
    setVal(localNameSpace, lines, lineNum, 'state', val, qset = True)



def perm(localNameSpace, lines, lineNum, tokens) -> OpReturn:
    raise NotImplementedError()


def meas(localNameSpace, lines, lineNum, tokens) -> OpReturn:
    varName = getVarName(lines, lineNum, tokens[1])

    b = evaluateWrapper(lines, lineNum, tokens[2], localNameSpace)
    # TODO allow for probval basis
    if not isinstance(b, basis.Basis):
        err.raiseFormattedError(err.customTypeError(lines, lineNum, ['Basis'], str(type(b))))

    try:
        if len(tokens) < 4:
            result = measureArbitraryMultiState(localNameSpace['state'], b)
        else:
            targets = evaluateWrapper(lines, lineNum, tokens[3], localNameSpace)
            if isinstance(targets, list):
                result = measureArbitraryMultiState(localNameSpace['state'], b, targets)
            elif isinstance(targets, ProbVal):
                result = funcWrapper(measureArbitraryMultiState, localNameSpace['state'], b, targets)
            else:
                err.raiseFormattedError(err.customTypeError(lines, lineNum, ['list<int>', 'ProbVal<list<int>>'], str(type(b))))
    except Exception as e:
        err.raiseFormattedError(err.pythonError(lines, lineNum, e))

    if isinstance(result, ProbVal):
        result = MeasurementResult.fromProbVal(result)

    localNameSpace[varName] = result


def cout(localNameSpace, lines, lineNum, tokens) -> OpReturn:
    print(evaluateWrapper(lines, lineNum, tokens[1], localNameSpace))



# "op_name: (func, arg_range_start, arg_range_end),
operations = {
    'qset': (qset, 1, 2),
    'disc': (disc, 1, 1),
    'jump': (jump, 1, 1),
    'cjmp': (cjmp, 2, 2),
    'qjmp': (qjmp, 2, 2),
    'cdef': (cdef, 2, 2),
    'qdef': (qdef, 2, 2),
    'gate': (gate, 2, 3),
    'perm': (perm, 1, 1),
    'meas': (meas, 2, 3),
    #'mark': (mark, 1, 1),
    'cout': (cout, 1, 1),
}
