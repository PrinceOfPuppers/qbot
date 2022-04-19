import math
import numpy as np
from qbot.evaluation import evaluate
import sys

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

def InvalidOperationError(lines, lineNum, op):
    return formatError(lines, lineNum, "InvalidOperation", op)

def InvalidVariableName(lines, lineNum, varName):
    return formatError(lines, lineNum, "InvalidVariableName", varName)

def NumArgumentsError(lines, lineNum, op, numArgsGiven, numRequiredMin, numRequiredMax = -1):
    if numRequiredMax < numRequiredMin:
        return formatError(lines, lineNum, "NumArgumentsError", f"operation {op} requires {numRequiredMin}-{numRequiredMax} arguments ({numArgsGiven} given)")
    return formatError(lines, lineNum, "NumArgumentsError", f"operation {op} requires {numRequiredMin} argument(s) ({numArgsGiven} given)")

# operations
def qset(hilbertSpace, localNameSpace, lines, lineNum, tokens):
    '''sets current hilbertspace (or some subspace of it) to a specific value'''
    raise NotImplementedError()

def jump(hilbertSpace, localNameSpace, lines, lineNum, tokens):
    raise NotImplementedError()

def cjmp(hilbertSpace, localNameSpace, lines, lineNum, tokens):
    raise NotImplementedError()

def qjmp(hilbertSpace, localNameSpace, lines, lineNum, tokens):
    raise NotImplementedError()

def cdef(hilbertSpace, localNameSpace, lines, lineNum, tokens):
    name:str = tokens[1]
    if not name.isidentifier():
        raiseFormattedError(InvalidVariableName(lines, lineNum, name))

    expr = tokens[2]
    val = evaluate(expr, localNameSpace)
    localNameSpace[name] = val

def qdef(hilbertSpace, localNameSpace, lines, lineNum, tokens):
    raise NotImplementedError()

def gate(hilbertSpace, localNameSpace, lines, lineNum, tokens):
    raise NotImplementedError()

def perm(hilbertSpace, localNameSpace, lines, lineNum, tokens):
    raise NotImplementedError()

def meas(hilbertSpace, localNameSpace, lines, lineNum, tokens):
    raise NotImplementedError()

def mark(hilbertSpace, localNameSpace, lines, lineNum, tokens):
    raise NotImplementedError()

def cout(hilbertSpace, localNameSpace, lines, lineNum, tokens):
    print(evaluate(tokens[1], localNameSpace))

# "op_name: (func, arg_range_start, arg_range_end),
operations = {
    'qset': (qset, 1, 2),
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
    hilbertSpace = None
    #raise NotImplementedError("init hilberSpace")
    localNameSpace = {
        'state': hilbertSpace
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
            raiseFormattedError(InvalidOperationError(lines, lineNum, tokens[0]))

        numArgs = len(tokens) - 1
        if numArgs < argRangeStart or numArgs > argRangeEnd:
            raiseFormattedError(NumArgumentsError(lines, lineNum, tokens[0], numArgs, argRangeStart, argRangeEnd))

        op(hilbertSpace, localNameSpace, lines, lineNum, tokens)

