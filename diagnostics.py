#!/usr/bin/python3
# -*- coding: utf-8 -*-

""""
@Author:        Bo Molenaar
@Date:          5 April 2023

@Last edited:    12 April 2023

This script takes ASR output aligned with prompts 
for a collection of SERDA oral reading task data 
and wrangles it into two output files:
1. speaker level binary correctness judgements by ASR for each word
2. speaker level reading time for each word
"""

import os
import argparse
import json
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('asr_dir',
                    help = "The directory where your ASR transcriptions are located.")
parser.add_argument('log_dir',
                    help = "The directory where the reading prompts are located.")
parser.add_argument('adaptfile',
                    help = "File containing ADAPT alignments of your ASR transcriptions"
                    "and reading prompts.")
parser.add_argument('correct_outfile',
                    help = "File to write ASR correctness judgements to.")
parser.add_argument('speed_outfile',
                    help = "File to write reading speed values to.")
args = parser.parse_args()
ALIGNMENTS = args.adaptfile
AO_DIR = args.asr_dir
LOGS_DIR = args.log_dir
COR_OUT = args.correct_outfile
SPEED_OUT = args.speed_outfile

def diagnose_correctness(alignments, outfile):
    """
    get automatic accuracy diagnostics for pairs of ASR output and reading prompts, using their ADAPT alignments
    """
    df = pd.read_excel(alignments).set_index('wav_id')
    full_data = []

    for wav_id, row in df.iterrows():    # elicit the information we want into a dict with wav_id as keys
        correct = row['correct']

        # break up wav_id into all idenfication components it contains
        id_comps = str(wav_id).split('-')
        spk_id, item_specifier = id_comps[0], id_comps[1]
        # task_comps = task_specifier.split('_')
        # task_type = task_comps[0]
        # task_id = task_comps[:1]
        # prompt_id = task_comps[:-1]

        # now we make a list of tuples that includes item ID, speaker ID and correct
        # using wav_id to get unique combinations
        full_data.append((item_specifier, spk_id, correct))
    
    # some pandas magic
    # load tuples as columns
    df2 = pd.DataFrame(full_data, columns=['Item ID', 'Speaker ID', 'Correct'])
    # now use pivot to set tuple columns to index, columns and values :)
    df_final = df2.pivot(index='Item ID', columns='Speaker ID', values='Correct')

    df_final.to_csv(outfile)

def diagnose_speed(ao_dir, log_dir, outfile):
    """
    get automatic speed diagnostics for pairs of ASR output and reading prompts, using SERDA logs and ASR timestamps
    """
    # collect log files in a list and dict
    log_filelist = []
    log_files = {}
    for dirpath, dirnames, filenames in os.walk(log_dir):
        for filename in filenames:
            if filename.endswith(".csv"):
                log_filelist.append(filename)
                rec_id = filename.split('.')[0]
                log_files[rec_id] = os.path.join(dirpath, filename)
    
    # collect asr output files in a list and dict
    ao_filelist = []
    ao_files = {}
    for dirpath, dirnames, filenames in os.walk(ao_dir):
        for filename in filenames:
            if filename.endswith(".json"):
                if 'whisperx' in ao_dir:  # specifically get timestamped files for whisperX
                    if 'timestamps' not in filename:
                        continue
                else:
                    ao_filelist.append(filename)
                    rec_id = filename.split(".")[0]
                    ao_files[rec_id] = os.path.join(dirpath, filename)

    full_data = []
    for rec_id, log_file in log_files.items():
        timestamps = {}

        # TODO get timestamps from log for words 1-50
        log_data = pd.read_csv(log_file, delimiter=";", index_col="user_id")
        for speaker_id, row in log_data.iterrows():
            prompt_id = row['prompt_id']
            start_time_log = row['start_speak']/1000
            end_time_log = row['stop_speak']/1000

        # TODO get timestamps from ASR for words 1-50
        # TODO exception case for whisperX because the timestamped files have different structure
        # following works for regular .json (whisperT)
        ao_file = ""
        with open(ao_file, 'r', encoding='utf-8') as ao_in:
            ao = json.load(ao_in)
            # subtract 0.3 seconds from first timestamp because there is 0.3s silence buffer around asr input audio
            start_time_ao = min(ao['segments'][0]['start']-0.3, 0)

        # TODO calculate time between word appearance and start speaking (either button press or asr timestamp, which ever is sooner)
    
    # then construct a dataframe similar to diagnose_correctness
    mylist = []
    for wav_id, row in enumerate(mylist):    # elicit the information we want into a dict with wav_id as keys
        
        speed = ""

        # break up wav_id into all idenfication components it contains
        id_comps = str(wav_id).split('-')
        spk_id, item_specifier = id_comps[0], id_comps[1]
        # task_comps = task_specifier.split('_')
        # task_type = task_comps[0]
        # task_id = task_comps[:1]
        # prompt_id = task_comps[:-1]

        # now we make a list of tuples that includes item ID, speaker ID and correct
        # using wav_id to get unique combinations
        full_data.append((item_specifier, spk_id, speed))
    
    # some pandas magic
    # load tuples as columns
    df2 = pd.DataFrame(full_data, columns=['Item ID', 'Speaker ID', 'Reading time'])
    # now use pivot to set tuple columns to index, columns and values :)
    df_final = df2.pivot(index='Item ID', columns='Speaker ID', values='Reading time')

    df_final.to_csv(outfile)

# diagnose_correctness(ALIGNMENTS, COR_OUT)
diagnose_speed(AO_DIR, LOGS_DIR, SPEED_OUT)
