import numpy as np
from qbot.density import ketsToDensity
from qbot.helpers import log2

class Basis:
    __slots__ = (
        'name',
        'density',
        'kets',
        'numQubits',
        'ketSymbols',
        'gateSymbol' # used for circuit representation of measurement
    )
    def __init__(self, name, kets, ketSymbols, gateSymbol):
        if len(ketSymbols) != len(kets):
            raise Exception("basis must have same number of ketSymbols and kets")
        self.name = name
        self.kets = kets
        self.numQubits = log2(kets[0].shape[0])
        self.ketSymbols = ketSymbols
        self.gateSymbol = gateSymbol
        self.density = []
        for ket in kets:
            self.density.append(
                ketsToDensity([ket])
            )

computation = Basis(
    'computation', 
    [
        np.array([1,0], dtype = complex),
        np.array([0,1], dtype = complex),
    ],
    [ "|0〉", "|1〉" ],
    '∡'
)

computation2D = Basis(
    'computation2D', 
    [
        np.array([1,0,0,0], dtype = complex),
        np.array([0,1,0,0], dtype = complex),
        np.array([0,0,1,0], dtype = complex),
        np.array([0,0,0,1], dtype = complex),
    ],
    [ "|00〉", "|01〉", "|10〉", "|11〉" ],
    '∡ 2D'
)

oneOverRoot2 = 2**(-1/2)

hadamard = Basis(
    'hadamard', 
    [
        oneOverRoot2*np.array([1,1] ,dtype=complex),
        oneOverRoot2*np.array([1,-1],dtype=complex)
    ],
    [ "|+〉", "|-〉" ],
    '∡ ±'
)

bell = Basis(
    'bell',
    [
        oneOverRoot2*np.array([1,0,0,1] ,dtype=complex),
        oneOverRoot2*np.array([0,1,1,0] ,dtype=complex),
        oneOverRoot2*np.array([1,0,0,-1],dtype=complex),
        oneOverRoot2*np.array([0,1,-1,0],dtype=complex),
    ],
    [ "|β₀₀〉", "|β₀₁〉", "|β₁₀〉", "|β₁₁〉" ],
    '∡ β'
)
# corrisponds to lables on measurement circuit elements
basisDict = {
    computation.gateSymbol: computation,
    hadamard.gateSymbol: hadamard,
    bell.gateSymbol: bell,
}