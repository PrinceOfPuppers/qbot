import sys
import qbot.basis as basis

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

def InvalidMarkName(lines, lineNum, markName):
    return formatError(lines, lineNum, "InvalidMarkName", markName)

def UnknownMarkName(lines, lineNum, markName):
    return formatError(lines, lineNum, "UnknownMarkName", markName)

def NumArgumentsError(lines, lineNum, op, numArgsGiven, numRequiredMin, numRequiredMax = -1):
    if numRequiredMax < numRequiredMin:
        return formatError(lines, lineNum, "NumArgumentsError", f"operation {op} requires {numRequiredMin}-{numRequiredMax} arguments ({numArgsGiven} given)")
    return formatError(lines, lineNum, "NumArgumentsError", f"operation {op} requires {numRequiredMin} argument(s) ({numArgsGiven} given)")

def customIndexError(lines, lineNum, targetOrControl, index, maxIndex, minIndex = 0):
    return formatError(lines, lineNum, "IndexError", f"{targetOrControl} index {index} outside of valid range [{minIndex}, {maxIndex}]")

def customTypeError(lines, lineNum, expectedTypes:list[str], gotType:str):
    if len(expectedTypes) > 1:
        expectedTypeStr = f"any of {expectedTypes}"
    else:
        expectedTypeStr = f"{expectedTypes}"

    return formatError(lines, lineNum, "TypeError", f"{gotType} cannot be interpreted as {expectedTypeStr}")

def SizeError(lines, lineNum, str):
    return formatError(lines, lineNum, "SizeError", str)

def pythonError(lines, lineNum, e: Exception):
    return formatError(lines, lineNum, e.__class__.__name__, str(e))
