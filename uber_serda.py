#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import argparse
import serda_data_sel as data_sel
import serda_data_prep as data_prep


parser = argparse.ArgumentParser()
parser.add_argument('--clean', help = "Flag specifying whether you want to generate new directories. Default=False", action = 'store_true', required=False)
parser.add_argument('-a', '--audiozip', required='--clean' in sys.argv, help = "Path to raw audio zip. Required when using --clean.")
parser.add_argument('-l', '--logzip', required='--clean' in sys.argv, help = "Path to raw log zip. Required when using --clean")
parser.add_argument('audio_path', help = "Path to audio processing and storing dir")
parser.add_argument('log_path', help = "Path to log processing and storing dir")
parser.add_argument('prompts_source', help = "Path to story prompts")
parser.add_argument('prompt_path', help = "Path to prompt processing and storing dir")
parser.add_argument('recs_to_ignore', help = "Location of a file specifying recordings to ignore")
parser.add_argument('stories_AO_source', help = "Path to ASR output for story task recs")
# parser.add_argument('words_AO_source', help = "Path to ASR output for word task recs")

args = parser.parse_args()
print(vars(args))


if args.clean and (args.audiozip is None or args.logzip is None):
    parser.error("--clean requires --audiozip and --logzip.")

print("\n###\tSERDA v1 data processing\t###\n")

print("\n# 1. Data selection  #\n")
print("Creating dict of selected data...")
if args.clean:
    full_dict = data_sel.gen_clean_dict(args.audio_path, args.log_path, args.recs_to_ignore, args.clean, args.audio_zip, args.log_zip)
else:
    full_dict = data_sel.gen_clean_dict(args.audio_path, args.log_path, args.recs_to_ignore, args.clean)
print("Done.")

print("\n# 2. Data preparation #\n")
print("Segmenting data and matching prompts...")
data_prep.prepare_data(args.clean, full_dict, args.audio_path, args.log_path, args.prompts_source, args.prompt_path, args.stories_AO_source)#, args.words_AO_source)
print("Done.")

print("\n# Finished preparing data #\n")
