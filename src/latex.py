
from syntax import *



# def latexify(ast):
#     match ast:
#         case {'program': block}:
#             return latexify()


def bin_op_tex(op: str) -> str:
    op_dict = {
        'xor' : '\\oplus',
        'is': '\\overset{?}{=}'
    }
    if op in op_dict.keys():
        return op_dict[op]
    return op

def texify(ast: AST) -> str:
    match ast:
        case Identifier(id):
            return id
        case Number(n):
            return str(n)
        case Assignment(lhs,rhs):
            return f'${texify(lhs)} := {texify(rhs)}$'
        case Sample(lhs,rhs):
            return f'${texify(lhs)} \\lar {texify(rhs)}$'
        case SetLiteral(data):
            if data == '{0,1}':
                return '\\Bin'
            else:
                return data
        case Return(expr):
            return f'return ${texify(expr)}$'
        case FunctionCall(name,args):
            args_list = ', '.join(texify(arg) for arg in args)
            return '\\subname{' + name + '}' + f'({args_list})'
        case FunctionArgument(name,type):
            if type is None:
                return str(name)
            return f'{name}' + '\\in \\Bin'
        case FunctionArguments(args):
            return ', '.join(texify(arg) for n,arg in args)
        case FunctionDefinition(fun_name,args,block):
            args_list = texify(args)
            header = '\\underline{$\\subname{' + fun_name + '}' + f'({args_list}):' + '$}'
            return header + '\\\\' + texify(block)
        case BinaryOperation(lhs,bin_op,rhs):
            return f'{texify(lhs)} {bin_op_tex(bin_op)} {texify(rhs)}'
        case Block(procedure):
            lines = [f'\\> {texify(stmt)}' for stmt in procedure]
            return '\\\\'.join(line for line in lines)
        case CallingProgramDefinition(name,Block(body)):
            body_source = '\\\\'.join(texify(line) for line in body)
            return '\\titlecodebox{\\fancy{' + name + '} }{' + body_source + '}'
        case LibraryDefinition(name,exposing,Block(body)):
            body_source = '\\\\'.join(texify(line) for line in body)
            return '\\titlecodebox{ \\lib{' + name + '} }{' + body_source + '}'
        case Definitions(Block(definitions)):
            return '\\quad'.join(texify(line) for line in definitions)
        case _:
            print('UNDEFINED', ast)
            return ''

