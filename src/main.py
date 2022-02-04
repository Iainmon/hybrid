import parser
import syntax
import latex
from prettyprinter import pprint

parse_tree = parser.file_to_ast_dict('../examples/input.rosu')
pprint(parse_tree)
print('\n\n------ Parse Tree Tree ------\n')
print(parse_tree)


ast = syntax.construct_ast(parse_tree)
print('\n\n------ Abstract Syntax Tree ------\n')
pprint(ast)

tex_source = latex.texify(syntax.Definitions(ast))
print('\n\n------ Latex Source ------\n')
print(tex_source)
