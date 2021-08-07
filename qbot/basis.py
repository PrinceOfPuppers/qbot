import numpy as np
from qbot.density import ketsToDensity

class Basis:
    __slots__ = (
        'name',
        'density',
        'kets',
        'symbols'
    )
    def __init__(self,name,kets,symbols):
        if len(symbols) != len(kets):
            raise Exception("basis must have same number of symbols and kets")
        self.name = name
        self.kets = kets
        self.symbols = symbols
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
    [ "|0〉", "|1〉" ]
)

oneOverRoot2 = 2**(-1/2)

hadamard = Basis(
    'hadamard', 
    [
        oneOverRoot2*np.array([1,1] ,dtype=complex),
        oneOverRoot2*np.array([1,-1],dtype=complex)
    ],
    [ "|+〉", "|-〉" ]
)

bell = Basis(
    'bell',
    [
        oneOverRoot2*np.array([1,0,0,1] ,dtype=complex),
        oneOverRoot2*np.array([1,0,0,-1],dtype=complex),
        oneOverRoot2*np.array([0,1,1,0] ,dtype=complex),
        oneOverRoot2*np.array([0,1,-1,0],dtype=complex),
    ],
    [ "|Φ⁺〉", "|Φ⁻〉", "|Ψ⁺〉", "|Ψ⁻〉" ]
)
allBasis = [computation, hadamard]