"""
Wrapper for transformation of matches  
"""

import os
import pickle
import subprocess
import sys
import tempfile

import pandas as pd

from baleen.utils import tree_yield



def transform_matches(org_matches, transform_fname,
                      trans_matches_fname=None, jython_exec="jython", 
                      jython_path=None):
    """
    Transform matches by applying tree transformations
    
    Parameters
    ----------
    org_matches: pandas.DataFrame or str
        original matches or name of file with pickled original matches
    transform_fname: str
        name of file with definitions of tree transformations
    trans_matches_fname: str
        name of file for outputting transformed matches
    jython_exec: str
        path to Jython executable
    jython_path: str
        value assigned to JYTHONPATH environment variable 
        
    Returns
    -------
    merged_matches: pandas.DataFrame
        original matches merged with transformed matches
    
    """
    # ------------------------------------------------------------------------
    # STEP 1: Export original matches to tuples
    # ------------------------------------------------------------------------
    if isinstance(org_matches, str): 
        org_matches = pd.read_pickle(org_matches)
    org_tuples_file = tempfile.NamedTemporaryFile()
    export_to_tuples(org_matches, org_tuples_file.name)
    
    # ------------------------------------------------------------------------
    # STEP 2: Transform matches by spawning Jython script
    # ------------------------------------------------------------------------
    trans_tuples_file = tempfile.NamedTemporaryFile()     
        
    # get file path to current module (i.e. baleen.trans.wrap)
    path = sys.modules[__name__].__file__
    # and deduce file path to the Jython script in the same directory 
    script_fname = os.path.join(os.path.split(path)[0], 
                                "transform.py") 
    
    args = [jython_exec, script_fname, 
            org_tuples_file.name, transform_fname, trans_tuples_file.name]
    
    # if given, set JYTHONPATH env var, otherwise assume it is set
    if jython_path:
        os.environ["JYTHONPATH"] = jython_path    
        
    subprocess.check_output(args)
    
    # ------------------------------------------------------------------------
    # STEP 3: Import transformed matches from tuples       
    # ------------------------------------------------------------------------
    trans_matches = import_from_tuples(trans_tuples_file.name)
    
    # ------------------------------------------------------------------------
    # STEP 4: Import transformed matches from tuples       
    # ------------------------------------------------------------------------
    merged_matches = merge_matches(org_matches, trans_matches)
    
    if trans_matches_fname:
        pd.to_pickle(merged_matches, trans_matches_fname)
        
    return merged_matches
    
    





#==============================================================================
# Bridging between CPython and JPython.
#==============================================================================

# Export to/import from pickled tuples is required because Jython does not
# support Pandas and thus can not read a DataFrame


# Columns which are exported to/imported from tuples

COLUMNS = ["index",           # index of transformed match (i.e. its own index)
           "ancestor",        # index of ancestor match
           "trans_name",      # name of transformation
           "subtree"          # subtree as labeled-brackets string 
           ]


def export_to_tuples(matches, tuples_fname):
    """
    Export selected columns from matches to tuples
    
    Parameters
    ----------
    matches: pandas.DataFrame instance
        originally extracted matches with columns "index" and "subtree"
    tuples_fname: str
        filename for writing pickled tuples 
    """
    subset = matches[["subtree"]]
    subset["ancestor"] = None
    subset["trans_name"] = None
    subset.reset_index(inplace=True)
    # rearrange columns
    subset = subset[COLUMNS]
    tuples = [tuple(r) for r in subset.values]
    # force protocol 2, because Jython is at python2 and thus cannot handle
    # higher protocols
    pickle.dump(tuples, open(tuples_fname, "wb"), protocol=2)
    
    
def import_from_tuples(tuples_fname):
    """
    Import selected columns from tuples to matches
    
    Parameters
    ----------
    tuples_fname: str
        filename for reading pickled tuples 
    
    Returns
    -------
    trans_matches: pandas.DataFrame instance
        transformed matches
    """
    tuples = pickle.load(open(tuples_fname, "rb"))
    trans_matches = pd.DataFrame(tuples, columns=COLUMNS)
    trans_matches.set_index("index", inplace=True)
    return trans_matches


def merge_matches(org_matches, trans_matches):
    """
    Merge original and transformed matches
    
    Parameters
    ----------
    org_matches: pandas.DataFrame
        originally extracted matches
    trans_matches: pandas.DataFrame
        transformed matches resulting from import_from_tuples
    
    Returns
    -------
    merged_matches: pandas.DataFrame
    """
    # Remove column 'subtree' from original matches, because its values are
    # included in the columns 'subtree' from the transformed matches
    org_matches = org_matches.drop("subtree", axis=1)
    # Now join on the indices. The indices of transformed matches contain
    # almost all of the indices of original mathes, except for those that
    # were dropped during pruning because of ill-formed trees.
    merged_matches = trans_matches.join(org_matches)
    # Add a new columns for tracking descendants
    merged_matches["descendants"] = None
    
    # Get indices of transformed matches
    indices = merged_matches.index[merged_matches["file"].isnull()]
    # Columns to copy from ancestor to descendant
    columns = ["pat_name", "label", "file", "rel_tree_n", "node_n"]
    
    # Now iterate over all transformed matches 
    for i in indices:        
        # Get ancenstor index
        j = int(merged_matches.at[i, 'ancestor'])
        
        # Copy info from ancestor to descendant        
        merged_matches.loc[i, columns] = merged_matches.loc[j, columns]
        
        # Derive substring from subtree
        merged_matches.at[i, "substr"] = tree_yield(
            merged_matches.at[i, "subtree"])
        
        # Add current index to list of descendants of ancestor
        try:
            merged_matches.loc[j, "descendants"].append(i)
        except AttributeError:
            merged_matches.loc[j, "descendants"] = [i]
            
    # rearrange columns
    columns = ['pat_name', 'label', 'file', 'rel_tree_n', 'node_n',
               'subtree', 'substr', 'trans_name', 'ancestor', 'descendants']
    return merged_matches[columns]
        

    
    
    
