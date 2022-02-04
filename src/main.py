import parser
import syntax
from prettyprinter import pprint

parse_tree = parser.file_to_ast_dict('../examples/input.rosu')
pprint(parse_tree)

ast = syntax.construct_ast(parse_tree)
pprint(ast)