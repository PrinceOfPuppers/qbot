import math
import numpy as np
from qbot.evaluation import evaluate
from qbot.density import partialTraceArbitrary, replaceArbitrary
from qbot.probVal import ProbVal, funcWrapper
import sys

def convertToDensity(lines, lineNum, val):
    if isinstance(val, ProbVal):
        try:
            return val.toDensityMatrix()
        except:
            raiseFormattedError(customTypeError(lines, lineNum, ['np.ndarray', 'ProbVal<np.ndarray>'], val.typeString()))

    if not isinstance(val, np.ndarray):
        raiseFormattedError(customTypeError(lines, lineNum, ['np.ndarray', 'ProbVal<np.ndarray>'], type(val)))

    if len(val.shape) == 1:
        np.outer(val, val)
    return val




def padZeros(s, numDigits):
    return str(s).zfill(numDigits)

numLinesInErrorMessage = 5
def formatError(lines: list, lineNum: int, errorName: str, errorInfo: str):
    errorMessage = f"{errorName}: {errorInfo}"

    startIndex = max(int(lineNum - ((numLinesInErrorMessage - 1) / 2)), 0)
    endIndex = min(startIndex + numLinesInErrorMessage, len(lines))

    numDigits = len(str(endIndex - 1))

    for i in range(startIndex, lineNum):
        errorMessage += f"\n    {padZeros(i, numDigits)}: {lines[i]}"

    errorMessage += f"\n>>> {padZeros(lineNum, numDigits)}: {lines[lineNum]}"

    for i in range(lineNum + 1, endIndex):
        errorMessage += f"\n    {padZeros(i, numDigits)}: {lines[i]}"

    return errorMessage

def raiseFormattedError(error:str):
    print(error)
    sys.exit()

def UnknownOperationError(lines, lineNum, op):
    return formatError(lines, lineNum, "UnknownOperation", op)

def InvalidVariableName(lines, lineNum, varName):
    return formatError(lines, lineNum, "InvalidVariableName", varName)

def NumArgumentsError(lines, lineNum, op, numArgsGiven, numRequiredMin, numRequiredMax = -1):
    if numRequiredMax < numRequiredMin:
        return formatError(lines, lineNum, "NumArgumentsError", f"operation {op} requires {numRequiredMin}-{numRequiredMax} arguments ({numArgsGiven} given)")
    return formatError(lines, lineNum, "NumArgumentsError", f"operation {op} requires {numRequiredMin} argument(s) ({numArgsGiven} given)")

def customIndexError(lines, lineNum, targetOrControl, index, maxIndex, minIndex = 0):
    return formatError(lines, lineNum, "IndexError", f"{targetOrControl} index {index} outside of valid range [{minIndex}, {maxIndex}]")

def customTypeError(lines, lineNum, expectedTypes:list, gotType:str):
    if len(expectedTypes) > 1:
        expectedTypeStr = f"any of {expectedTypes}"
    else:
        expectedTypeStr = f"{expectedTypes}"

    return formatError(lines, lineNum, "TypeError", f"{gotType} cannot be interpreted as {expectedTypeStr}")

def SizeError(lines, lineNum, str):
    return formatError(lines, lineNum, "SizeError", str)

def pythonError(lines, lineNum, e: Exception):
    return formatError(lines, lineNum, e.__class__.__name__, str(e))


# operations
def _qset(val, localNameSpace, lines, lineNum, numQubits, targets):
    for target in targets:
        if target < 0 or target > numQubits - 1:
            raiseFormattedError(customIndexError(lines, lineNum, 'target', target, numQubits - 1))

    try:
        localNameSpace['state'] = replaceArbitrary(localNameSpace['state'], val, targets)
        print("here0\n", localNameSpace['state'])
    except ValueError as e:
        raiseFormattedError(pythonError(lines,lineNum, e))



def qset(localNameSpace, lines, lineNum, tokens):
    '''sets current hilbertspace (or some subspace of it) to a specific value'''
    if len(localNameSpace['state'].shape) == 0:
        numQubits = 0
    else:
        numQubits = np.log2(localNameSpace['state'].shape[0])

    expr:str = tokens[1]
    val = convertToDensity(lines, lineNum, evaluate(expr, localNameSpace))

    if len(tokens) == 2:
        localNameSpace['state'] = val
        print("here-1\n", localNameSpace['state'])
        return
    else:
        targets = evaluate(tokens[2], localNameSpace)

        if isinstance(targets, ProbVal):
            funcWrapper(_qset, localNameSpace['state'], localNameSpace, lines, lineNum, numQubits, targets)
            print("here1\n", localNameSpace['state'])
            return

        if isinstance(targets, list) or isinstance(targets, tuple) or isinstance(targets, set):
            _qset(val, localNameSpace, lines, lineNum, numQubits, targets)
            print("here2\n", localNameSpace['state'])
            return
        raiseFormattedError(customTypeError(lines, lineNum, ['list', 'tuple', 'set'], type(targets)))


def _disc(localNameSpace, lines, lineNum, numQubits, targets):
    for target in targets:
        if target < 0 or target > numQubits - 1:
            raiseFormattedError(customIndexError(lines, lineNum, 'target', target, numQubits - 1))

    _, localNameSpace['state'] = partialTraceArbitrary(localNameSpace['state'], numQubits, targets)

def disc(localNameSpace, lines, lineNum, tokens):
    numQubits = np.log2(localNameSpace['state'].shape[0])
    targets = evaluate(tokens[1], localNameSpace)
    if isinstance(targets, ProbVal):
        funcWrapper(_disc, localNameSpace['state'], localNameSpace, lines, lineNum, numQubits, targets)
        return
    if isinstance(targets, list) or isinstance(targets, tuple) or isinstance(targets, set):
        _disc(localNameSpace, lines, lineNum, numQubits, targets)
        return
    raiseFormattedError(customTypeError(lines, lineNum, ['list', 'tuple', 'set'], type(targets)))


def jump(localNameSpace, lines, lineNum, tokens):
    raise NotImplementedError()

def cjmp(localNameSpace, lines, lineNum, tokens):
    raise NotImplementedError()

def qjmp(localNameSpace, lines, lineNum, tokens):
    raise NotImplementedError()

def cdef(localNameSpace, lines, lineNum, tokens):
    name:str = tokens[1]
    if not name.isidentifier():
        raiseFormattedError(InvalidVariableName(lines, lineNum, name))

    expr = tokens[2]
    val = evaluate(expr, localNameSpace)
    localNameSpace[name] = val

def qdef(localNameSpace, lines, lineNum, tokens):
    name:str = tokens[1]
    if not name.isidentifier():
        raiseFormattedError(InvalidVariableName(lines, lineNum, name))

    expr = tokens[2]
    val = convertToDensity(lines, lineNum, evaluate(expr, localNameSpace))
    localNameSpace[name] = val


def gate(localNameSpace, lines, lineNum, tokens):
    raise NotImplementedError()

def perm(localNameSpace, lines, lineNum, tokens):
    raise NotImplementedError()

def meas(localNameSpace, lines, lineNum, tokens):
    raise NotImplementedError()

def mark(localNameSpace, lines, lineNum, tokens):
    raise NotImplementedError()

def cout(localNameSpace, lines, lineNum, tokens):
    print(evaluate(tokens[1], localNameSpace))

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
            raiseFormattedError(UnknownOperationError(lines, lineNum, tokens[0]))

        numArgs = len(tokens) - 1
        if numArgs < argRangeStart or numArgs > argRangeEnd:
            raiseFormattedError(NumArgumentsError(lines, lineNum, tokens[0], numArgs, argRangeStart, argRangeEnd))

        op(localNameSpace, lines, lineNum, tokens)

