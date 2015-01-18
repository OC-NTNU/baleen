from glob import glob
from os.path import basename

import pandas as pd

from tredev.tregex import get_matches



class Matches(pd.DataFrame):

    fields = ["pat_name", "label", "file", "rel_tree_n", "node_n", "subtree", "substr"]
    
    @classmethod
    def from_patterns(cls, patterns, nodes, file_path, 
                      tree_info=None, exec_path="tregex.sh"):
        """
        Collect the subtrees/substrings matching the given patterns
        
        Parameters
        ----------
        patterns: tredev.patterns.Patterns instance
            tree matching patterns
        nodes: tredev.nodes.Nodes instance
            nodes 
        file_path: str
            directory containing tree files
        tree_info: dict, optional
            precomputed info on relative tree numbers and original filename;
            see Matches.get_tree_info
        exec_path: str, optional
            path to tregex.sh executable
            
        Returns
        -------
        Matches instance
            table of matching subtrees/substrings 
        """
        if not tree_info:
            tree_info = cls.get_tree_info(file_path)
            
        records = []  
        
        for index, row in patterns.iterrows(): 
            matches = get_matches(row["pattern"], file_path, exec_path=exec_path)
            
            for abs_tree_n, node_n in matches:  
                node_id = nodes.get_node_id(abs_tree_n, node_n) 
                rel_tree_n, fname = tree_info[abs_tree_n]
                records.append((index, 
                                row["label"], 
                                fname,
                                rel_tree_n, 
                                node_n, 
                                nodes.get_subtree(node_id), 
                                nodes.get_substring(node_id)))
            
        return pd.DataFrame(records, columns=cls.fields)
        
    @classmethod   
    def get_tree_info(cls, file_path):
        """
        For each tree from the tree files in directory file_path, map its
        absolute tree number to its relative tree number and its filename.
        """
        tree_info = {}
        # absolute tree number, counting from 1
        abs_tree_n = 0
        
        for fname in glob(file_path + "/*"):
            base_fname = basename(fname)
            # relative tree number, restarting at 1 for every new file
            rel_tree_n = 0
            
            for _ in open(fname):
                abs_tree_n += 1
                rel_tree_n += 1
                tree_info[abs_tree_n] = rel_tree_n, base_fname
                
        return tree_info
    