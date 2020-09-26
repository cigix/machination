# Machination
## A Turing machine description language, parser, and runtime

## Syntax

The Turing machine is described with a dictionary structure. This could be a
JSON object, or an equivalent Python `dict`. The fields of the root object
each name a state or state-template. The state named `"start"` is the initial
state of the execution, while any state featuring a `0` [direction](#direction)
is a final state.

### Symbol

A symbol is either:
* a one character string
* `"NUL"` (see [alphabet](#Alphabet))
* `"EOT"` (see [alphabet](#Alphabet))
* special strings depending on the context

### Direction

A direction is either:
* `"left"` or `-1`
* `"right"` or `1`
* `0` for a final state

### Rule

A rule is an array with three fields:
0. a [symbol](#symbol) to write
1. a [direction](#direction) to shift to
2. the name of a state or state-template to go to

In a rule, having the string `"SAME"` as the symbol means "write the same
symbol than the one matched by the rule", essentially a noop tape-wise, while
having the string `"SAME"` as the state means "go to the same state as the
current one", essentially a noop state-wise.

### State

A state is an object where each field is a named [rule](#rule), named after the
[symbol](#symbol) to match.

In a state, having the string `"ELSE"` as the name of a rule means "duplicate
this rule for every symbol not explicitely mentionned". 

### State-template

A state-template is a generic way to define similar states for information
storage. A state-template is identified by terminating it with a `.`. Every
instanciation of the state-template will be a state with a similar name, except
with the final `.` replaced with the instanciation symbol.

#### State Rule leading to a state-template

In the rule of a regular state, the final dot of the state-template is replaced
with the matched symbol. For an `"ELSE"` match, there will be one state-template
instanciation for every matched symbol.

#### State-template rule

In a state-template, the string `"DOT"` where a symbol is expected (either in
the name of a rule or as the write symbol of a rule) will be replaced with the
instanciation symbol.

#### State-template rule leading to a state-template

In the rule of a state-template, the final dot of the state template is replaced
with the instanciation symbol. This means that you can chain templates while
retaining the same instanciation symbol.

## Alphabet

The alphabet is given as input to the parser. On top of the given characters,
two special symbols are injected in the alphabet:
* `"NUL"` which symbolizes a empty space
* `"EOT"` which symbolizes the end of the tape

## Tooling

`mtparser.py` is a Python module that flattens the above description language.
You can use it to turn a high level description of the Turing machine into a set
of low level rules.

`mtoutput.py` is a Python module that turns the rules built by `mtparser.py`
into text. There are 3 output drivers:
* for humans
* for mathematicians
* for C compilers

`machination` is a frontend for the two modules above. It parses a JSON file
describing a Turing machine, and rewrites it as plain rules. It can output the
Turing machine as a C array into a header file.

`mtruntime.c` is a runtime for a rule array as output by `machination`. You can
use the associated `Makefile` to turn your Turing machine into an executable.

## Example

[reverse.json](reverse.json) contains an example of the description of a Turing
machine that reverses a string. To use it:

```
$ ./machination -c reverse.json ASCII
Successfully written transition function as rules.h
$ make
cc -o mtruntime mtruntime.c
$ ./mtruntime "Hello world!"
!dlrow olleH
```
