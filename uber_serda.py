#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import serda_data_sel as data_sel
# import serda_data_prep as data_prep


parser = argparse.ArgumentParser()
parser.add_argument('-c', '--clean', help = "Flag specifying whether you want to generate new directories. Default=False", action = 'store_true')
parser.add_argument('audio_zip', help = "Path to raw audio zip")
parser.add_argument('log_zip', help = "Path to raw log zip")
parser.add_argument('audio_path', help = "Path to audio processing and storing dir")
parser.add_argument('log_path', help = "Path to log processing and storing dir")
parser.add_argument('prompts_source', help = "Path to story prompts")
parser.add_argument('prompt_path', help = "Path to prompt processing and storing dir")
parser.add_argument('recs_to_ignore', help = "Location of a file specifying recordings to ignore")
args = parser.parse_args()

print("\n###\tSERDA v1 data processing\t###\n")

print("\n# Data selection  #\n")
full_dict = data_sel.gen_clean_dict(args.audio_zip, args.log_zip, args.audio_path, args.log_path, args.recs_to_ignore, args.clean)

# for rec_id, (audio, log) in list(full_dict.items())[:10]:
#     print(f"{rec_id}\n{audio}\n{log}\n")

print("\n# Data preparation #\n")

# TODO:
# import and call data_prep functions in this script directly, using full_dict as input

