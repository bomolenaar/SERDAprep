#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import shutil
from subprocess import run, PIPE, check_output
import pathlib
import ast

if len(sys.argv) < 7:
    print(f"You must add 6 arguments:\n1) Audio path\n2) Logs path\n"
    "3) A directory to process & place audio\n4) A directory to process & place logs\n"
    "5) Story prompts path\n6) A directory to process & place prompts")
    sys.exit(-1)

audio_zip = sys.argv[1]
log_zip = sys.argv[2]
audio_path = os.path.join(os.getcwd(), sys.argv[3])
log_path = os.path.join(os.getcwd(), sys.argv[4])
prompts_source = os.path.join(os.getcwd(), sys.argv[5])
prompt_path = os.path.join(os.getcwd(), sys.argv[6])


sel_cmd = f"python3 scripts/serda_data_sel.py {audio_zip} {log_zip} {audio_path} {log_path} {prompts_source}"
prep_cmd = f"python3 scripts/serda_data_prep.py {audio_path} {log_path} {prompts_source} {prompt_path}"

print("Gathering data...")
full_dict = ast.literal_eval(check_output(sel_cmd, shell=True, text=True))

for key, value in full_dict.items()[:10]:
    print(key, value)

# TODO:
# need to pass the dict from data_sel as an arg to data_prep,
# but python items (like a dict) cannot be passed to command line
# so preferably we import and call data_prep functions in this script directly to avoid that problem
# or !! better we import and call data_sel functions in data_prep!!!
