import numpy as np
import qbot.density as density
from qbot.probVal import ProbVal
import qbot.errors as err
from qbot.operators import operations, OpReturn

def resetUpdates(localNameSpace):
    for key in localNameSpace.keys():
        if key.startswith('__updated_'):
            localNameSpace[key] = False

def collapseNamespaces(p1, n1, p2, n2) -> dict:
    '''merges n1 changes into n2 and returns n2'''
    # note the keys of newNameSpace are a superset of oldNameSpace (keys cannot be removed)

    for n1Key in n1.keys():
        if n1Key.startswith('__'):
            continue

        isUpdatedStr = f'__updated_{n1Key}'
        if not n1[isUpdatedStr]:
            continue

        
        isQstr = f'__is_q_{n1Key}'


        # value will be handled
        n2[isUpdatedStr] = False

        if n1Key in n2:
            # either existing key or key was added in both branches since split
            if n1[isQstr] and n2[isQstr]:
                density.densityEnsambleToDensity([n1[n1Key], n2[n1Key]], [p1, p2])
                continue

            n2[n1Key] = ProbVal.fromUnzipped([p1, p2], [n1[n1Key], n2[n1Key]])
            n2[isQstr] = False
            continue

        # key was added in n1 branch, does not exist in n2
        n2[n1Key] = ProbVal.fromUnzipped([p1, p2], [n1[n1Key], None])
        n2[isQstr] = False
        continue

    # we must now handle keys which where updated/added exclusivly in n2's branch
    for n2Key in n2.keys():
        if n2Key.startswith('__'):
            continue

        isUpdatedStr = f'__updated_{n2Key}'

        # skip all keys not updated on n2's branch, or handled by first loop
        if not n2[isUpdatedStr]:
            continue

        # value will be handled
        n2[isUpdatedStr] = False

        # key was added in n2 branch, does not exist in n1
        n2[n2Key] = ProbVal.fromUnzipped([p1, p2], [None, n2[n2Key]])
        n2[isQstr] = False

    return n2




def getOp(line:str):
    '''used when recording all marks in preprocessing step'''
    return line.strip()[:4].lower()

def mark(localNameSpace, lines, lineNum, tokens):
    markName = tokens[1]
    if not markName.isidentifier():
        err.raiseFormattedError(err.InvalidMarkName(lines, lineNum, markName))

    localNameSpace['__marks'][markName] = lineNum

def recordMarks(localNameSpace, lines):
    # record marks
    for lineNum, line in enumerate(lines):
        if getOp(line) == 'mark':
            tokens = processLineIntoTokens(line)
            mark(localNameSpace, lines, lineNum, tokens)


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

def runtime(localNameSpace, lines, startLine = 0, endLine = -1):
    '''line end is not inclusive'''
    startLine = max(startLine, 0)
    endLine = len(lines) if endLine == -1 or endLine > len(lines) else endLine

    lineNum = startLine-1
    while lineNum != endLine - 1 and lineNum < len(lines) - 1:
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

        ret:OpReturn = op(localNameSpace, lines, lineNum, tokens)
        # handle jumps
        if ret is None:
            continue
        if isinstance(ret.jumpLineNum, int):
            lineNum = ret.jumpLineNum - 1
            continue
        if isinstance(ret.jumpLineNum, ProbVal):
            assert ret.joinLineNum is not None
            assert len(ret.jumpLineNum.probs) == 2
            # duplicate localNameSpace and call runtime on each value
            branch1Line = ret.jumpLineNum.values[0]
            branch2Line = ret.jumpLineNum.values[1]

            branch1Prob = ret.jumpLineNum.probs[0]
            branch2Prob = ret.jumpLineNum.probs[1]

            joinLine = ret.joinLineNum

            print(f">>> ProbVal jump condition encountered: \n" \
                  f"branch 1:\n" \
                  f"    prob: {branch1Prob} ({branch1Prob*100}%)\n" \
                  f"    line: {branch1Line}\n" \
                  f"branch 2:\n" \
                  f"    prob: {branch2Prob} ({branch2Prob*100}%)\n" \
                  f"    line: {branch2Line}")


            resetUpdates(localNameSpace)

            print(f">>> taking branch 1")
            newLocalNameSpace = localNameSpace.copy()
            runtime(newLocalNameSpace, lines, branch1Line, joinLine + 1)

            print(f">>> taking branch 2")
            runtime(localNameSpace, lines, branch2Line, joinLine + 1)
            print(f">>> branches met on line {branch2Line}, merging them")

            localNameSpace = collapseNamespaces(branch1Prob, newLocalNameSpace, branch2Prob, localNameSpace)

            lineNum = branch2Line - 1
            continue

def executeTxt(text: str):
    lines = text.splitlines()
    state = np.array([], dtype = complex)
    localNameSpace = {
        'state': state,
        f'__updated_state': False,
        '__marks': dict()

    }

    recordMarks(localNameSpace, lines)
    runtime(localNameSpace, lines)


