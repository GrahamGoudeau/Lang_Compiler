from __future__ import print_function
from type_keyword_info import *
from tokenize import Token_Label, get_label_str
import sys

# expects a dictionary of every function in the input code
# returns true if the parse succeeds, false otherwise
def is_parsed(func_map):
    for f in func_map:
        function = func_map[f]
        definition = function.def_block

        parse_definition(iter(definition), function)

    return True


# start state for parsing; expeccts iter of function definition
def parse_definition(def_iter, function):
    # get function name token
    func_name = def_iter.next()
    expect_label(func_name, Token_Label.Func_Id)

    # make sure parameters are correct
    parse_params(def_iter, function) 

    # get past '=' operator
    assgn = def_iter.next()
    expect_symbol(assgn, '=')

    # expects a string of tokens beginning with a '{'
    parse_block(def_iter, function)

def parse_params(def_iter, function):
    open_paren = def_iter.next()
    expect_symbol(open_paren, '(')
    num_param = 0
    next_token = def_iter.next()
    while next_token.symbol != ')':
        if next_token.symbol == ',':
            next_token = def_iter.next()
            continue
        else: num_param += 1

        next_token = def_iter.next()

    expect_num_param(function, num_param)

def parse_block(def_iter, function):
    open_curly = def_iter.next()
    expect_symbol(open_curly, '{')

    parse_statement_list(def_iter, function)

# expects the first token of a statement, 
def parse_statement_list(def_iter, function):
    first_token = def_iter.next()
    if first_token.symbol == '}':
        return
    elif first_token.symbol == RETURN_KEYWORD:
        parse_return(def_iter, function)

        semicolon = def_iter.next()
        expect_symbol(semicolon, ';')

        close_curly = def_iter.next()
        expect_symbol(close_curly, '}')
    elif first_token.label == Token_Label.Var_Id:
        parse_eval(first_token, def_iter, function)
    elif first_token.label == Token_Lable.Fun_Id:
        parse_freestanding_func(def_iter, function)
    else:
        pass
        print("uncaught case with " + token.symbol)
        sys.exit()

# expects the return value; 'return' has been consumed already
def parse_return(def_iter, function):
    value = def_iter.next()
    if value.label != Token_Label.Var_Id and \
            value.label != Token_Label.Func_Id and \
            value.label != Token_Label.Num:
        print(get_label_str(value.label))
        print("Error in return statement: return '" + \
                value.symbol + "' on line " + str(value.line_num), \
                file=sys.stderr)
        sys.exit()

def expect_symbol(token, symbol):
    if token.symbol != symbol:
        actual = token.symbol
        expect = symbol
        print("Expected token '" + expect + "'; got token '" + \
                actual + "' at line num " + str(token.line_num), \
                file=sys.stderr)
        sys.exit() 

def expect_label(token, label):
    if token.label != label:
        actual = get_label_str(token.label)
        expect = get_label_str(label)
        print("Expected token with label " + expect + \
                "; got token " + token.symbol + " with label " + actual + \
                " at line num " + str(token.line_num), \
                file=sys.stderr)
        sys.exit()

def expect_num_param(function, num_param):
    # the function map builder checked for void already
    if "void" in function.param_list:
        return
    if function.num_param != num_param:
        print("In definition of function " + function.name + ", expected " + \
            str(function.num_param) + " parameters; saw " + \
            str(num_param) + " parameters", \
            file=sys.stderr) 
        sys.exit()
