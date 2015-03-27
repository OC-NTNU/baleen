"""
Trace transformation of matches
"""



def print_derivations(matches):
    """
    Print derivations showing transformation of original matches into
    transformed matches    
    
    Parameters
    ----------
    matches: pandas.DataFrame
        transformed matches    
    """
    def print_steps(index, indent=0):
        print(indent * " ", matches.at[index, "substr"]) 
        for i in matches.at[index, "descendants"] or []:
            print((indent + 4) * " ", "===", matches.at[i, "trans_name"], "===>")
            print_steps(i, indent + 8)
    
    # Select matches on top of derivations (exclude matches embedded in larger
    # derivations)
    indices = matches.index[~matches["descendants"].isnull() & 
                            matches["ancestor"].isnull()]
    
    for n, index in enumerate(indices):
        print(78 * "-")
        print(n+1, ":", matches.at[index, "label"], "(", index, ")")
        print(78 * "-")
        print_steps(index)
        print()