from __future__ import print_function
from type_keyword_info import *
import sys

class Variable:
    def __init__(self, name, type=None, is_in_scope=False):
        self.name = name
        self.type = type
        self.is_in_scope = is_in_scope

class Function:
    def __init__(self, name, param_list, return_type, def_block = []):
        self.name = name
        self.num_param = len(param_list)
        self.param_list = param_list
        self.return_type = return_type
        self.def_block = def_block

class Token_Label:
    Var_Id, Func_Id, Type, Num, Operator, \
        Keyword, Delimiter, Paren, Curly = range(0,9)

def get_label_str(label):
    if label == 0:
        return "Var_Id"
    elif label == 1:
        return "Func_Id"
    elif label == 2:
        return "Type"
    elif label == 3:
        return "Num"
    elif label == 4:
        return "Operator"
    elif label == 5:
        return "Keyword"
    elif label == 6:
        return "Delimiter"
    elif label == 7:
        return "Paren"
    elif label == 8:
        return "Curly Bracket"
 
class Token:
    def __init__(self, symbol, label, line_num):
        self.symbol = symbol
        self.label = label
        self.line_num = line_num

def check_parens(code):
    stack = []

    line_num = 1
    col = 1
    for i in range(len(code)):
        # reset error report line/col numbers on newline
        if code[i] == '\n':
            line_num += 1
            col = 1
            continue

        if code[i] in OPEN_BRACKET:
            stack.append(code[i])
        elif code[i] in CLOSE_BRACKET and len(stack) != 0: 
            stack.pop()
        elif code[i] in CLOSE_BRACKET and len(stack) == 0: 
            print("Mismatched brackets at line " + str(line_num) +
                    " col " + str(col), file=sys.stderr)
            sys.exit()

        col += 1

    if len(stack) != 0:
        print("Too many open brackets", file=sys.stderr)
        sys.exit()

def tokenize(raw_string):
    tokens = []
    cur_toke = ""
    prev_toke = ""
    line_num = 1

    for c in raw_string:
        if c.isspace():
            if cur_toke: 
                lab = determine_label(cur_toke, prev_toke, line_num)
                tokens.append(Token(cur_toke, lab, line_num))
                prev_toke = cur_toke
                cur_toke = ""

            if c == '\n':
                line_num += 1
            continue
        
        cur_toke = cur_toke + c

        if cur_toke.isdigit(): continue

        if (cur_toke.isalpha() or '_' in cur_toke) and c not in OPEN_BRACKET: 
            continue

        # c was not part of current token; add all of token up to c
        if cur_toke[:-1]: 
            label = determine_label(cur_toke[:-1], prev_toke, line_num)
            tokens.append(Token(cur_toke[:-1], label, line_num))

        prev_toke = cur_toke[:-1]
        cur_toke = c

    return tokens

def determine_label(token, prev_toke, line):
    if token.isdigit():
        label = Token_Label.Num
    elif token in TYPE_LIST:
        label = Token_Label.Type
    elif token in KEYWORDS:
        label = Token_Label.Keyword
    elif (token.isalpha() or '_' in token):
        if prev_toke == "let":
            label = Token_Label.Func_Id
        else: label = Token_Label.Var_Id
    elif token == DELIM:
        label = Token_Label.Delimiter
    elif token == '(' or token == ')':
        label = Token_Label.Paren
    elif token == '{' or token == '}':
        label = Token_Label.Curly
    elif token in OPERATORS:
        label = Token_Label.Operator
    else:
        print("Unable to resolve token '" + token + "' on line " \
                + str(line), file=sys.stderr)
        sys.exit()

    return label

# make a function map; ensures that main exists and is defined
# needs an iterator of the tokens, and the original 
# array to get the function definition
def make_function_map(token_iter, tokenized_arr):
    func_map = {}
    prev_tok_symbol = ""
    while True:
        try:
            token = token_iter.next()
        except StopIteration:
            break

        if token.label == Token_Label.Func_Id:
            if token.symbol not in func_map:
                # get declaration of function and associated info
                new_function = make_new_function(token.symbol, token_iter)
                func_map[token.symbol] = new_function

                # get definition of function if it exists
                func_code = get_def_block(token.symbol, tokenized_arr)
                func_map[token.symbol].def_block = func_code
            else:
                print("Redeclaration of function '" + token.symbol + \
                        " at line " + str(token.line_num), file=sys.stderr)

        prev_tok_symbol = token.symbol

    # ensures that if a func has 'void' as a paremter, it is the only param
    # also checks that each function has at least 1 parameter
    # fails with sys.exit() and a message if not
    # (only checks declarations)
    check_params(func_map)

    # ensures that a return type exists, and the function 
    # does not contain 'return' if it returns void
    check_return(func_map)

    # mark all occurrences of function calls as function ids
    mark_functions(func_map, tokenized_arr)

    # ensure main exists and is defined
    if "main" not in func_map:
        print("Missing declaration of function 'main'", file=sys.stderr)
        sys.exit()
    if not func_map["main"].def_block:
        print("Missing definition of function 'main'", file=sys.stderr)
        sys.exit()

    return func_map

# check the parameter types in the declarations
def check_params(func_map):
    # check for void
    void = "void"
    for f in func_map:
        function = func_map[f]
        if void in function.param_list and function.num_param != 1:
            print("Function " + function.name + " has multiple parameters" + \
                " with 'void' parameter", file=sys.stderr)
            sys.exit()
        if function.num_param < 1:
            print("Function " + function.name + " must have at least one" + \
                " parameter (can have 'void' keyword)", file=sys.stderr)
            sys.exit()

def check_return(func_map):
    for f in func_map:
        saw_return = False
        function = func_map[f]
        for t in function.def_block:
            if t.symbol == RETURN_KEYWORD:
                saw_return = True

        if function.return_type == "void" and saw_return:
            print("Function " + function.name + " is void, " + \
                "but its definition contains 'return' keyword", \
                file=sys.stderr)
            sys.exit()
        if function.return_type != "void" and not saw_return:
            print("Function " + function.name + " has nonvoid " + \
                "return type, but 'return' keyword not in definition", \
                file=sys.stderr)
            sys.exit() 
        if not function.return_type:
            print("Function " + function.name + " has no return type; " + \
                "must return at least 'void'", file=sys.stderr)
            sys.exit()

# mark function calls as function ids
def mark_functions(func_map, tokenized):
    for f in func_map:
        for token in tokenized:
            if token.symbol == func_map[f].name:
                token.label = Token_Label.Func_Id
        
''' example function declaration:
        let foobar : {type1,type2,...} -> {return_type}
    the following functions expect to see the above, and fail
    with sys.exit() if otherwise
'''
def make_new_function(func_name, token_iter):
    param_list = get_param_list(func_name, token_iter)
    return_type = get_return_type(func_name, token_iter)

    return Function(func_name, param_list, return_type)

# expects to first see a ':'
def get_param_list(func_name, token_iter):
    colon = token_iter.next()
    func_decl_expect(func_name, colon.symbol, ':')
    open_curly = token_iter.next()
    func_decl_expect(func_name, open_curly.symbol, '{')
    
    param_list = []
    next_token = token_iter.next()
    while (next_token.symbol != '}' or next_token == ','):
        if next_token.symbol != ',':
            func_decl_expect_type(func_name, next_token, Token_Label.Type)
            param_list.append(next_token.symbol) 
        next_token = token_iter.next()

    return param_list

# expects to first see the '-' in the "->" symbol
def get_return_type(func_name, token_iter):
    hyphen = token_iter.next()
    func_decl_expect(func_name, hyphen.symbol, '-')
    GT_sign = token_iter.next()
    func_decl_expect(func_name, GT_sign.symbol, '>')
    open_curly = token_iter.next()
    func_decl_expect(func_name, open_curly.symbol, '{')

    return_type = token_iter.next()
    func_decl_expect_type(func_name, return_type, Token_Label.Type)

    return return_type.symbol
    
        
# given a token, checks if its label is a "type" label
def func_decl_expect_type(func_name, actual, expected_label):
    if actual.label != expected_label:
        print("In declaration of " + func_name + ":\n\t" + \
                "expected a valid type; instead saw '" + actual.symbol + "'", \
                file=sys.stderr)
        sys.exit()

# checks if the next character is the same as expected
def func_decl_expect(func_name, actual_token, expected_token):
    if actual_token != expected_token:
        print("In declaration of " + func_name + ":\n\t" + \
                "saw '" + actual_token + "'; expected '" + expected_token, \
                + "'", file=sys.stderr)
        sys.exit()

def get_def_block(func_symbol, tokenized_arr):
    seen_definition = False
    in_block = []
    function_definition = []
    record_tokens = False

    for token in tokenized_arr:
        if token.symbol == '{':
            in_block.append(True)

        if token.symbol == '}':
            in_block.pop()
            if not in_block and record_tokens:
                function_definition.append(token)
                record_tokens = False

        # before definition, a function id has label Var_Id
        if token.label == Token_Label.Var_Id and token.symbol == func_symbol:
            if seen_definition:
                print("Redefinition of function " + func_symbol + \
                        " at line " + str(token.line_num), file=sys.stderr)
                sys.exit()
            if not in_block:
                record_tokens = True
                seen_definition = True 

        if record_tokens:
            function_definition.append(token)

    return function_definition
