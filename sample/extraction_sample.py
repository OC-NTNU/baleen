#!/usr/bin/env python3

"""
Extraction sample

Note: run setup_sample.py first to create data files
"""

from tredev import Tredev

from baleen.extract import Matches
from baleen.postproc import post_process

from setup_sample import path_prefix, parse_dir


# load data files
td = Tredev.load(path_prefix, parse_dir)

# extract
matches = Matches.from_patterns(td.patterns, td.nodes, parse_dir)

# post-process
post_process(matches, "post_proc_rules")

print(matches)





