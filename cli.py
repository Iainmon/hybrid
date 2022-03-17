import sys
from hybrid import syntax, latex, parser, visualization


from prettyprinter import pprint
from hybrid.language import definition_libraries, definition_calling_programs
from hybrid.visualization import construct_ast_graph
if len(sys.argv) < 2:
    print('No input .rosu file specified!')
    sys.exit(0)

parse_tree = parser.file_to_ast_dict(f'./{sys.argv[1]}')
print('\n\n------ Parse Tree Tree ------\n')
print(parse_tree)


ast = syntax.construct_ast(parse_tree)
print('\n\n------ Abstract Syntax Tree ------\n')
pprint(ast)

tex_source = latex.texify(syntax.Definitions(ast))
print('\n\n------ Latex Source ------\n')
print(tex_source)


construct_ast_graph(ast)
