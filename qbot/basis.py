import numpy as np
from qbot.density import ketsToDensity

class Basis:
    __slots__ = (
        'name',
        'density',
        'kets',
        'numQubits',
        'ketSymbols',
        'gateSymbol'
    )
    def __init__(self, name, kets, ketSymbols, gateSymbol):
        if len(ketSymbols) != len(kets):
            raise Exception("basis must have same number of ketSymbols and kets")
        self.name = name
        self.kets = kets
        self.numQubits = kets[0].shape[0]
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
    ' '
)

oneOverRoot2 = 2**(-1/2)

hadamard = Basis(
    'hadamard', 
    [
        oneOverRoot2*np.array([1,1] ,dtype=complex),
        oneOverRoot2*np.array([1,-1],dtype=complex)
    ],
    [ "|+〉", "|-〉" ],
    'H'
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
    'BELL'
)
# corrisponds to lables on measurement circuit elements
basisDict = {
    computation.gateSymbol: computation,
    hadamard.gateSymbol: hadamard,
    bell.gateSymbol: bell,
}