# qbot

> A domain-specific programming language for analysing quamtum algorithms using the quantum circuit model and probabilistic computing.
Paradigms: Quantum, Probabilistic, Imperative, Interpreted

1. [OVERVIEW](#OVERVIEW)
    - [Probabilistic Computing](##Probabilistic)
    - [Quantum Circuit Model](##Probabilistic)
    - [General Syntax](##General Syntax)

2. [BUILTIN TYPES](#BUILTIN TYPES)
    - [ProbVal](##ProbVal)

3. [OPERATIONS](#OPERATIONS)
    - [Defines](##Defines)
    - [State Manipulation](##State Manipulation)
    - [Measuring](##Measuring)
    - [Control Flow](##Control Flow)
    - [Misc](##Misc)

4. [TOOLS](#TOOLS)
5. [EXAMPLE](#EXAMPLE)



# OVERVIEW
qbot is a domain-specific programming language for analysing quamtum algorithms using the quantum circuit model and probabilistic computing. 

qbot uses a wrapped version of python's expression evalutaion for its own expression evaluation, some examples of primitive/expression behavior will be in python for this reason.

## Probabilistic Computing
Rather than using a random number generator to decide the outcome of a random processes (ie measurement), qbot stores the outcomes and associeated probabilites in a special primitive called a [ProbVal](###ProbVal) which can be used in futher computation. 

## Quantum Circuit Model
Qbot has a register of qubits on which it applies unitary matrices, measurements and etc. On top of this qbot contains a traditional namespace to be used in computation, which comes pre-populated with many commonly needed unitaries, states, bases and operations. Anything missing can be created using the inbuilt [TOOLS](#TOOLS), or the exposed numpy functions, all of which are compatible with [ProbVals](###ProbVal).

## General Syntax
The syntax resembles an assembly language:
```
OPERATION arg1 ; arg2 ; ...
```
where the arguments are valid python expressions seperated by `;`. [OPERATIONS](#OPERATIONS) may [act on the qubit register](##State Manipulation), [measure the qubit register](##Measurement), [define variables](##Defines), [control the flow](##Control Flow), [among other functions](##Misc).



# BUILTIN TYPES
List does not include standard python primitives

## ProbVal
qbot allows for the creation of probabilistic values (Probval's) which are in essense a classical superposisiton of multiple possible values. They behave very similary to standard variables in python, for example:

``` python
# python example
x = ProbVal([0.5, 0.5], [1, 3])
y = 4
print(x + y) # prints ProbVal([0.5, 0.5], [5, 8])

print(x == 3) # prints ProbVal([0.5, 0.5], [False, True])
```
They are compatible with nearly all inbuilt python operators, qbot specific helper functions, and the provided numpy/math functions. ProbVals will auto normalize on instanceation

ProbVal Attributes:
- `x.values` list of values x could be
- `x.probs` list of probabilites for each value

ProbVal Methods:
- `x.toDensity()`           return density matrix if all values are either kets (1d np.ndarray), or density matrices (2d np.ndarray)
- `x.map(lambdaFunc)`       returns a ProbVal with all the values in `x` mapped to return of `lambdaFunc`
- `x.instance()`            used for instance checking, ie `if isinstance(x.instance(), int)`, returns the first value from `x.values` if all values are of the same type, else return `None`
- `x.typeString()`          returns `ProbVal<[TYPE]>` if all values are of type `[TYPE]`, else returns `ProbVal<mixed>`
- `x.isEquivalent(y)`       returns `True` if `x` and y are completly interchangable (contain all the same values with the same probabilities), else `False`


ProbVal also implements nearly all `python dunder methods`, which allows for its compatibility with python's operators and the like.


## Basis
qbot predefines `computation` `hadamard` `bell` bases to be used to state creation and measurement, bases are represented as `Basis` type and can be indexed to get specific basis states, and passed directly to the [measurment operator](### meas). bases have several aliases for convience


```
note qbot example

note set x to |0>
cdef x ; computation[0]

note set y to |010>
cdef y ; tensorProd(comp[0], comp[1], comp[0])

note set z to |+>
cdef y ; hada[0]
```

Predefined bases aliases:

- computation basis aliases: `comp`, `computation`, `computational`, `compBasis`, `computationBasis`, `computationalBasis`
- hadamard basis aliases:    `hadamard`, `had`, `hada`, `hadamardBasis`, `hadBasis`, `hadaBasis`
- bell basis aliases:        `bell`, `epr`, `bellBasis`, `eprBasis`


Basis Attributes:
- `x.names`     `list<string>` of aliases
- `x.numQubits` `int` corrisponding to size of basis states
- `x.density`   `list<np.ndarray>` basis state density matrices
- `x.kets`      `list<np.ndarray>` basis state kets

Basis "Methods":
- `x[i]`  returns `np.ndarray` density matrix of ith basis state (short form of x.density[i])


## MeasurementResult
Returned by [measurement operator](###meas), contains information about a measurment. can be directly printed out using [cout operator](###cout) for clear readout of the results of a measurement. Also returned by [peek operator](###peek).


```
note qbot example

note set state to |0>, measure state to x, print x
qset computation[0]
meas x ; computation
cout x
```
this will print:
```
|0〉- 1.0 (100.0%)
|1〉- 0.0 (0.0%)
```

MeasurementResult Attributes:
- `x.probs`             `list<float>`      list of probabilites for each state in the measurment basis
- `x.basisDensity`      `list<np.ndarray>` list of measurement basis states corrisponding to `x.probs`
- `x.basisSymbols`      `list<string>`     list of measurement basis state ket representations (used in printout)
- `x.newState`          `np.ndarray`       density matrix of `state` after measurement (what state is assigned to)
- `x.unMeasuredDensity` `np.ndarray`       density matrix partially traced target qubits before measurement, gets turned into `x.newState`



# OPERATIONS

Quick info format:
```
operator [arg1] ; [arg2] ; [optionalArg3?] ; ...

[arg1]           - type
[arg2]           - typeA, orTypeB, ...
[optionalArg3?]  - typeA, orTypeB, ... (optional)
```

the qubit register will be referred to as `state`, `target`/`targets` refers to target qubits in `state`


## Defines
### cdef
```
cdef [identifier] ; [value]

[identifier] - identifier
[value]      - any
```

adds `[value]` to the namespace under name `[identifier]`. 

Operator name stands for "classical define"

example:
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
adds `[value]` to the namespace under name `[identifier]`. `[value]` type must be `np.ndarray` or  `ProbVal<np.ndarray>`, kets and ProbVals are converted into density matrices

operator name stands for "quantum define"

example:
```
qdef x ; tensorProd(computation[0], computation[1])
qdef y ; ProbVal([0.25, 0.75], [hadamard[0], bell[1]])
```


## State Manipulation

### qset
```
qset ; [newState] ; [targets?]

[newState] - np.ndarray, ProbVal<np.ndarray>
[targets?] - int, list<int>, ProbVal<int>, ProbVal<list<int>> (optional)
```

sets `[targets?]` qubits in `state` to `[newState]`, if `[targets?]` are not provided, discards current register and sets it to `[newState]`

operator name stands for "quantum set"

### gate
```
gate ; [gate] ; [targets?] ; [controls?] ; [conditional?]

[gate]         - np.ndarray, ProbVal<np.ndarray>
[targets?]     - int, list<int>, ProbVal<int>, ProbVal<list<int>> (optional)
[controls?]    - int, list<int>, ProbVal<int>, ProbVal<list<int>> (optional)
[conditional?] - bool, ProbVal<bool>
```

applies unitary `gate` to `[targets?]` qubits in state with `[controls?]`. `gate` application can also be controlled by a classical condition using `[conditional?]`

### disc
```
disc ; [targets]

[targets] - int, list<int>, ProbVal<int>, ProbVal<list<int>>
```

traces out `[targets]` from `state`

operator name stands for "discard"

### swap
```
swap ; [targetA] ; [targetB]

[targetA] - int, ProbVal<int>
[targetB] - int, ProbVal<int>
```

swaps `[targetA]` and `[targetB]` in `state`, equivalent to `gate swapGate(numQubits, targetA, targetB)` where `numQubits` is the number of qubits in `state`

## Measuring

### meas
```
meas ; [identifer] ; [basis] ; [targets?]

[identifier] - identifier
[basis]      - Basis
[targets?]   - int, list<int>, ProbVal<int>, ProbVal<list<int>> (optional)
```

measures `[targets?]` of `state` with respect to `[basis]` and sets `[identifer]` to the result. 

operator name stands for "measurement"

    'meas': (meas, 2, 3),
    'peek': (peek, 2, 3),

## Control Flow
## Misc
