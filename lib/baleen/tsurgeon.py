from subprocess import check_output, Popen, PIPE 
from tempfile import NamedTemporaryFile          
    
    

def edit_trees(trees, pattern, script, exec_path="tsurgeon.sh",
               encoding="utf-8"):
    """
    Edit trees by matching tree pattern and applying Tsurgeon script
    
    Parameters
    ----------
    trees: list of str
        list of input trees in LBS format
    pattern: str
        Tregex pattern
    script: str
        Tsurgeon script
    excec_path: str, optional
        path to tsurgeon.sh executable
    encoding: str, optional
        encoding during file IO 
        
    Returns
    -------
    result: list of str
        list of output trees in LBS format
    """
    trees_file = NamedTemporaryFile("w")
    trees_file.write("\n".join(trees))
    trees_file.flush()
    result = call_tsurgeon(trees_file.name, pattern, script,
                           exec_path=exec_path)
    return result.strip().split("\n")


def call_tsurgeon(trees_fname, pattern, script, options=["-s"], 
                  exec_path="tsurgeon.sh", encoding="utf-8"):
    cmd = [exec_path] + options + ["-treeFile", trees_fname,
                                   "-po", pattern, script]
    return check_output(cmd).decode(encoding)


