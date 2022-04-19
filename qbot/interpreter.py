import math
import numpy as np
from qbot.evaluation import evaluate, nameSpace
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

def InvalidOperationError(lines, lineNum, op):
    return formatError(lines, lineNum, "InvalidOperation", op)

def NumArgumentsError(lines, lineNum, op, numArgsGiven, numRequiredMin, numRequiredMax = -1):
    if numRequiredMax <= numRequiredMin:
        return formatError(lines, lineNum, "NumArgumentsError", f"operation: {op} requires {numRequiredMin}-{numRequiredMax} arguments ({numArgsGiven} given)")
    return formatError(lines, lineNum, "NumArgumentsError", f"operation: {op} requires {numRequiredMin} argument(s) ({numArgsGiven} given)")

# operations
def jump(hilbertSpace, localNameSpace, lines, lineNum, tokens):
    raise NotImplementedError()

def cjmp(hilbertSpace, localNameSpace, lines, lineNum, tokens):
    raise NotImplementedError()

def qjmp(hilbertSpace, localNameSpace, lines, lineNum, tokens):
    raise NotImplementedError()

def cdef(hilbertSpace, localNameSpace, lines, lineNum, tokens):
    if len(tokens) != 3:
        raise
    raise NotImplementedError()

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
    raise NotImplementedError()

# "op_name: (func, arg_range_start, arg_range_end),
operations = {
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

def executeTxt(text: str):
    lines = text.split()
    lineNum = 0
    hilbertSpace = None
    #raise NotImplementedError("init hilberSpace")
    localNameSpace = {}
    while lineNum < len(lines):
        tokens = lines[lineNum].strip().split(' ')

        if len(tokens) == 0:
            continue

        tokens[0] = tokens[0].lower()
        if tokens[0] == 'note':
            continue

        try:
            op, argRangeStart, argRangeEnd = operations[tokens[0]]
        except KeyError:
            raiseFormattedError(InvalidOperationError(lines, lineNum, tokens[0]))
            sys.exit()

        numArgs = len(tokens) - 1
        if numArgs < argRangeStart or numArgs > argRangeEnd:
            raiseFormattedError(NumArgumentsError(lines, lineNum, tokens[0], numArgs, argRangeStart, argRangeEnd))
            sys.exit()

        op(hilbertSpace, localNameSpace, lines, hilbertSpace, localNameSpace, lines, lineNum, tokens)


