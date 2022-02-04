from dataclasses import dataclass
from typing import Any, Optional

class AST():
    pass
class Statement(AST):
    pass
class NonStatement(AST):
    pass

@dataclass
class Block(AST):
    procedure : list[Statement | NonStatement]

@dataclass
class Definitions(AST):
    body : Block

    
# -------- Expression (start) --------
class Expression(Statement):
    pass

class Literal(Expression):
    pass

@dataclass
class Identifier(Literal):
    id : str

@dataclass
class Number(Literal):
    num : int

@dataclass
class BinaryOperation(Expression):
    lhs : Expression
    bin_op : str
    rhs : Expression

@dataclass
class FunctionCall(Expression):
    fun_name : str
    args : list[Expression]

# -------- Expression (end) --------



# -------- Statement (start) --------
@dataclass
class Assignment(Statement):
    lhs : Identifier
    rhs : Expression

@dataclass
class Sample(Statement):
    lhs : Identifier
    rhs : Expression | Any

@dataclass
class Return(Statement):
    ret : Expression
# -------- Statement (end) --------

@dataclass
class SetLiteral(AST):
    data : str

# -------- NonStatement (start) --------
@dataclass
class FunctionArgument(AST):
    arg_id : str
    arg_type : Optional[SetLiteral]
@dataclass
class FunctionArguments(AST):
    args : list[tuple[int, FunctionArgument]]

@dataclass
class FunctionDefinition(NonStatement):
    fun_name : str
    args : FunctionArguments
    block : Block

@dataclass
class IfStatement(NonStatement):
    condition : Expression
    then_block : Block
    else_block : Optional[Block]

@dataclass
class CallingProgramDefinition(NonStatement):
    name : str
    body : Block

@dataclass
class LibraryDefinition(NonStatement):
    name : str
    exposing : list[tuple[str,str]]
    body : Block

# -------- NonStatement (end) --------


def construct_ast(parse_tree) -> Any:
    match parse_tree:
        case {'id': name}:
            return Identifier(name)
        case {'num': number}:
            return Number(number)
        case {'assignment': {'lhs': lhs, 'rhs': rhs}}:
            return Assignment(construct_ast(lhs), construct_ast(rhs))
        case {'sample': {'lhs': lhs, 'rhs': rhs}}:
            return Sample(construct_ast(lhs), construct_ast(rhs))
        case {'return': expr}:
            return Return(construct_ast(expr))
        case {'fun_call': {'fun': name, 'args': args}}:
            return FunctionCall(name,[construct_ast(a) for a in args])
        case {'fun_def': {'fun_name': {'id': name}, 'args': args, 'block': block}}:
            return FunctionDefinition(name, FunctionArguments([(n,construct_ast(a)) for n,a in args]), construct_ast(block))
        case {'bin_op': {'op': op, 'lhs': lhs, 'rhs': rhs}}:
            return BinaryOperation(construct_ast(lhs),op,construct_ast(rhs))
        case {'set_literal': s}:
            return SetLiteral(s)
        case {'block': instructions}:
            return Block([construct_ast(inst) for inst in instructions])
        case {'program' : program}:
            return construct_ast(program)
        case {'calling_program_def': {'name': {'id': name}, 'body': block}}:
            return CallingProgramDefinition(name, construct_ast(block))
        case {'library_def': {'name': {'id': name}, 'body': block}}:
            return LibraryDefinition(name, [], construct_ast(block))
        case x if type(x) is list:
            return Block([construct_ast(y) for y in x])
        case _:
            print('Failed!', parse_tree)
            return parse_tree
    
