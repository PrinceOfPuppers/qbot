# qbot
<p>
<img src="https://img.shields.io/pypi/dm/qbot">
<img src="https://img.shields.io/pypi/l/qbot">
<img src="https://img.shields.io/pypi/v/qbot">
<img src="https://img.shields.io/badge/python-%E2%89%A53.6-blue">
</p>

> A domain-specific programming language for analysing quamtum algorithms using the quantum circuit model and probabilistic computing.
Paradigms: Quantum, Probabilistic, Imperative, Interpreted

1. [OVERVIEW](#OVERVIEW)
    - [Probabilistic Computing](##Probabilistic)
    - [Quantum Circuit Model](##Probabilistic)
    - [General Syntax](##General Syntax)

2. [OPERATIONS](#OPERATIONS)
    - [Defines](##Defines)
    - [State Manipulation](##State Manipulation)
    - [Measuring](##Measuring)
    - [Control Flow](##Control Flow)
    - [Misc](##Misc)

3. [TOOLS](#TOOLS)
4. [EXAMPLE](#EXAMPLE)
5. [DEVLOPMENT](#DEVLOPMENT)





# OVERVIEW
qbot is a domain-specific programming language for analysing quamtum algorithms using the quantum circuit model and probabilistic computing. 

qbot uses a wrapped version of python's expression evalutaion for its own expression evaluation, some examples of primitive/expression behavior will be in python for this reason.



## Probabilistic Computing
Rather than using a random number generator to decide the outcome of a random processes (ie measurement), qbot stores the outcomes and associeated probabilites in a special primitive called a [ProbVal](###ProbVal) which can be used in futher computation. 

### ProbVal
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


ProbVal also implements nearly all python dunder methods, which allows for its compatibility with python's operators and the like.



## Quantum Circuit Model
Qbot has a register of qubits on which it applies unitary matrices, measurements and etc. On top of this qbot contains a traditional namespace to be used in computation, which comes pre-populated with many commonly needed unitaries, states, bases and operations. Anything missing can be created using the inbuilt [TOOLS](#TOOLS), or the exposed numpy functions, all of which are compatible with [ProbVals](###ProbVal).



## General Syntax
The syntax resembles an assembly language:
```
OPERATION arg1 ; arg2 ; ...
```
where the arguments are valid python expressions seperated by `;`. [OPERATIONS](#OPERATIONS) may [act on the qubit register](##State Manipulation), [measure the qubit register](##Measurement), [define variables](##Defines), [control the flow](##Control Flow), [among other functions](##Misc).




# OPERATIONS

## Defines
### cdef
```
cdef [identifier] ; [value]
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
qdef [identifier] ; [value]
```
adds `[value]` to the namespace under name `[identifier]`. `[value]` type must be `np.ndarray` or  `ProbVal<np.ndarray>`, where `ProbVal<np.ndarray>` both kets and ProbVals are converted into density matrices

operator name sands for "quantum define"

example:
```
qdef x ; tensorProd(computation[0], computation[1])
qdef y ; ProbVal([0.25, 0.75], [hadamard[0], bell[1]])
```



## State Manipulation
## Measuring
## Control Flow
## Misc
