
from syntax import *
import os
import tempfile
from dataclasses import dataclass

@dataclass
class Stylizer(AST):
    pass
@dataclass
class Relation(Stylizer):
    pass

@dataclass
class HighlightExpression(Stylizer):
    expression : AST

@dataclass
class Link(Relation):
    lhs : AST
    rhs : AST
@dataclass
class Interchangable(Relation):
    lhs : AST
    rhs : AST
@dataclass
class Indistinguishable(Relation):
    lhs : AST
    rhs : AST


def bin_op_tex(op: str) -> str:
    op_dict = {
        'xor' : '\\oplus',
        'is': '\\overset{?}{=}',
        '*': '\\cdot',
        '&': '\\&',
    }
    if op in op_dict.keys():
        return op_dict[op]
    return op
def texify_relation(relation: str) -> str:
    rel_dict = {
        '<>' : '\\link',
        '==' : '\\equiv',
        '~=' : '\\indist',
        '|'  : '\\quad',
        '=>' : '\\implies',
    }
    if relation in rel_dict.keys():
        return rel_dict[relation]
    return relation

context = {
    'library' : {},
    'program' : {}
}

is_in_math_block = False
depth = 0
def texify(ast: AST,queries_only = True) -> str:
    global is_in_math_block
    match ast:
        case Identifier(id):
            return id
        case Number(n):
            if n == 0 or n == 1:
                return f'\\bit{n}'
            return str(n)
        case String(string):
            if is_in_math_block:
                return '\\text{' + string + '}'
            return string
        case Assignment(lhs,rhs):
            return f'${texify(lhs)} := {texify(rhs)}$'
        case Sample(lhs,rhs):
            return f'${texify(lhs)} \\lar {texify(rhs)}$'
        case IfStatement(condition,then_block,else_block):
            block_lines = texify(then_block).split('\\\\')
            indented_block = '\\\\'.join(f'\\>{line}' for line in block_lines)
            return f'if ${texify(condition)}$ then:\\\\{indented_block}'
        case SetLiteral(atoms):
            return '\\{' + ','.join(texify(atom) for atom in atoms) + '\\}'
        case NumberSetAtom(n):
            if n == 0 or n == 1:
                return f'\\bit{n}'
            return f'\\bit{n}'
        case IdentifierSetAtom(c):
            return '\\str{' + c + '}'
        case Return(expr):
            return f'return ${texify(expr)}$'
        case FunctionCall(name,args):
            args_list = ', '.join(texify(arg) for arg in args)
            return ('\\subname{' + name + '}' if len(name) > 2 else f'{name}') + f'({args_list})'
        case FunctionArgument(name,type):
            if type is None:
                return str(name)
            return f'{name} \\in {texify(type)}'

            # return f'{name}' + '\\in \\Bin'
        case FunctionArguments(args):
            return ', '.join(texify(arg) for n,arg in args)
        case FunctionDefinition(fun_name,args,block):
            args_list = texify(args)
            
            header = '\\underline{$' + ('\\subname{' + fun_name + '}' if len(fun_name) > 2 else f'{fun_name}') + f'({args_list}):' + '$}'
            return header + '\\\\' + texify(block)
        case BinaryOperation(lhs,bin_op,rhs):
            return f'{texify(lhs)} {bin_op_tex(bin_op)} {texify(rhs)}'
        case Block(procedure):
            lines = [f'\\> {texify(stmt)}' for stmt in procedure]
            return '\\\\'.join(line for line in lines)
        case CallingProgramDefinition(name,Block(body)):
            context['program'][name] = CallingProgramDefinition(name,Block(body))
            body_source = '\\\\'.join(texify(line) for line in body)
            return '\\titlecodebox{\\fancy{' + name + '} }{' + body_source + '}'
        case LibraryDefinition(name,exposing,Block(body)):
            context['library'][name] = LibraryDefinition(name,exposing,Block(body))
            body_source = '\\\\'.join(texify(line) for line in body)
            return '\\titlecodebox{ \\lib{' + name + '} }{' + body_source + '}'
        case Definitions(Block(definitions)):
            if queries_only:
                for line in definitions:
                    texify(line) # populates context
                source = ''.join(texify(line) for line in definitions if isinstance(line,QueryStatement))
                if is_in_math_block:
                    is_in_math_block = False
                    source += '\\end{gather*}'
                return source
            return '\\quad'.join(texify(line) for line in definitions)
        case ProgramReference(name):
            if name in context['program'].keys():
                return texify(context['program'][name])
            return '\\fancy{' + name + '}'
        case LibraryReference(name):
            if name in context['library'].keys():
                return texify(context['library'][name])
            return '\\lib{' + name + '}'
        case ShowQueryStatement(expr):
            if is_in_math_block:
                return texify(expr)
            else:
                is_in_math_block = True
                return '\\begin{gather*}\n' + texify(expr)
        case QueryRelation(lhs,relation,rhs):
            return texify(lhs) + texify_relation(relation) + texify(rhs)
        case Write(String(comment)):
            if is_in_math_block:
                return '\\text{' + comment + '}'
            else:
                return comment
        case WriteQueryStatement(String(comment)):
            if is_in_math_block:
                is_in_math_block = False
                return '\\end{gather*}\n' + texify(String(comment)) + ' '
            return texify(String(comment)) + ' '
        case _:
            print('UNDEFINED', ast)
            return ''


def link(prog: AST, lib: LibraryDefinition,glowing=False) -> str:
    if glowing:
        return f'{texify(prog)}' + '\\link\\glowingbox{' + f'{texify(lib)}' + '}'
    return f'{texify(prog)}' + '\\link' + f'{texify(lib)}'

def equiv(left: AST, right: AST,align=False) -> str:
    if align:
        return f'{texify(left)}' + '&\\equiv' + f'{texify(right)}'
    return f'{texify(left)}\\equiv{texify(right)}'






def save_file(tex_source,file):
    pf = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../tex/prelude.tex'), 'r')
    prelude = pf.read()
    source = prelude + '\\begin{document} ' + tex_source + '\\end{document}'
    output_tex_file = os.path.join(os.path.abspath(os.getcwd()),'../tex/temp_out.tex')
    f = open(output_tex_file,'w')
    f.write(source)
    f.close()
    inputted_path = output_tex_file
    os.system("cd ../tex; pdflatex %s" % inputted_path)