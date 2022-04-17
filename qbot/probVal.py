from typing import List, Tuple
import math
import operator

smallVal = 1e-5
probRounding = 15

def valsClose(a, b):
    if isinstance(a, float):
        return abs(a-b) < smallVal
    return a == b

class ProbVal:
    probs: List[float]
    values: list

    def normalize(self):
        '''
        removes small probability values
        collapses duplicates
        ensures sum of all probabilites is 1
        '''

        i = 0
        while i < len(self.probs):
            # remove small probability values
            if self.probs[i] < smallVal:
                self.probs.pop(i)
                self.values.pop(i)
                continue

            # remove duplicate values
            j = i + 1
            while j < len(self.probs):
                if valsClose(self.values[i], self.values[j]):
                    self.probs.pop(j)
                    self.values.pop(j)
                    continue
                j+=1
            i += 1

        #normalize
        s = sum(self.probs)
        for i in range(len(self.probs)):
            self.probs[i] /= s
            self.probs[i] = round(self.probs[i], probRounding)

    def __init__(self, probs: List[float], values: list):
        self.probs = probs
        self.values = values
        self.normalize()

    @staticmethod
    def fromZipped(pairs:List[Tuple]):
        probs = []
        values = []
        for prob, value in pairs:
            probs.append(prob)
            values.append(value)
        return ProbVal(probs, values)

    def __unary(self, unaryOp, *args):
        newProbs = []
        newVals = []
        for i, val in enumerate(self.values):
            newProbs.append(self.probs[i])
            newVals.append(unaryOp(val, *args))
        return ProbVal(newProbs, newVals)

    def __comparison(self, other, compareOp):
        trueProb = 0
        falseProb = 0
        if isinstance(other,ProbVal):
            for i, prob1 in enumerate(self.probs):
                value1 = self.values[i]
                for j,prob2, in enumerate(other.probs):
                    value2 = other.values[j]
                    if compareOp(value1, value2):
                        trueProb += prob1 * prob2
                    else:
                        falseProb += prob1 * prob2
        else:
            for i, prob, in enumerate(self.probs):
                value = self.values[i]
                if compareOp(value, other):
                    trueProb += prob
                else:
                    falseProb += prob
        return ProbVal([trueProb, falseProb], [True, False])

    def __binary(self, other, binaryOp, reversed:bool):
        newProbs = []
        newVals = []
        if isinstance(other,ProbVal):
            for i, prob1 in enumerate(self.probs):
                value1 = self.values[i]
                for j,prob2, in enumerate(other.probs):
                    value2 = other.values[j]
                    if reversed:
                        newVals.append(binaryOp(value1, value2))
                    else:
                        newVals.append(binaryOp(value2, value1))
                    newProbs.append(prob1 * prob2)
        else:
            for i, prob, in enumerate(self.probs):
                newProbs.append(prob)
                if reversed:
                    newVals.append(binaryOp(other, self.values[i]))
                else:
                    newVals.append(binaryOp(self.values[i], other))

        return ProbVal(newProbs, newVals)

    def __str__(self):
        return "[" + ", ".join([f"({self.probs[i]} {self.values[i]})" for i in range(len(self.probs))]) + "]"

    # comparison
    def __eq__(self, other):
        return self.__comparison(other, operator.eq)

    def __ne__(self, other):
        return self.__comparison(other, operator.ne)

    def __gt__(self, other):
        return self.__comparison(other, operator.gt)

    def __lt__(self, other):
        return self.__comparison(other, operator.lt)

    def __ge__(self, other):
        return self.__comparison(other, operator.ge)

    def __le__(self, other):
        return self.__comparison(other, operator.le)


    # logical ops
    def __and__(self, other):
        return self.__comparison(other, operator.and_)

    def __rand__(self, other):
        return self.__and__(other)

    def __or__(self, other):
        return self.__comparison(other, operator.or_)

    def __ror__(self, other):
        return self.__or__(other)

    def __xor__(self, other):
        return self.__comparison(other, operator.xor)

    def __rxor__(self, other):
        return self.__xor__(other)


    # uniary
    def __not__(self):
        return self.__unary(operator.not_)

    def __abs__(self):
        return self.__unary(operator.abs)

    def __trunc__(self):
        return self.__unary(math.trunc)

    def __floor__(self):
        return self.__unary(math.floor)

    def __ceil__(self):
        return self.__unary(math.ceil)

    def __round__(self, ndigits = None):
        return self.__unary(round, ndigits)

    # does not work, requires boolean return type
    # def __bool__(self):
    #     return self == True

    def __neg__(self):
        return self.__unary(operator.neg)

    def __invert__(self):
        return self.__unary(operator.inv)

    def __pos__(self):
        return self.__unary(operator.pos)


    # binary ops
    def __add__(self, other, reversed = False):
        return self.__binary(other, operator.add, reversed)

    def __radd__(self, other):
        return self.__add__(other, reversed = True)

    def __sub__(self, other, reversed = False):
        return self.__binary(other, operator.sub, reversed)

    def __rsub__(self, other):
        return self.__sub__(other, reversed = True)

    def __mul__(self, other, reversed = False):
        return self.__binary(other, operator.mul, reversed)

    def __rmul__(self, other):
        return self.__mul__(other, reversed = True)

    def __truediv__(self, other, reversed = False):
        return self.__binary(other, operator.truediv, reversed)

    def __rtruediv__(self, other):
        return self.__truediv__(other, reversed = True)

    def __div__(self, other):
        return self.__truediv__(other)

    def __rdiv__(self, other):
        return self.__truediv__(other, reversed = True)

    def __mod__(self, other, reversed = False):
        return self.__binary(other, operator.mod, reversed)

    def __rmod__(self, other):
        return self.__mod__(other, reversed = True)

    def __floordiv__(self, other, reversed = False):
        return self.__binary(other, operator.floordiv, reversed)

    def __rfloordiv__(self, other):
        return self.__floordiv__(other, reversed = True)

    def __lshift__(self, other, reversed = False):
        return self.__binary(other, operator.lshift, reversed)

    def __rlshift__(self, other):
        return self.__lshift__(other, reversed = True)

    def __rshift__(self, other, reversed = False):
        return self.__binary(other, operator.rshift, reversed)

    def __rrshift__(self, other):
        return self.__rshift__(other, reversed = True)

    def __matmul__(self, other, reversed = False):
        return self.__binary(other, operator.matmul, reversed)

    def __rmatmul__(self, other):
        return self.__matmul__(other, reversed = True)
