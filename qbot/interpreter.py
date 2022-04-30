import math
import numpy as np
from qbot.evaluation import evaluateWrapper, globalNameSpace
import qbot.qgates as gates
import qbot.density as density
from qbot.probVal import ProbVal, funcWrapper
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
    if len(hilbertSpace.shape) == 0:
        return 0
    return int(np.log2(hilbertSpace.shape[0]))


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
    raise NotImplementedError()

def cjmp(localNameSpace, lines, lineNum, tokens):
    raise NotImplementedError()

def qjmp(localNameSpace, lines, lineNum, tokens):
    raise NotImplementedError()

def cdef(localNameSpace, lines, lineNum, tokens):
    name:str = tokens[1]
    if not name.isidentifier():
        err.raiseFormattedError(err.InvalidVariableName(lines, lineNum, name))

    expr = tokens[2]
    val = evaluateWrapper(lines, lineNum, expr, localNameSpace)
    localNameSpace[name] = val

def qdef(localNameSpace, lines, lineNum, tokens):
    name:str = tokens[1]
    if not name.isidentifier():
        err.raiseFormattedError(err.InvalidVariableName(lines, lineNum, name))

    expr = tokens[2]
    val = convertToDensity(lines, lineNum, evaluateWrapper(lines, lineNum, expr, localNameSpace))
    localNameSpace[name] = val


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
    name = tokens[0].lower()

    for b in allBasis:
        if name in b.names:
            return

    err.raiseFormattedError(err.unknownBasis(lines, lineNum, name))


    raise NotImplementedError()

def mark(localNameSpace, lines, lineNum, tokens):
    raise NotImplementedError()

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
    'meas': (meas, 2, 2),
    'mark': (mark, 1, 1),
    'cout': (cout, 1, 1),
}

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

    tokens.append(op)
    for s in line[4:].split(';'):
        s = s.strip()
        if s:
            tokens.append(s)

    return tokens


def executeTxt(text: str):
    lines = text.splitlines()
    state = np.ndarray([], dtype = complex)
    localNameSpace = {
        'state': state
    }

    lineNum = -1
    while lineNum < len(lines) - 1:
        lineNum += 1
        tokens = processLineIntoTokens(lines[lineNum])

        if len(tokens) == 0:
            continue

        tokens[0] = tokens[0].lower()
        if tokens[0] == 'note':
            continue

        try:
            op, argRangeStart, argRangeEnd = operations[tokens[0]]
        except KeyError:
            err.raiseFormattedError(err.UnknownOperationError(lines, lineNum, tokens[0]))

        numArgs = len(tokens) - 1
        if numArgs < argRangeStart or numArgs > argRangeEnd:
            err.raiseFormattedError(err.NumArgumentsError(lines, lineNum, tokens[0], numArgs, argRangeStart, argRangeEnd))

        op(localNameSpace, lines, lineNum, tokens)

