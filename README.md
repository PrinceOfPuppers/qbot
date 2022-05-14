# qbot

> A domain-specific programming language for analyzing quantum algorithms using the quantum circuit model and probabilistic computing. Implemented in python with exclusively numpy. \
Paradigms: Quantum, Probabilistic, Imperative, Interpreted

## Contents
2. [OVERVIEW](#OVERVIEW)
    - [Probabilistic Computing](#Probabilistic-Computing)
    - [Quantum Circuit Model](#Quantum-Circuit-Model)
    - [USAGE](#USAGE)
    - [General Syntax](#General-Syntax)

3. [BUILTIN TYPES](#BUILTIN-TYPES)
    - [ProbVal](#ProbVal)
    - [Basis](#Basis)
    - [MeasurementResult](#MeasurementResult)

4. [TOOLS AND CONSTANTS](#TOOLS-AND-CONSTANTS)
    - [Gates](#Gates)
    - [States](#States)
    - [Combining Gates/States](#combining-gatesstates)
    - [numpy/math wrappers](#numpymath-wrappers)

5. [OPERATIONS](#OPERATIONS)
    - [Defines](#Defines)
    - [State Manipulation](#State-Manipulation)
    - [Measurement](#Measurement)
    - [Control Flow](#Control-Flow)
    - [Misc](#Misc)

6. [EXAMPLES](#EXAMPLES)
    - [Superdense Coding](#Superdense-Coding)
    - [Phase Kickback](#Phase-Kickback)
    - [The Deutsch Algorithm](#The-Deutsch-Algorithm)


&nbsp;
# OVERVIEW
qbot is a domain-specific programming language for analyzing quantum algorithms using the quantum circuit model and probabilistic computing. 

qbot uses a wrapped version of python's expression evaluation for its own expression evaluation, some examples of primitive/expression behaviour will be in python for this reason.

Terminology used throughout this document:
- `state` refers to the qubit register
- `targets` refers to qubits in `state` being affected by an operation (such as a unitary or measurement)

## Probabilistic Computing
Rather than using a random number generator to decide the outcome of a random processes (i.e. measurement), qbot stores the outcomes and associated probabilities in a special primitive called a [ProbVal](#ProbVal) which can be used in further computation. 

## Quantum Circuit Model
qbot has a register of qubits on which it applies unitary matrices, measurements, etc. On top of this, qbot contains a traditional namespace to be used in computation which comes pre-populated with many commonly needed unitaries, states, bases and operations. Anything missing can be created using the inbuilt [tools](#TOOLS-AND-CONSTANTS), or the exposed numpy functions, all of which are compatible with [ProbVals](#ProbVal).

## USAGE
### Installation
```
git clone https://github.com/PrinceOfPuppers/qbot
pip install -e .
```

### File Execution
```bash
$ qbot [FILE]
```
Where `[FILE]` is either a relative or absolute path, the canonical file extension is `.qb` however this is not nessisary for qbot to attempt to execute a file.


### Python Embedding
```python
from qbot import executeTxt, executeFile

qbScript = \
'''
cout "hello world!"
'''

executeTxt(qbScript)

filePath = 'path/to/test.qb'
with open(filePath, 'r') as f:
    executeFile(f)

```

## General Syntax
The syntax resembles an assembly language:
```
OPERATION arg1 ; arg2 ; ...
```
Where the arguments are valid python expressions separated by `;`. [operations](#OPERATIONS) may [act on state](#State-Manipulation), [measure the state](#Measurement), [define variables](#Defines) and [control flow](#Control-Flow), [among other functions](#Misc).


&nbsp;
# BUILTIN TYPES
List does not include standard python types or primitives.

## ProbVal
qbot allows for the creation of probabilistic values (ProbVals) which are in essence a classical superposition of multiple possible values. They behave very similarly to standard variables in python, for example:

``` python
# python example
x = ProbVal([0.5, 0.5], [1, 3])
y = 4
print(x + y) # prints ProbVal([0.5, 0.5], [5, 8])

print(x == 3) # prints ProbVal([0.5, 0.5], [False, True])
```
They are compatible with nearly all inbuilt python operators, qbot specific helper functions, and the provided numpy/math functions. ProbVals will auto normalize on instantiation.

**ProbVal Attributes:**
- `x.values - list<any>` \
List of values x could be
- `x.probs - list<float>` \
List of probabilities for each value

**ProbVal Methods:**
- `x.toDensity() -> np.ndarray` \
Return density matrix if all values are either kets (1d np.ndarray), or density matrices (2d np.ndarray)
- `x.map(lambdaFunc) -> ProbVal` \
Returns a ProbVal with all the values in `x` mapped to return of `lambdaFunc`
- `x.instance() -> any` \
Used for instance checking, i.e. `if isinstance(x.instance(), int)`, returns the first value from `x.values` if all values are of the same type, else returns `None`
- `x.typeString() -> string` \
Returns `ProbVal<[TYPE]>` if all values are of type `[TYPE]`, else returns `ProbVal<mixed>`
- `x.isEquivalent(y) -> bool` \
Returns `True` if `x` and y are completely interchangeable (contain all the same values with the same probabilities), else `False`

ProbVal also implements nearly all `python dunder methods`, which allows for its compatibility with python's operators and the like.


## Basis
qbot predefines `computation` `hadamard` `bell` bases to be used to state creation and measurement, bases are represented as `Basis` type and can be indexed to get specific basis states, and passed directly to the [measurement operator](#meas). Bases have several aliases for convenience i.e. `comp`, `hada`, etc.

```
note qbot example

note set x to |0〉
cdef x ; comp[0]

note set y to |010〉
cdef y ; tensorProd(comp[0], comp[1], comp[0])

note set z to |+〉
cdef y ; hada[0]
```

**Predefined bases aliases:**
- computation basis aliases: \
`comp`, `computation`, `computational`, `compBasis`, `computationBasis`, `computationalBasis`
- hadamard basis aliases: \
`hadamard`, `had`, `hada`, `hadamardBasis`, `hadBasis`, `hadaBasis`
- bell basis aliases: \
`bell`, `epr`, `bellBasis`, `eprBasis`


**Basis Attributes:**
- `x.names - list<string>` \
List of aliases
- `x.numQubits - int` \
Corresponds to the size of basis states
- `x.density - list<np.ndarray>` \
List of basis state density matrices
- `x.kets    - list<np.ndarray>` \
List of basis state kets

**Basis "Methods":**
- `x[i] -> np.ndarray` \
Returns a density matrix of the `i`th basis state (short form of `x.density[i]`)


## MeasurementResult
Returned by [measurement operator](#meas), contains information about a measurement. Can be directly printed out using [cout operator](#cout) for a clear readout of the results of a measurement. Also returned by [peek operator](#peek).


```
note qbot example

note set state to |0>, measure state to x, print x
qset computation[0]
meas x ; computation
cout x
```
This will print:
```
|0〉- 1.0 (100.0%)
|1〉- 0.0 (0.0%)
```

**MeasurementResult Attributes:**
- `x.probs - list<float>` \
List of probabilities for each state in the measurement basis
- `x.basisDensity - list<np.ndarray>` \
List of measurement basis states corresponding to `x.probs`
- `x.basisSymbols - list<string>` \
List symbols of each measurement basis kets (used in printout)
- `x.newState - np.ndarray` \
Density matrix of `state` after measurement (what state is assigned to)
- `x.unMeasuredDensity - np.ndarray` \
Density matrix partially traced target qubits before measurement, gets turned into `x.newState`


&nbsp;
# TOOLS AND CONSTANTS
**NOTE:** All listed functions are compatible with [ProbVal](#ProbVal) arguments so long as the [ProbVal](#ProbVal) values are of the correct type.

## Gates
- `identityGate - np.ndarray`
- `hadamardGate - np.ndarray`
- `pauliXGate - np.ndarray`
- `pauliYGate - np.ndarray`
- `pauliZGate - np.ndarray`
- `xRotGate - np.ndarray`
- `yRotGate - np.ndarray`
- `zRotGate - np.ndarray`
- `qftGate(numQubits: int) -> np.ndarray`
- `simonsGate(numQubits: int, f: Callable) -> np.ndarray` \
implements `U_f: |x〉|b〉 -> |x〉|b addmod2 f(x)〉`
- `swapGate(numQubits: int, qubitA: int, qubitB: int) -> np.ndarray` \
swaps `qubitA` and `qubitB`
- `shiftGate(numQubits: int, up:bool = True) -> np.ndarray` \
shifts all qubits up or down

## States
- Computational Basis States
- Hadamard Basis States
- Bell (EPR) Basis States

For more information about how these are represented/applied see [Basis](#Basis).

## Combining Gates/States
qbot contains the following helpers implementing tensor/kroneker product:
- `tensorProd(*args: np.ndarray) -> np.ndarray` \
takes the tensor product of a variable number of `np.ndarrays`
- `tensorExp(arg: np.ndarray, n:int) -> np.ndarray` \
tensor exponent ie) `tensorExp(hadamardGate, 2) == tensorProd(hadamardGate, hadamardGate)`
- `tensorPermute(numTensProd: int, n: int, densities: Basis or list<np.ndarray>) -> np.ndarray` \ 
returns the `n`th permutation of of `numTensProd` states in `densities` ie) `tensorPermute(3, 2, comp) == tensorProd(comp[0], comp[1], comp[0])`

## numpy/math wrappers

qbot exposes nearly all numpy, numpy.linalg and builtin python math functions and wraps them to be compatible with [ProbVal](#ProbVal). numpy functions are prefixed with `np_*`, linalg with `linalg_*` and math functions with `math_*`.

**Examples:**

- `math_cos`
- `math_pi`
- `np_array`
- `linalg_solve`
- etc...

For a full list please see `qbot/evaluation.py`.


&nbsp;
# OPERATIONS

**Quick format info:**
```
operator [arg1] ; [arg2] ; [optionalArg3?] ; ...

[arg1]           - type
[arg2]           - typeA, orTypeB, ...
[optionalArg3?]  - typeA, orTypeB, ... (optional)
```

As a reminder, the qubit register will be referred to as `state`, `target`/`targets` refers to target qubits in `state`.


## Defines
### cdef
```
cdef [identifier] ; [value]

[identifier] - identifier
[value]      - any
```

Adds `[value]` to the namespace under name `[identifier]`.

Operator name stands for "classical define".

**example:**
```
cdef x ; 1234
cdef y ; ProbVal([0.25, 0.75], ["hello", "there"])
```

### qdef
```
qdef [identifier] ; [valueExpr]

[identifier] - identifier
[value]      - np.ndarray, ProbVal<np.ndarray>
```
Adds `[value]` to the namespace under name `[identifier]`. `[value]` type must be `np.ndarray` or  `ProbVal<np.ndarray>`, kets and ProbVals are converted into density matrices.

Operator name stands for "quantum define".

**example:**
```
qdef x ; tensorProd(computation[0], computation[1])
qdef y ; ProbVal([0.25, 0.75], [hadamard[0], bell[1]])
```


## State Manipulation

### qset
```
qset [newState] ; [targets?]

[newState] - np.ndarray, ProbVal<np.ndarray>
[targets?] - int, list<int>, ProbVal<int>, ProbVal<list<int>> (optional)
```

Sets `[targets?]` qubits in `state` to `[newState]`, if `[targets?]` are not provided, discards current register and sets it to `[newState]`.

Operator name stands for "quantum set".

### gate
```
gate [gate] ; [targets?] ; [controls?] ; [conditional?]

[gate]         - np.ndarray, ProbVal<np.ndarray>
[targets?]     - int, list<int>, ProbVal<int>, ProbVal<list<int>> (optional)
[controls?]    - int, list<int>, ProbVal<int>, ProbVal<list<int>> (optional)
[conditional?] - bool, ProbVal<bool>
```

Applies unitary `gate` to `[targets?]` qubits in state with `[controls?]`. `gate` application can also be controlled by a classical condition using `[conditional?]`.

### disc
```
disc [targets]

[targets] - int, list<int>, ProbVal<int>, ProbVal<list<int>>
```

Traces out `[targets]` from `state`.

Operator name stands for "discard".

### swap
```
swap [targetA] ; [targetB]

[targetA] - int, ProbVal<int>
[targetB] - int, ProbVal<int>
```

Swaps `[targetA]` and `[targetB]` in `state`, equivalent to `gate swapGate(numQubits, targetA, targetB)` where `numQubits` is the number of qubits in `state`.

## Measurement

### meas
```
meas [identifer] ; [basis] ; [targets?]

[identifier] - identifier
[basis]      - Basis
[targets?]   - int, list<int>, ProbVal<int>, ProbVal<list<int>> (optional)
```

Measures `[targets?]` of `state` with respect to `[basis]` and sets `[identifer]` to the result. `[targets?]` in `state` are collapsed to an ensemble of measurement basis states.

Operator name stands for "measurement".

### peek
```
peek [identifer] ; [basis] ; [targets?]

[identifier] - identifier
[basis]      - Basis
[targets?]   - int, list<int>, ProbVal<int>, ProbVal<list<int>> (optional)
```

Similar to [meas](#meas), `peek` measures `[targets?]` of `state` with respect to `[basis]` and sets `[identifer]` to the result, however `state` remains completely unaffected.


## Control Flow

### mark
```
mark [identifer]

[identifier] - identifier
```

Marks a line with `[identifier]` to later be jumped to with [jump](#jump) or [cjmp](#cjmp).

### jump
```
jump [identifer]

[identifier] - identifier
```

Jumps to `mark [identifier]`.

### cjmp
```
cjmp [identifer] ; [condition]

[identifier] - identifier
[condition]  - bool
```

Jumps to `mark [identifier]` if `[condition]` is true.

### retr
```
retr [condition?]

[condition?]  - bool (optional)
```

Returns (jumps) to line after most recent [jump](#jump)/[cjmp](#cjmp) statement if `[condition?]` is true, if there is no `[condition?]` always jumps. If there was no prior jump statement, returns to start of script.

operator name stands for "return".

### halt
```
halt [condition?]

[condition?]  - bool (optional)
```

Halts execution if `[condition?]` is true, if there is no `[condition?]` always halts.


## Misc

### pydo
```
pydo [expr]

[expr]  - any
```

Evaluates expression `[expr]` and ignores what it evaluates to, identical to using `cdef x ; [expr]` but without variable assignment.

Operator name stands for "python do".

**example:**
```
cdef x ; ["hello"]
pydo x.append("there")
```

### cout
```
cout [toPrint]

[toPrint] - any
```

Evaluates `[toPrint]` and prints it.

Operator name stands for "console out".


&nbsp;
# EXAMPLES

## Superdense Coding

This algorithm tests all 4 permutations of 2 classical bits that can be transmitted by 1 qubit under superdense coding. It stores the results of the bell measurement in the results list (used in qbot's unit testing).
```
cdef results ; []
cdef index ; 0

mark loop
qset bell[0]
gate pauliXGate ; 0 ; [] ; (index & 0b01) != 0
gate pauliZGate ; 0 ; [] ; (index & 0b10) != 0
meas result ; bell
pydo results.append(result.probs)
cdef index ; index + 1
cjmp loop ; index < 4

```

## Phase Kickback

Reads out list of eigan values `[1, -1]` of the c-not gate associated with eigan vectors `|+〉` (hadamard plus) and `|-〉` (hadamard minus).
```
cdef results ; []

note eiganValue is 1
qset tensorProd(comp[0], hada[0])
jump checkPhase

note eiganValue is -1
qset tensorProd(comp[0], hada[1])
jump checkPhase

cout results
halt

mark checkPhase
gate hadamardGate ; 0
gate pauliXGate   ; 1 ; 0
gate hadamardGate ; 0
meas tmp ; comp ; 0
pydo results.append(1 if np_isclose(tmp[0], 1.0) else -1)
retr
```


## The Deutsch Algorithm
Determines if lambda function is balanced or constant using a single call to a gate derived from it. Tested with a constant lambda function, then a balanced one.

```
cdef results ; []

note constant f (should return |0〉)
cdef f ; lambda x: 1
jump check

note balanced f (should return |1〉)
cdef f ; lambda x: x
jump check

halt

mark check
qset tensorProd(comp[0], hada[1])
gate hadamardGate ; 0
gate simonsGate(2, f)
gate hadamardGate ; 0
meas tmp ; comp ; 0
pydo results.append("constant" if np_isclose(tmp.probs[0], 1.0) else "balanced")
retr
```
