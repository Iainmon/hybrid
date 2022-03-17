import sys
import os
import typing as ty

from .syntax import *
from .parser import source_to_ast_dict

from dataclasses import asdict as serialize_tree, fields
import dataclasses as dc

import graphviz as gv



def show_graph(g):
    g.render(filename=f'./graphs/tmp.gv',view=True)

def path(p):
    return os.path.join(os.getcwd(),p)

colors = {
    'scheme': 'spectral11',
    'lit': '4',
    'app': '8',
    'lam': '2'
}
def new_graph(title=None):
    graph_attr = {'rankdir': 'TD'}
    if not title is None:
        graph_attr['labelloc'] = 't'
        graph_attr['label']    = title
    return gv.Digraph(
        graph_attr=graph_attr,
        node_attr={ 'style': 'filled', 'shape': 'square', 'colorscheme': 'spectral11'}, # lightblue2
        edge_attr={'arrowhead': 'none'},
        format='png', # svg
        engine='dot'
    )

from dataclasses import Field, MISSING, _FIELDS, _FIELD, _FIELD_INITVAR  # type: ignore
from typing import Type, Any, TypeVar, List, Dict
Data = Dict[str, Any]
T = TypeVar("T", bound=Any)

def get_fields(data_class: Type[T]) -> List[Field]:
    fields = getattr(data_class, _FIELDS)
    return [f for f in fields.values() if f._field_type is _FIELD or f._field_type is _FIELD_INITVAR]


def get_name(instance):
    datacls = type(instance)
    if not dc.is_dataclass(datacls):
        raise TypeError(f"Expected dataclass instance, got '{datacls!r}' object")
    mod = sys.modules.get(datacls.__module__)
    if mod is None or not hasattr(mod, datacls.__qualname__):
        raise ValueError(f"Can't resolve '{datacls!r}' reference")
    return datacls.__qualname__


def construct_ast_graph(ast : AST,d=0):
    graph = new_graph()# gv.Graph()

    def construct_graphviz_graph(tree,par_idx = None):
        print(par_idx)
        print(tree)
        
        par_name = str(tree) if not dc.is_dataclass(tree) else get_name(tree) # list(tree.as_dict().keys())[0]
        par_idx = str(tree) if not (type(par_idx) is str and par_idx != '') else par_idx
        graph.node(par_idx, label=par_name, shape='circle', color='8')
        
        if not dc.is_dataclass(tree):
            return None

        for c in tree.children():
            if type(c) is list:
                for c_ in c:
                    construct_graphviz_graph(c_,par_idx)
            else:
                child_idx = str(c)
                construct_graphviz_graph(c,child_idx)
                graph.edge(par_idx,child_idx)
        return None
    serialized = ast.as_dict(named_args=True)
    # print(serialized)
    construct_graphviz_graph(ast,None)
    show_graph(graph)

    # # node = gd.node(d, label=str(ast), shape='square', color='8')
    
print('-------------------------')
parse_tree = source_to_ast_dict('rout a() : {return 1;}')
print(parse_tree)
print('-------------------------')
ast = construct_ast(parse_tree)
print(ast)
print('-------------------------')
ast_dict = serialize_tree(ast)
print(ast_dict)
print('-------------------------')
construct_ast_graph(ast)


def lambdagraph(g: gv.Graph,ast: AST):
    nodes = []
    edges = []
    to_connect = []
    next_node_id = 0
    nodes_to_visit = [expr]
    while len(nodes_to_visit) > 0:
        curr = nodes_to_visit.pop(0)
        typ  = curr[0]
        if not len(to_connect) < 1:
            edge = (to_connect.pop(0), str(next_node_id))
            edges.append(edge)
        if typ == 'App':
            node = g.node(str(next_node_id), label='App', shape='square', color='8')
            nodes.append(node)
            nodes_to_visit.append(curr[1]) # left
            nodes_to_visit.append(curr[2]) # right
            to_connect.append(str(next_node_id))
            to_connect.append(str(next_node_id))
        elif typ == 'Lit':
            node = g.node(str(next_node_id), label=curr[1], shape='circle', color='4')
        elif typ == 'Abs':
            node = g.node(str(next_node_id), label='λ'+curr[1], shape='doublecircle', color='2')
            nodes.append(node)
            nodes_to_visit.append(curr[2]) # body
            to_connect.append(str(next_node_id))
        else:
            break
        next_node_id += 1
    for e in edges:
        g.edge(e[0],e[1])
    return g



# node = g.node(str(next_node_id), label='App', shape='square', color='8')
# node = g.node(str(next_node_id), label=curr[1], shape='circle', color='4')
# node = g.node(str(next_node_id), label='λ'+curr[1], shape='doublecircle', color='2')



def save(g,name='graph'):
    g.render(filename=f'./graphs/{name}.gv',view=False)
    try:
        try:
            os.remove(path(f'./graphs/{name}.png'))
        except BaseException:
            t = None
        os.rename(path(f'./graphs/{name}.gv.png'), path(f'./graphs/{name}.png'))
        os.remove(path(f'./graphs/{name}.gv'))
    except BaseException:
        print('Saved to: ', path(f'./graphs/{name}.png'))
        exit()
