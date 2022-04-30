def measureTopNQubits(density: np.ndarray, basisDensity: list[np.ndarray], N: int) -> MeasurementResult:
    '''
    Measures the top N Qubits with respect to the provided basis (must also be density matrices)
    '''
    numQubits = log2(ensureSquare(density))

    if (numQubits == N):
        toMeasureDensity = density
        unMeasuredDensity = np.array([],dtype=complex)
    else:
        toMeasureDensity, unMeasuredDensity = partialTraceBoth(density, N, numQubits - N)
    
    probs = []
    s = 0

    for b in basisDensity:
        probs.append(
            abs(np.trace(np.matmul(toMeasureDensity, b)))
        )
        s += probs[-1]

    for i in range(0,len(probs)):
        probs[i] /= s
    
    return MeasurementResult(unMeasuredDensity,toMeasureDensity,probs)

def measureArbitrary(density: np.ndarray, basisDensity: List[np.ndarray], toMeasure: List[int]) -> MeasurementResult:
    '''
    Measures all qubits in toMeasure
    '''
    numQubits = log2(ensureSquare(density))

    if len(toMeasure) == numQubits:
        toMeasureDensity = density
        unMeasuredDensity = np.array([],dtype=complex)
    else:
        toMeasureDensity, unMeasuredDensity = partialTraceArbitrary(density, numQubits, toMeasure)
    
    probs = []
    s = 0

    for b in basisDensity:
        probs.append(
            abs(np.trace(np.matmul(toMeasureDensity, b)))
        )
        s += probs[-1]

    for i in range(0,len(probs)):
        probs[i] /= s
    
    return MeasurementResult(unMeasuredDensity,toMeasureDensity,probs)
