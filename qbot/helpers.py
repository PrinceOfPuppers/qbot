import numpy as np
from math import sqrt, frexp
from fractions import Fraction

def printBits(x, numBits):
    fmt = f'0{numBits}b'
    print(format(x, fmt))
    
def log2(x):
    return frexp(x)[1] - 1

def nthRootsOfUnity(n):
    return np.exp(2j * np.pi / n * np.arange(n))

def boundsOverlap(min1, max1, min2, max2):
    if max1 < min1 or max2 < min2:
        raise Exception(f"Improper Bounds: min1 {min1}, max1 {max1}, min2 {min2}, max2 {max2}")
    Min = min(min1, min2)
    Max = max(max1, max2)
    return (max1 - min1) + (max2 - min2) >= Max - Min

def ensureSquare(array: np.ndarray):
    '''
    Throws Error if not square array
    '''
    if(array.ndim!=2):
        raise Exception("array must be 2 dimensional")
    shape = array.shape
    
    if(shape[0]!=shape[1]):
        raise Exception("array must be square")
    
    return shape[0]


def ensureVec(array: np.ndarray):
    if(array.ndim!=1):
        raise Exception("array must be 1 dimensional")
    return array.shape[0]

# following function is from source:
# http://www.johndcook.com/blog/2010/10/20/best-rational-approximation/?utm_source=feedburner&utm_medium=feed&utm_campaign=Feed%3A+TheEndeavour+%28The+Endeavour%29
def farey(x, N):
    a, b = 0, 1
    c, d = 1, 1
    while (b <= N and d <= N):
        mediant = float(a+c)/(b+d)
        if x == mediant:
            if b + d <= N:
                return a+c, b+d
            elif d > b:
                return c, d
            else:
                return a, b
        elif x > mediant:
            a, b = a+c, b+d
        else:
            c, d = a+c, b+d

    if (b > N):
        return c, d
    else:
        return a, b

def bestRationalApprox(x,maxDenom):
    leading = int(x // 1)
    x -= leading
    numerator,denominator = farey(x,maxDenom)
    numerator += leading*denominator
    return numerator,denominator


def close(x,y,tolerance):
    return abs(x-y) < tolerance

maxDenom = 50
tolerance = 1e-6
vals    = [sqrt(2), sqrt(3), sqrt(5), np.pi, np.e, sqrt(np.pi), sqrt(2*np.pi)]
symbols = ['√2','√3','√5','π','e','√π','√2√π']
  
def floatToAlgebra(f:float,addToNumerator = ''):

    nume,denom = bestRationalApprox(f,maxDenom)
    
    if close(f,nume/denom,tolerance):
        result = str(nume)+addToNumerator
        if denom!=1:
            result+=f'/{denom}'
        return result
    
    #val in numerator
    for i,val in enumerate(vals):
        coeff = f/val
        nume,denom = bestRationalApprox(coeff,maxDenom)
        if close(coeff,nume/denom,tolerance):
            result = f'{nume if nume != 1 else ""}{symbols[i]}{addToNumerator}'
            if denom!=1:
                result+=f'/{denom}'
            return result
    
    #val in denominator
    for i,val in enumerate(vals):
        coeff = val*f
        nume,denom = bestRationalApprox(coeff,maxDenom)
        if close(coeff,nume/denom,tolerance):
            if denom!=1:
                return f'{nume}{addToNumerator}/{denom}{symbols[i]}'
            else:
                return f'{nume}{addToNumerator}/{symbols[i]}'
        
    return str(round(f,tolerance)) + addToNumerator


def complexToAlgebra(c:complex):
    real = floatToAlgebra(c.real)
    imag = floatToAlgebra(c.imag,'j')
    
    if imag == '0j':
        return real
    elif real == '0':
        return imag
    else:
        return f'({real} + {imag})'



def stateVecStr(state:np.ndarray):
    size = ensureVec(state)
    result = f'{complexToAlgebra(state[0])} |{format(0,f"0{size-1}b")}〉'
    for i in range(1,size):
        ele = state[i]
        ket = f' + {complexToAlgebra(ele)} |{format(i,f"0{size-1}b")}〉'
        result += ket
    return result
        

if __name__ == "__main__":
    print(boundsOverlap(4,5,4,4))
