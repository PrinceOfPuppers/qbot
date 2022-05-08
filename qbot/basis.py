import numpy as np
from qbot.density import ketsToDensity
from qbot.helpers import log2

class Basis:
    __slots__ = (
        'names',
        'density',
        'kets',
        'numQubits',
        'ketSymbols',
        'gateSymbol' # used for circuit representation of measurement
    )
    def __init__(self, names, kets, ketSymbols, gateSymbol):
        if len(ketSymbols) != len(kets):
            raise Exception("basis must have same number of ketSymbols and kets")
        self.names = names
        self.kets = kets
        self.numQubits = log2(kets[0].shape[0])
        self.ketSymbols = ketSymbols
        self.gateSymbol = gateSymbol
        self.density = []
        for ket in kets:
            self.density.append(
                ketsToDensity([ket])
            )
    def __getitem__(self, i):
        return self.density[i]

computation = Basis(
    ['comp', 'computation', 'computational', 'compBasis', 'computationBasis', 'computationalBasis'],
    [
        np.array([1,0], dtype = complex),
        np.array([0,1], dtype = complex),
    ],
    [ "|0〉", "|1〉" ],
    '∡'
)

#computation2D = Basis(
#    'computation2D', 
#    [
#        np.array([1,0,0,0], dtype = complex),
#        np.array([0,1,0,0], dtype = complex),
#        np.array([0,0,1,0], dtype = complex),
#        np.array([0,0,0,1], dtype = complex),
#    ],
#    [ "|00〉", "|01〉", "|10〉", "|11〉" ],
#    '∡ 2D'
#)

oneOverRoot2 = 2**(-1/2)

hadamard = Basis(
    ['hadamard', 'had', 'hada', 'hadamardBasis', 'hadBasis', 'hadaBasis'],
    [
        oneOverRoot2*np.array([1,1] ,dtype=complex),
        oneOverRoot2*np.array([1,-1],dtype=complex)
    ],
    [ "|+〉", "|-〉" ],
    '∡ ±'
)

bell = Basis(
    ['bell', 'epr', 'bellBasis', 'eprBasis'],
    [
        oneOverRoot2*np.array([1,0,0,1] ,dtype=complex),
        oneOverRoot2*np.array([0,1,1,0] ,dtype=complex),
        oneOverRoot2*np.array([1,0,0,-1],dtype=complex),
        oneOverRoot2*np.array([0,1,-1,0],dtype=complex),
    ],
    [ "|β₀₀〉", "|β₀₁〉", "|β₁₀〉", "|β₁₁〉" ],
    '∡ β'
)

allBasis = [computation, hadamard, bell]

