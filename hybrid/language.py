from .syntax import *



def definition_libraries(ast) -> list[LibraryDefinition]:
    if isinstance(ast,list):
        return [l for l in ast if isinstance(l,LibraryDefinition)]
    if isinstance(ast,Block):
        return [l for l in ast.procedure if isinstance(l,LibraryDefinition)]
    return []

def definition_calling_programs(ast) -> list[CallingProgramDefinition]:
    if isinstance(ast,list):
        return [p for p in ast if isinstance(p,CallingProgramDefinition)]
    if isinstance(ast,Block):
        return [p for p in ast.procedure if isinstance(p,CallingProgramDefinition)]
    return []