from aifc import Error
from copy import deepcopy
from typing import Generic, Literal, Optional, cast
import typing as ty


from dataclasses import dataclass, field
import dataclasses as dc

from antlr4 import *
from antlr4.tree.Tree import Tree, TerminalNodeImpl, ParseTree, ParseTreeWalker
from antlr4.tree.Trees import Trees
from antlr4.ParserRuleContext import ParserRuleContext

from .parsing.HybLangLexer import HybLangLexer
from .parsing.HybLangParser import HybLangParser
from .parsing.HybLangVisitor import HybLangVisitor

import prettyprinter as pp
from prettyprinter import pprint

NonTerminalName = ty.Literal["prog", "stat", "expr", None]


def get_rule_name(node: Tree) -> str:
    return str(Trees.getNodeText(node, HybLangParser.ruleNames))


def get_children_derivation_names(node: Tree):
    return [
        method_name
        for method_name in dir(node)
        if method_name in HybLangParser.ruleNames
        and callable(getattr(node, method_name))
    ]


def copy_context(node):
    # ctx = ParserRuleContext()
    # ctx.copyFrom(node)
    return node


def expand_all_derivations(node: ParserRuleContext):
    derivation_rules = get_children_derivation_names(node)
    root_copies = [(rule, node) for rule in derivation_rules]
    derived_copies = [(rule, getattr(n, rule)()) for (rule, n) in root_copies]
    return derived_copies


def non_terminal_children(ctx):
    children = list(ctx.getChildren())
    return [
        c
        for c in children
        if (not isinstance(c, TerminalNode)) and (not isinstance(c, TerminalNodeImpl))
    ]


class RawSyntaxTreeVisitor(HybLangVisitor):
    def visitProgram(self, ctx: HybLangParser.ProgramContext):
        return {"program": {"block": self.visit(ctx.procedure())}}

    def visitProcedure(self, ctx: HybLangParser.ProcedureContext):
        children = non_terminal_children(ctx)
        return [self.visit(c) for c in children]

    def visitCall_prog_def(self, ctx: HybLangParser.Call_prog_defContext):
        name = self.visit(ctx.IDENTIFIER())
        block = self.visit(ctx.block())
        return {"calling_program_def": {"name": name, "body": block}}

    def visitLibrary_def(self, ctx: HybLangParser.Library_defContext):
        name = self.visit(ctx.IDENTIFIER())
        block = self.visit(ctx.block())
        exposing = (
            self.visit(ctx.exposing_sequence()) if ctx.exposing_sequence() else []
        )
        return {"library_def": {"name": name, "exposing": exposing, "body": block}}

    def visitBlock(self, ctx: HybLangParser.BlockContext):
        return {"block": self.visit(ctx.procedure())}

    def visitStatement(self, ctx: HybLangParser.StatementContext):
        # return {"stmt": self.visit(non_terminal_children(ctx)[0])}
        return self.visit(non_terminal_children(ctx)[0])

    def visitAssignment(self, ctx: HybLangParser.AssignmentContext):
        return {
            "assignment": {
                "lhs": self.visit(ctx.IDENTIFIER()),
                "rhs": self.visit(ctx.expression()),
            }
        }

    def visitSample(self, ctx: HybLangParser.SampleContext):
        return {
            "sample": {
                "lhs": self.visit(ctx.IDENTIFIER()),
                "rhs": self.visit(ctx.set_type() or ctx.expression()),
            }
        }

    def visitSet_type(self, ctx: HybLangParser.Set_typeContext):
        if ctx.set_lit():
            children = non_terminal_children(ctx)
            return {"set_literal": {"atom_list": [self.visit(c) for c in children]}}
        return {"set_literal": ctx.getText()}

    def visitSet_lit(self, ctx: HybLangParser.Set_litContext):
        if ctx.IDENTIFIER():
            return {"set_atom": {"char": self.visit(ctx.IDENTIFIER())["id"]}}
        else:
            return {"set_atom": {"num": self.visit(ctx.NUMBER())["num"]}}

    def visitExpression(self, ctx: HybLangParser.ExpressionContext):
        children = list(ctx.children or [])
        visited = list(map(self.visit, children))

        match visited:
            case [{"id": i}]:
                return {"id": i}
            case [{"num": n}]:
                return {"num": n}
            case [lhs, {"op": op}, rhs]:
                return {
                    "bin_op": {
                        "op": op,
                        "lhs": lhs,
                        "rhs": rhs,
                    }
                }
            case [{"fun_call": fun_call}]:
                return {"fun_call": fun_call}
            # case [x]:
            #     return x
            case ["(", e, ")"]:
                return e
            case _:
                return visited

        return super().visitExpression(ctx)

    def visitBin_op(self, ctx: HybLangParser.Bin_opContext):
        child = self.visitChildren(ctx)
        return {"op": (child or [""])}

    def visitFunction_call(self, ctx: HybLangParser.Function_callContext):
        children = non_terminal_children(ctx)
        return {
            "fun_call": {
                "fun": self.visit(ctx.IDENTIFIER())["id"],
                "args": [self.visit(c) for c in children],
            }
        }

    def visitReturn_stmt(self, ctx: HybLangParser.Return_stmtContext):
        return {"return": self.visit(ctx.expression())}

    def visitFunction_arguments(self, ctx: HybLangParser.Function_argumentsContext):
        children = non_terminal_children(ctx) or []
        args = list(map(self.visit, children))
        return list(enumerate(args))

    def visitFunction_argument(self, ctx: HybLangParser.Function_argumentContext):
        if ctx.set_type():
            return {
                "arg_def": {
                    "id": self.visit(ctx.IDENTIFIER())["id"],
                    "type": self.visit(ctx.set_type()),
                }
            }
        return self.visit(ctx.IDENTIFIER())

    def visitFunction_def(self, ctx: HybLangParser.Function_defContext):
        args = self.visit(ctx.function_arguments()) if ctx.function_arguments() else []
        name = self.visit(ctx.IDENTIFIER())
        block = self.visit(ctx.block())
        return {
            "fun_def": {
                "fun_name": name,
                "args": args,
                "block": block["block"],
            }
        }
        return super().visitFunction_def(ctx)

    def visitTerminal(self, node: TerminalNodeImpl):
        token_type = node.getSymbol().type
        match token_type:
            case HybLangLexer.NUMBER:
                return {"num": int(node.getText() or "")}
            case HybLangLexer.IDENTIFIER:
                return {"id": node.getText()}
            case _:
                return node.getText()

    def visitIf_stmt(self, ctx: HybLangParser.If_stmtContext):
        return {
            "if": {
                "condition": self.visit(ctx.expression()),
                "block": self.visit((ctx.block() or [])[0])["block"],
            }
        }
        return super().visitIf_stmt(ctx)

    def visitQuery_statement(self, ctx: HybLangParser.Query_statementContext):
        children = non_terminal_children(ctx)
        visited = list(map(self.visit, children))
        match visited:
            case [c]:
                return {"query": c}
        print('Fail!', visited)
        # return {"query": self.visit(ctx.show_query_statement() or ctx.write_query_statement())}

    def visitShow_query_statement(self, ctx: HybLangParser.Show_query_statementContext):
        return {"show_query": self.visit(ctx.query_expression())}

    def visitQuery_relation(self, ctx: HybLangParser.Query_relationContext):
        return {"relation": ctx.getText()}

    def visitQuery_expression(self, ctx: HybLangParser.Query_expressionContext):
        children = list(ctx.children or [])
        visited = list(map(self.visit, children))
        print(visited)
        match visited:
            case ["pro", _, identifier, _] | ["program", _, identifier, _]:
                return {"pro": identifier}
            case ["lib", _, identifier, _] | ["library", _, identifier, _]:
                return {"lib": identifier}
            case [lhs, {"relation": relation}, rhs]:
                return {
                    "query_relation": {"lhs": lhs, "relation": relation, "rhs": rhs}
                }
            case ['write', _,string_lit,_]:
                return {'write': string_lit}
            case ['(',e,')']:
                return e
            case [{'id':name}]:
                return {'id':name}
            case _:
                print('Failed!', visited)

    def visitString_literal(self, ctx: HybLangParser.String_literalContext):
        str_lit = ctx.STRING_LITERAL()
        body = str_lit.getText() if isinstance(str_lit,TerminalNodeImpl) else '""'
        return {'string': (body or '""')[1:-1]}

    def visitWrite_query_statement(self, ctx: HybLangParser.Write_query_statementContext):
        return {'write_query': self.visit(ctx.string_literal())}
    def aggregateResult(self, aggregate, nextResult):
        return nextResult
        return (aggregate or []) + [nextResult]

    def defaultResult(self):
        None

    pass


def file_to_ast_dict(file):
    input_stream = FileStream(file)
    lexer = HybLangLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = HybLangParser(stream)
    tree = parser.program()
    visitor = RawSyntaxTreeVisitor()
    ast = visitor.visit(tree)
    return ast
