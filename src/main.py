import parser
import syntax
import latex
from prettyprinter import pprint
from language import definition_libraries, definition_calling_programs

parse_tree = parser.file_to_ast_dict('../examples/input.rosu')
# pprint(parse_tree)
print('\n\n------ Parse Tree Tree ------\n')
print(parse_tree)


ast = syntax.construct_ast(parse_tree)
print('\n\n------ Abstract Syntax Tree ------\n')
pprint(ast)

tex_source = latex.texify(syntax.Definitions(ast))
print('\n\n------ Latex Source ------\n')
print(tex_source)

# source = ''
# print('\n\n------ Latex Definitions ------\n')
progA = definition_calling_programs(ast)[0]
libs = definition_libraries(ast)
# for lib in libs:
#     print(f'&{latex.link(progA,lib,glowing=True)}\\\\')
#     source += f'&{latex.link(progA,lib,glowing=True)}\\\\'

# source = ''
# print('\n\n------ Equivalences Definitions ------\n')
# for i in range(0,len(libs)-1,2):
#     print(latex.equiv(libs[i],libs[i+1],align=True) + '\\\\')
#     source += latex.equiv(libs[i],libs[i+1]) + '\\implies&' +f'{latex.link(progA,libs[i],glowing=True)}\\equiv {latex.link(progA,libs[i+1],glowing=True)}' + '\\\\'

# latex.save_file(source,'output.pdf')
file_name = '../examples/example.rosu'
tex_source = latex.texify(syntax.Definitions(syntax.construct_ast(parser.file_to_ast_dict(file_name))))
latex.save_file(tex_source, file_name)
print(tex_source)