#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import shutil
import pandas as pd
from subprocess import run, PIPE
import re
import pathlib

""""
@Author:        Bo Molenaar
@Date:          1 February 2023

@Last edited:    13 March 2023

This script takes SERDA v1 audio and log files and sorts them on task.
The audio files are .webm format, so ffmpeg is called to convert them into .wav (maintaining 32-bit encoding)
Log files are matched to the corresponding audio file in a dict.
Audio files for story tasks with duration > 3 minutes are trimmed to 3 minutes.
Audio files for word tasks are split on single words with added word ID tag.
"""


if len(sys.argv) < 5:
    print(f"You must add 4 arguments:\n1) Audio path\n2) Logs path\n3) Story prompts path\n"
    "4) Directory to place prompts")
    # TODO:
    # add expected extensions for the different files
    sys.exit(-1)

audio_path = os.path.join(os.getcwd(), sys.argv[1])
log_path = os.path.join(os.getcwd(), sys.argv[2])
prompts_source = os.path.join(os.getcwd(), sys.argv[3])
prompt_path = os.path.join(os.getcwd(), sys.argv[4])

words_dir = "words"
stories_dir = "stories"
long_stories_dir = "long_stories"
segments_dir = "words/segments"

audio_words_path = os.path.join(audio_path, words_dir, "full")
audio_stories_path = os.path.join(audio_path, stories_dir)
log_words_path = os.path.join(log_path, words_dir)
log_stories_path = os.path.join(log_path, stories_dir)
prompt_words_path = os.path.join(prompt_path, words_dir)
prompt_stories_path = os.path.join(prompt_path, stories_dir)

words_segments_path = os.path.join(audio_path, segments_dir)

#  remove working directories for audio and logs and create fresh ones
dir_lst = [audio_words_path, audio_stories_path,
        log_words_path, log_stories_path,
        prompt_words_path, prompt_stories_path]
for mydir in dir_lst:
    pathlib.Path(mydir).mkdir(parents=True, exist_ok=True)


def create_word_segments(rec_path, words_dict):
    """
    Takes a dict for 1 word task with items 'prompt_id': ('prompt_id', 'segment_start', 'segment_end').
    Then recalculates start time as word appearance (= prev word end + 1323ms).
    Finally the timestamps are used to create an audio file for each segment.
    """
    for prompt_id, (start_time, end_time) in words_dict:
        segment_path = f"{rec_path[:-4]}_{prompt_id}.wav"
        
        # TODO:
        # figure out how to get an accurate start timestamp for the first word

        # the plan is to make an exception case for the first word, where two files are generated
        # one file starts from the beginning of the recording
        # the other file starts from the first word start click event

        soxcommand = f"sox {rec_path} {segment_path} trim {start_time} ={end_time} pad 0.3 0.3"
        run(soxcommand, check=True, shell=True)

# TODO:
# import functions from data_sel to be able to generate the dict in place
# then call the functions here

full_dict = {}

for rec_id, (audio, log) in full_dict.items():
    # handle story tasks
    if "story" in rec_id:      
        # generate prompt file
        storynum = rec_id.split("-")[1].replace("_", "")
        prompt = ""
        infile = os.path.join(prompts_source, f"{storynum}_cut.txt")
        outfile = os.path.join(prompt_stories_path, f"{rec_id}.prompt")
        with open(infile, "r", encoding="utf-8") as prompt_in, open(outfile, "w", encoding="utf-8") as prompt_out:
            for line in prompt_in.readlines():
                prompt += line
            prompt_out.write(prompt)

    # handle word tasks
    # el
    if "H2S4W-words" in rec_id:
        word_segments = {}
        # load logfile to get the word timestamps
        # INFO:
        # there are 1323ms between end of last word and first appearance of next word
        log_data = pd.read_csv(log, delimiter=";", index_col="user_id")
        for speaker_id, row in log_data.iterrows():
            word_segments[row['prompt_id']] = (row['start_speak'], row['stop_speak'])
            prompt = str(row['prompt'])
            prompt_id = row['prompt_id']
            outfile = os.path.join(prompt_words_path, f"{rec_id}_{prompt_id}.prompt")
            with open(outfile, "w", encoding="utf-8") as prompt_out:
                prompt_out.write(prompt)


        # create_word_segments(audio, word_segments)

# for item in sorted(word_segments.items())[:10]:
#     print(item)

