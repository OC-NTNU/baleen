from configparser import ConfigParser

from baleen.tsurgeon import edit_trees
from baleen.utils import tree_yield


def post_process(matches, rules_fname):
    target_to_rules = read_postproc_rules(rules_fname)
    
    for target, rules in target_to_rules.items():
        selection = matches["pat_name"] == target
        subtrees = matches["subtree"][selection]
        
        for rule in rules:
            subtrees = edit_trees(subtrees, rule["pattern"], rule["script"])
            matches["subtree"][selection] = subtrees
            matches["substr"][selection] = subtrees_to_substrings(subtrees)
        

def read_postproc_rules(rules_fname):
    
    rules = ConfigParser()
    rules.read(rules_fname)
    
    target_to_rules = {}
    
    for rule_name in rules.sections():
        rule = rules[rule_name]
        targets = [target.strip() 
                   for target in rule.get("targets").split(",")]
        
        for target in targets:
            try:
                target_to_rules[target].append(rule)
            except KeyError:
                target_to_rules[target] = [rule] 
                
    return target_to_rules
    
        
def subtrees_to_substrings(subtrees):
    return [tree_yield(subtree) for subtree in subtrees]
