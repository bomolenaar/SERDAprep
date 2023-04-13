#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import shutil
import time
import serda_data_sel as data_sel
import serda_data_prep as data_prep


t = time.process_time()

parser = argparse.ArgumentParser()
parser.add_argument('--clean', action = 'store_true', required=False,
                    help = "Flag specifying whether you want to generate new directories."
                    " When True, script will delete everything under project_dir"
                    " and generate new directories and files starting from audio zip and logs zip."
                    " When False, will leave files as is"
                    " and only collect their paths for data preparation steps."
                    " Default=False")
parser.add_argument('-a', '--audiozip', required='--clean' in sys.argv,
                    help = "Path to raw audio zip. Required when using --clean.")
parser.add_argument('-l', '--logzip', required='--clean' in sys.argv,
                    help = "Path to raw log zip. Required when using --clean.")
parser.add_argument('project_dir',
                    help = "Parent project directory where you want to process and store audio, logs, prompts and ASR transcriptions.")
parser.add_argument('audio_dir',
                    help = "Path to audio processing and storing dir. A subdirectory of project_dir."
                    "Default = 'audio'", default = 'audio')
parser.add_argument('log_dir',
                    help = "Path to log processing and storing dir. A subdirectory of project_dir."
                    "Default = 'logs'", default = 'logs')
parser.add_argument('prompt_dir',
                    help = "Path to prompt processing and storing dir. A subdirectory of project_dir."
                    "Default = 'prompts'", default= 'prompts')
parser.add_argument('raw_prompts',
                    help = "Path to story prompts."
                    " Expected prompt files are 1 sentence per line and filenames are story{1/2/3}_clean.txt")
parser.add_argument('recs_to_ignore',
                    help = "Location of a .txt file specifying recordings to ignore."
                    " Each line should contain the ID of one recording (! not a path)."
                    " E.g. AB123-story_1-20230101090012345")

args = parser.parse_args()
if args.clean and (args.audiozip is None or args.logzip is None):
    parser.error("--clean requires -a/--audiozip and -l/--logzip.")

audio_path = os.path.join(args.project_dir, args.audio_dir)
logs_path = os.path.join(args.project_dir, args.log_dir)
prompts_path = os.path.join(args.project_dir, args.prompt_dir)

print("\n###\tSERDA v1 data processing\t###\n")

# remove project folder and audio, logs and prompts subfolders if they already exist
for mydir in [args.project_dir, args.audio_dir, args.log_dir, args.prompt_dir]:
    if args.clean and os.path.isdir(mydir):
        print("Creating new project dir...")
        shutil.rmtree(mydir)
        os.mkdir(mydir)
    
print("\n# 1. Data selection  #\n")
print("Creating dict of selected data...")
if args.clean:
    full_dict = data_sel.gen_clean_dict(audio_path, logs_path, args.recs_to_ignore, args.clean, args.audiozip, args.logzip)
else:
    full_dict = data_sel.gen_clean_dict(audio_path, logs_path, args.recs_to_ignore, args.clean)
print("Done.")

print("\n# 2. Data preparation #\n")
print("Segmenting data and matching prompts...")
data_prep.prepare_data(args.clean, full_dict, audio_path, logs_path, args.raw_prompts, prompts_path)
print("Done.")

print("\n# Finished preparing data #\n")

elapsed_time = time.process_time() - t
print(f"Elapsed time: {elapsed_time} s")

print("\nPlease prepare a folder with ASR output for story tasks in"
      f" {os.path.join(args.project_dir, 'asr')}, so you can run segment_stories.py")
