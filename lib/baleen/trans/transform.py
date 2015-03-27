#!/usr/bin/env jython

"""
Apply tree transformations to matches

Requires:
- Jython 2.7 from http://www.jython.org/
- stanford-tregex.jar in Stanford Tregex package 
  from http://nlp.stanford.edu/software/tregex.shtml 
"""

import re
import sys
import pickle
from collections import OrderedDict, namedtuple
import logging


hint = """
Probably Jython can not find the Java library stanford-tregex.jar
Either set/prepend the environment variable JYTHONPATH like

  JYTHONPATH=/path/to/stanford-tregex.jar

or in your code extend the system path like

  import sys
  sys.path.append("/path/to/stanford-tregex.jar")
"""

try:
    from edu.stanford.nlp.trees import Tree
    from edu.stanford.nlp.trees.tregex import TregexPattern
    from edu.stanford.nlp.trees.tregex.tsurgeon import Tsurgeon
    from edu.stanford.nlp.ling import Sentence
except ImportError as error:
    print error
    sys.exit(hint)


    
# Prefix "sc_" indicates a Java object from Stanford CoreNLP, e.g. sc_tree is
# a edu.stanford.nlp.trees.Tree object

    

Tuple = namedtuple("Tuple", ["ancestor",   # index of ancestor match
                             "name",       # name of transformation
                             "subtree"     # subtree as Java Tree object
                             ])



def transform_matches(tuples, transforms, tuples_fname=None):
    if isinstance(tuples, str):
        tuples = read_tuples(tuples)        
        
    if isinstance(transforms, str):
        transforms = read_transformations(transforms)
        
    max_index = max(tuples.keys())
    
    for name, (pattern, operation) in transforms.items():
        sc_pattern = TregexPattern.compile(pattern)
        sc_operation = Tsurgeon.parseOperation(operation) 
        max_index = apply_transform(name, sc_pattern, sc_operation, tuples,
                                    max_index)
        
    if tuples_fname:
        write_tuples(tuples, tuples_fname)
        

def read_tuples(fname):
    tuples = {}
    
    for (index, ancestor, name, lbs_tree) in pickle.load(open(fname, "rb")):
        sc_tree = Tree.valueOf(lbs_tree)
        # if instantiation of Tree class fails for ill-formed trees, 
        # sc_tree is None
        if sc_tree:
            tuples[index] = Tuple(ancestor, name, sc_tree)

    return tuples
        

def read_transformations(fname):
    # FIXME: horrible one-liners 

    # first remove all comments starting with %
    content = "\n".join(line.split("%", 1)[0].strip()
                        for line in open(fname)).strip()

    # find parts separated by at least two newlines 
    parts = [p.replace("\n", " ") for p in re.split(r"[\n]{2,}", content)]

    # create an ordered dict with name as key and [pattern, operation] as
    # value
    return OrderedDict( (parts[i].lstrip(" #"), parts[i+1: i+3])
                        for i in range(0, len(parts), 3) )


def apply_transform(name, sc_pattern, sc_operation, tuples, max_index):
    # FIXME: exhaustive application by reapplying same transformation on
    # only the trees it generated
    
    # Copy input trees first because tsurgeon operations are destructive
    transformed_trees = [t.subtree.deepCopy() for t in tuples.values()]

    Tsurgeon.processPatternOnTrees(sc_pattern, sc_operation,
                                   transformed_trees)
    
    for trans_tree, ancestor_index in zip(transformed_trees, tuples):
        # Trimmed trees are obtained by parsing the labeled bracket string
        # using Tree.valueOf. Among other things, this flattens the tree.
        # E.g. (NP (NP x)) becomes (NP x). In order to compare trimmed trees
        # to Tsurgeon output, the latter trees must be normalized as well.
        trans_tree = Tree.valueOf(trans_tree.toString())
        ancestor_tree = tuples[ancestor_index].subtree

        if trans_tree != ancestor_tree:
            max_index += 1
            tuples[max_index] = Tuple(ancestor_index, name, trans_tree)
            
    return max_index


def write_tuples(sc_tuples, fname):
    lbs_tuples = [ (index, tup.ancestor, tup.name, Tree.toString(tup.subtree))
                   for index, tup in sc_tuples.items() ]
    pickle.dump(lbs_tuples, open(fname, "wb"))

    
def report(tuples):
    for index, tup in tuples.items():
        if tup.name:
            ancestor_tree = tuples[tup.ancestor].subtree
            print tup.name, ":"
            print tup.ancestor, ":", 
            print Sentence.listToString(ancestor_tree.yield())
            print "==>"
            print index, ":", Sentence.listToString(tup.subtree.yield())
            print
            
                        


if __name__ == "__main__":    
    import sys
    
    if len(sys.argv) == 4:
        transform_matches(*sys.argv[1:4])
    else:
        sys.exit("Usage: transform.py original-tuples-file "
                 "transformations-file transformed-tuples-file")
    
    
    

    