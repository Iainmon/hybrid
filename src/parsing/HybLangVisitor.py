# Generated from HybLang.g4 by ANTLR 4.9.3
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .HybLangParser import HybLangParser
else:
    from HybLangParser import HybLangParser

# This class defines a complete generic visitor for a parse tree produced by HybLangParser.

class HybLangVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by HybLangParser#program.
    def visitProgram(self, ctx:HybLangParser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by HybLangParser#bin_op.
    def visitBin_op(self, ctx:HybLangParser.Bin_opContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by HybLangParser#identifier.
    def visitIdentifier(self, ctx:HybLangParser.IdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by HybLangParser#function_call.
    def visitFunction_call(self, ctx:HybLangParser.Function_callContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by HybLangParser#expression.
    def visitExpression(self, ctx:HybLangParser.ExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by HybLangParser#assignment.
    def visitAssignment(self, ctx:HybLangParser.AssignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by HybLangParser#sample.
    def visitSample(self, ctx:HybLangParser.SampleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by HybLangParser#return_stmt.
    def visitReturn_stmt(self, ctx:HybLangParser.Return_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by HybLangParser#statement.
    def visitStatement(self, ctx:HybLangParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by HybLangParser#procedure.
    def visitProcedure(self, ctx:HybLangParser.ProcedureContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by HybLangParser#non_statement.
    def visitNon_statement(self, ctx:HybLangParser.Non_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by HybLangParser#set_lit.
    def visitSet_lit(self, ctx:HybLangParser.Set_litContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by HybLangParser#set_type.
    def visitSet_type(self, ctx:HybLangParser.Set_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by HybLangParser#function_argument.
    def visitFunction_argument(self, ctx:HybLangParser.Function_argumentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by HybLangParser#function_arguments.
    def visitFunction_arguments(self, ctx:HybLangParser.Function_argumentsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by HybLangParser#function_def.
    def visitFunction_def(self, ctx:HybLangParser.Function_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by HybLangParser#block.
    def visitBlock(self, ctx:HybLangParser.BlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by HybLangParser#if_stmt.
    def visitIf_stmt(self, ctx:HybLangParser.If_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by HybLangParser#call_prog_def.
    def visitCall_prog_def(self, ctx:HybLangParser.Call_prog_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by HybLangParser#exposing_sequence.
    def visitExposing_sequence(self, ctx:HybLangParser.Exposing_sequenceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by HybLangParser#library_def.
    def visitLibrary_def(self, ctx:HybLangParser.Library_defContext):
        return self.visitChildren(ctx)



del HybLangParser