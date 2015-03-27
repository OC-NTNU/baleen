
from tredev.nodes import Nodes

def tree_yield(tree):
    # quick & dirty tree yield
    terms = [Nodes.unescape_brackets(part.rstrip(")")) 
             for part in tree.split() 
             if not part.startswith("(")]
    return " ".join(terms)
