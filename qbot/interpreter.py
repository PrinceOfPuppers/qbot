import math
import numpy as np
from qbot.evaluation import evaluateWrapper, globalNameSpace
import qbot.qgates as gates
import qbot.density as density
import qbot.basis as basis
from qbot.probVal import ProbVal, funcWrapper
from qbot.measurement import measureArbitraryMultiState, MeasurementResult
import qbot.errors as err
import sys

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


def hilbertSpaceNumQubits(hilbertSpace):
    if len(hilbertSpace.shape) == 0 or hilbertSpace.size == 0:
        return 0
    return int(np.log2(hilbertSpace.shape[0]))

def getVarName(lines, lineNum, token):
    if not token.isidentifier():
        err.raiseFormattedError(err.InvalidVariableName(lines, lineNum, token))
    return token



# operations
def _qset(val, localNameSpace, lines, lineNum, numQubits, targets):
    for target in targets:
        if target < 0 or target > numQubits - 1:
            err.raiseFormattedError(err.customIndexError(lines, lineNum, 'target', target, numQubits - 1))

    try:
        localNameSpace['state'] = density.replaceArbitrary(localNameSpace['state'], val, targets)
    except ValueError as e:
        err.raiseFormattedError(err.pythonError(lines,lineNum, e))



def qset(localNameSpace, lines, lineNum, tokens):

    '''sets current hilbertspace (or some subspace of it) to a specific value'''
    numQubits = hilbertSpaceNumQubits(localNameSpace['state'])

    expr:str = tokens[1]

    x = evaluateWrapper(lines, lineNum, expr, localNameSpace)
    val = convertToDensity(lines, lineNum, x)

    if len(tokens) == 2:
        localNameSpace['state'] = val
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

    _, localNameSpace['state'] = density.partialTraceArbitrary(localNameSpace['state'], numQubits, targets)

def disc(localNameSpace, lines, lineNum, tokens):
    numQubits = hilbertSpaceNumQubits(localNameSpace['state'])

    targets = evaluateWrapper(lines, lineNum, tokens[1], localNameSpace)
    if isinstance(targets, ProbVal):
        funcWrapper(_disc, localNameSpace['state'], localNameSpace, lines, lineNum, numQubits, targets)
        return
    if isinstance(targets, list) or isinstance(targets, tuple) or isinstance(targets, set):
        _disc(localNameSpace, lines, lineNum, numQubits, targets)
        return
    err.raiseFormattedError(err.customTypeError(lines, lineNum, ['list', 'tuple', 'set'], str(type(targets))))


def jump(localNameSpace, lines, lineNum, tokens):
    markName = tokens[1]
    if not markName.isidentifier():
        err.raiseFormattedError(err.InvalidMarkName(lines, lineNum, markName))
    try:
        markLineNum = localNameSpace['__marks'][markName]
    except KeyError:
        err.raiseFormattedError(err.UnknownMarkName(lines, lineNum, markName))

    return markLineNum

def cjmp(localNameSpace, lines, lineNum, tokens):
    raise NotImplementedError()

def qjmp(localNameSpace, lines, lineNum, tokens):
    raise NotImplementedError()

def cdef(localNameSpace, lines, lineNum, tokens):
    varName = getVarName(lines, lineNum, tokens[1])

    expr = tokens[2]
    val = evaluateWrapper(lines, lineNum, expr, localNameSpace)
    localNameSpace[varName] = val

def qdef(localNameSpace, lines, lineNum, tokens):
    varName = getVarName(lines, lineNum, tokens[1])

    expr = tokens[2]
    val = convertToDensity(lines, lineNum, evaluateWrapper(lines, lineNum, expr, localNameSpace))
    localNameSpace[varName] = val


def gate(localNameSpace, lines, lineNum, tokens):
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

    localNameSpace['state'] = gates.applyGate(fullGate, localNameSpace['state'])




    



def perm(localNameSpace, lines, lineNum, tokens):
    raise NotImplementedError()

def meas(localNameSpace, lines, lineNum, tokens):
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


def mark(localNameSpace, lines, lineNum, tokens):
    markName = tokens[1]
    if not markName.isidentifier():
        err.raiseFormattedError(err.InvalidMarkName(lines, lineNum, markName))

    localNameSpace['__marks'][markName] = lineNum

def cout(localNameSpace, lines, lineNum, tokens):
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

def getOp(line:str):
    '''used when recording all marks in preprocessing step'''
    return line.strip()[:4].lower()

def processLineIntoTokens(line:str):
    tokens = []

    line = line.strip()

    if len(line) == 0:
        return tokens

    try:
        op = line[:4]
    except:
        return tokens

    if not op:
        return tokens

    tokens.append(op.lower())
    for s in line[4:].split(';'):
        s = s.strip()
        if s:
            tokens.append(s)

    return tokens


def executeTxt(text: str):
    lines = text.splitlines()
    state = np.array([], dtype = complex)
    localNameSpace = {
        'state': state,
        '__marks': dict()
    }

    # record marks
    for lineNum, line in enumerate(lines):
        if getOp(line) == 'mark':
            tokens = processLineIntoTokens(line)
            mark(localNameSpace, lines, lineNum, tokens)

    lineNum = -1
    while lineNum < len(lines) - 1:
        lineNum += 1
        tokens = processLineIntoTokens(lines[lineNum])

        if len(tokens) == 0:
            continue

        tokens[0] = tokens[0].lower()
        if tokens[0] == 'note' or tokens[0] == 'mark':
            continue

        try:
            op, argRangeStart, argRangeEnd = operations[tokens[0]]
        except KeyError:
            err.raiseFormattedError(err.UnknownOperationError(lines, lineNum, tokens[0]))

        numArgs = len(tokens) - 1
        if numArgs < argRangeStart or numArgs > argRangeEnd:
            err.raiseFormattedError(err.NumArgumentsError(lines, lineNum, tokens[0], numArgs, argRangeStart, argRangeEnd))

        newLineNum = op(localNameSpace, lines, lineNum, tokens)
        if newLineNum is not None:
            lineNum = newLineNum

