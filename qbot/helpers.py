import numpy as np
from math import sqrt
from fractions import Fraction

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


def ensureVec(array: np.array):
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
symbols = ['√2','√3','√5','π','e','√π','√2π']
  
def floatToAlgebra(f:float):

    nume,denom = bestRationalApprox(f,maxDenom)
    
    if close(f,nume/denom,tolerance):
        result = str(nume)
        if denom!=1:
            result+=f'/{denom}'
        return result
    
    #val in numerator
    for i,val in enumerate(vals):
        coeff = f/val
        nume,denom = bestRationalApprox(coeff,maxDenom)
        if close(coeff,nume/denom,tolerance):
            result = f'{nume if nume != 1 else ""}{symbols[i]}'
            if denom!=1:
                result+=f'/{denom}'
            return result
    
    #val in denominator
    for i,val in enumerate(vals):
        coeff = val*f
        nume,denom = bestRationalApprox(coeff,maxDenom)
        if close(coeff,nume/denom,tolerance):
            if denom!=1:
                return f'{nume}/{denom}{symbols[i]}'
            else:
                return f'{nume}/{symbols[i]}'
        
    return str(f)


def complexToAlgebra(c:complex):
    return floatToAlgebra(c.real) + ' + (' + floatToAlgebra(c.imag) + ')j'


#def stateVecStr(state:np.array):
#    size = ensureVec(state)
#
#    for i,ele in enumerate(state):
#        

if __name__ == "__main__":
    print(len(symbols),len(vals))
    for i in range(0,10):
        print(complexToAlgebra( (1/3)/(sqrt(2*3.1415926535)*5)+ 8j*np.e/43)  )