import dataclasses
from dataclasses import dataclass, Field, MISSING, _FIELDS, _FIELD, _FIELD_INITVAR  # type: ignore
import dataclasses as dc

from typing import Any, Optional, Type, TypeVar, List, Dict


Data = Dict[str, Any]
T = TypeVar("T", bound=Any)

def get_fields(data_class: Type[T]) -> List[Field]:
    fields = getattr(data_class, _FIELDS)
    return [f for f in fields.values() if f._field_type is _FIELD or f._field_type is _FIELD_INITVAR]


@dataclass(frozen=True,eq=True)
class CompositeDict():
    def __hash__(self):
        return hash(str(repr(self)))
    def as_dict(self,named_args=True):
        classtype = type(self)
        if not dc.is_dataclass(classtype):
            raise TypeError(f"Expected dataclass instance, got '{classtype!r}' object")
        name = classtype.__qualname__
        children = dict()
        for key, value in self.__dict__.items():
            if key in self.__dataclass_fields__.keys():
                if type(value) is list:
                    children[key] = [item.as_dict(named_args=named_args) for item in value]
                elif dc.is_dataclass(value):
                    if not hasattr(value,'as_dict'):
                        raise TypeError(f"Expected CompositeDict instance, got '{type(value)!r}' object")
                    children[key] = value.as_dict(named_args=named_args)
                else:
                    children[key] = value
        if not named_args:
            return { name : tuple(children.values())}
        return { name : children }
    def children(self,named=True):
        children = list(self.as_dict().values())[0]
        return [getattr(self,c) for c in children]
        
@dataclass(frozen=True,eq=True)
class AST(CompositeDict):
    pass
@dataclass(frozen=True,eq=True)
class Statement(AST):
    pass
@dataclass(frozen=True,eq=True)
class NonStatement(AST):
    pass

@dataclass(frozen=True,eq=True)
class Block(AST):
    procedure : list[Statement | NonStatement]

@dataclass(frozen=True,eq=True)
class Definitions(AST):
    body : Block


# -------- Expression (start) --------
@dataclass(frozen=True,eq=True)
class Expression(Statement):
    pass
@dataclass(frozen=True,eq=True)
class Literal(Expression):
    pass

@dataclass(frozen=True,eq=True)
class Identifier(Literal):
    id : str

@dataclass(frozen=True,eq=True)
class Number(Literal):
    num : int

@dataclass(frozen=True,eq=True)
class String(Literal):
    string : str

@dataclass(frozen=True,eq=True)
class BinaryOperation(Expression):
    lhs : Expression
    bin_op : str
    rhs : Expression

@dataclass(frozen=True,eq=True)
class FunctionCall(Expression):
    fun_name : str
    args : list[Expression]

# -------- Expression (end) --------



# -------- Statement (start) --------
@dataclass(frozen=True,eq=True)
class Assignment(Statement):
    lhs : Identifier
    rhs : Expression

@dataclass(frozen=True,eq=True)
class Sample(Statement):
    lhs : Identifier
    rhs : Expression | Any

@dataclass(frozen=True,eq=True)
class Return(Statement):
    ret : Expression
# -------- Statement (end) --------
@dataclass(frozen=True,eq=True)
class SetAtom(AST):
    pass
@dataclass(frozen=True,eq=True)
class NumberSetAtom(SetAtom):
    num : int
@dataclass(frozen=True,eq=True)
class IdentifierSetAtom(SetAtom):
    id : str

@dataclass(frozen=True,eq=True)
class SetLiteral(AST):
    data : list[SetAtom]

# -------- NonStatement (start) --------
@dataclass(frozen=True,eq=True)
class FunctionArgument(AST):
    arg_id : str
    arg_type : Optional[SetLiteral]
@dataclass(frozen=True,eq=True)
class FunctionArguments(AST):
    args : list[tuple[int, FunctionArgument]]

@dataclass(frozen=True,eq=True)
class FunctionDefinition(NonStatement):
    fun_name : str
    args : FunctionArguments
    block : Block

@dataclass(frozen=True,eq=True)
class IfStatement(NonStatement):
    condition : Expression
    then_block : Block
    else_block : Optional[Block]

@dataclass(frozen=True,eq=True)
class CallingProgramDefinition(NonStatement):
    name : str
    body : Block

@dataclass(frozen=True,eq=True)
class LibraryDefinition(NonStatement):
    name : str
    exposing : list[tuple[str,str]]
    body : Block

# -------- NonStatement (end) --------

@dataclass(frozen=True,eq=True)
class QueryExpression(AST):
    pass
@dataclass(frozen=True,eq=True)
class QueryIdentifier(QueryExpression):
    pass
@dataclass(frozen=True,eq=True)
class QueryStatement(NonStatement):
    pass

@dataclass(frozen=True,eq=True)
class ProgramReference(QueryIdentifier):
    name : str
@dataclass(frozen=True,eq=True)
class LibraryReference(QueryIdentifier):
    name : str
@dataclass(frozen=True,eq=True)
class QueryRelation(QueryExpression):
    lhs : QueryExpression
    relation : str 
    rhs : QueryExpression

@dataclass(frozen=True,eq=True)
class Write(QueryExpression):
    body : String 

@dataclass(frozen=True,eq=True)
class ShowQueryStatement(QueryStatement):
    expression : QueryExpression

@dataclass(frozen=True,eq=True)
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
    
