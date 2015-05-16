# Lang_Compiler
Compiler for an original (as of yet unnamed) programming language.  

The grammar is in progress, but the existing version of the grammar
can be found in the "grammar" file.

A function declaration must have the form:

    let foobar : {typeA, typeB,...} -> {typeC}

All functions must be declared before they can be defined or 
called from within another function.  A function that takes no parameters
and/or returns no value must have the "void" keyword as its only parameter
or in its return field.

Currently the only recognized types are "int" and "char", which are the
usual C style int and char.
