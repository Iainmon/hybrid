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
class String(Literal):
    string : str

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

class SetAtom(AST):
    pass
@dataclass
class NumberSetAtom(SetAtom):
    num : int
@dataclass
class IdentifierSetAtom(SetAtom):
    id : str

@dataclass
class SetLiteral(AST):
    data : list[SetAtom]

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

@dataclass
class QueryExpression(AST):
    pass
@dataclass
class QueryIdentifier(QueryExpression):
    pass
@dataclass
class QueryStatement(NonStatement):
    pass

@dataclass
class ProgramReference(QueryIdentifier):
    name : str
@dataclass
class LibraryReference(QueryIdentifier):
    name : str
@dataclass
class QueryRelation(QueryExpression):
    lhs : QueryExpression
    relation : str 
    rhs : QueryExpression

@dataclass
class Write(QueryExpression):
    body : String 

@dataclass
class ShowQueryStatement(QueryStatement):
    expression : QueryExpression

@dataclass
class WriteQueryStatement(QueryStatement):
    body : Write






def construct_ast(parse_tree) -> Any:
    match parse_tree:
        case {'id': name}:
            return Identifier(name)
        case {'num': number}:
            return Number(number)
        case {'string': string}:
            return String(string)
        case {'assignment': {'lhs': lhs, 'rhs': rhs}}:
            return Assignment(construct_ast(lhs), construct_ast(rhs))
        case {'sample': {'lhs': lhs, 'rhs': rhs}}:
            return Sample(construct_ast(lhs), construct_ast(rhs))
        case {'if': {'condition': condition, 'block': block}}:
            return IfStatement(construct_ast(condition),construct_ast({'block': block}),None)
        case {'return': expr}:            
            return Return(construct_ast(expr))
        case {'fun_call': {'fun': name, 'args': args}}:
            return FunctionCall(name,[construct_ast(a) for a in args])
        case {'arg_def': {'id': name, 'type': arg_type}}:
            return FunctionArgument(name,construct_ast(arg_type))
        case {'fun_def': {'fun_name': {'id': name}, 'args': args, 'block': block}}:
            return FunctionDefinition(name, FunctionArguments([(n,construct_ast(a)) for n,a in args]), construct_ast(block))
        case {'bin_op': {'op': op, 'lhs': lhs, 'rhs': rhs}}:
            return BinaryOperation(construct_ast(lhs),op,construct_ast(rhs))
        case {'set_literal': {'atom_list': atom_list}}:
            return SetLiteral([construct_ast(atom) for atom in atom_list])
        case {'set_atom': {'num': n}}:
            return NumberSetAtom(n)
        case {'set_atom': {'char': c}}:
            return IdentifierSetAtom(c)
        case {'block': instructions}:
            return Block([construct_ast(inst) for inst in instructions])
        case {'program' : program}:
            return construct_ast(program)
        case {'calling_program_def': {'name': {'id': name}, 'body': block}}:
            return CallingProgramDefinition(name, construct_ast(block))
        case {'library_def': {'name': {'id': name}, 'body': block}}:
            return LibraryDefinition(name, [], construct_ast(block))
        case {'query': query}:
            return construct_ast(query)
        case {'show_query': expr}:
            return ShowQueryStatement(construct_ast(expr))
        case {'query_relation': {'lhs':lhs,'relation': relation, 'rhs': rhs}}:
            return QueryRelation(construct_ast(lhs),relation,construct_ast(rhs))
        case {'pro': {'id': name}}:
            return ProgramReference(name)
        case {'lib': {'id': name}}:
            return LibraryReference(name)
        case {'write': body}:
            return Write(construct_ast(body))
        case {'write_query': write}:
            return WriteQueryStatement(construct_ast(write))
        case x if type(x) is list:
            return Block([construct_ast(y) for y in x])
        case _:
            print('Failed!', parse_tree)
            return parse_tree
    
