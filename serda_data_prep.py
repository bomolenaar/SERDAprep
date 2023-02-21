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

@Last edited:    17 February 2023

This script takes SERDA v1 audio and log files and sorts them on task.
The audio files are .webm format, so ffmpeg is called to convert them into .wav (maintaining 32-bit encoding)
Log files are matched to the corresponding audio file in a dict.
Audio files for story tasks with duration > 3 minutes are trimmed to 3 minutes.
Audio files for word tasks are split on single words with added word ID tag.
"""


if len(sys.argv) < 7:
    print("You must add five arguments:\n1) A path to the location of the audio\n2) A path to the location of the logs\n"
    "3) A directory to process audio\n4) A directory to process logs\n5) A path to the location of story prompts\n"
    "6) A directory to place prompts")
    # TODO:
    # add expected extensions for the different files
    sys.exit(-1)

audio_zip = sys.argv[1]
log_zip = sys.argv[2]
audio_path = os.path.join(os.getcwd(), sys.argv[3])
log_path = os.path.join(os.getcwd(), sys.argv[4])
prompts_source = os.path.join(os.getcwd(), sys.argv[5])
prompt_path = os.path.join(os.getcwd(), sys.argv[6])

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

long_stories_path = os.path.join(audio_path, long_stories_dir)
words_segments_path = os.path.join(audio_path, segments_dir)

recs_to_ignore = "recs_to_ignore.txt"

with open(recs_to_ignore, "r", encoding="utf-8") as recs:
    faulty_stories = [x.strip("\n ") for x in recs.readlines()]

#  remove working directories for audio and logs and create fresh ones
for path in [audio_path, log_path, prompt_path]:
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.mkdir(path)
dir_lst = [audio_words_path, audio_stories_path,
        log_words_path, log_stories_path,
        prompt_words_path, prompt_stories_path,
        long_stories_path, words_segments_path]
for mydir in dir_lst:
    pathlib.Path(mydir).mkdir(parents=True, exist_ok=True)

# unzip audio and log files into the path specified at call
print("Unzipping audio files...")
run(f"unzip -ojqq {audio_zip} -d {audio_path}", shell=True, check=True)
print("Unzipping log files...")
run(f"unzip -ojqq {log_zip} -d {log_path}", shell=True, check=True)

# gather audio files in a list
audio_filelist = []
for dirpath, dirnames, filenames in os.walk(audio_path):
    for filename in filenames:
        if filename.endswith(".webm"):
            audio_filelist.append(filename)

def trim_long_stories(stories_dict):
    """
    Takes a dict with items 'rec_id': ('audio path', 'audio duration').
    Recs in this dict should be audio of length > 180s.
    Tries to find the first 0.1s silence after 180s, trims the file from start to
    that silence marker, then saves it, overwriting the original file.
    If no silence is found, trims at 180s.
    """
    print(f"Trimming {len(stories_dict.items())} stories to 3 mins...")
    
    audio_tmp_dir = os.path.join(audio_path, "tmp")
    run(f"mkdir {audio_tmp_dir}", check=True, shell=True)

    for rec_id, (audio, audio_length) in stories_dict.items():
        audio_new = audio.replace("stories", "long_stories")
        # this is somehow broken now because os thinks old and new location are the same and will not move them
        # currently using force flag to override
        run(f"cp -f {audio} {audio_new}", check=True, shell=True)
        audio_tmp = audio.replace("stories", "tmp")

        noiselvl = "-50"
        ffcommand = f"ffmpeg -hide_banner -i {audio_new} -af silencedetect=noise={noiselvl}dB:d=0.1 -f null -"
        ff_out = run(ffcommand, check=True, shell=True, capture_output=True)

        silence_start = re.search(r"silence_start: 18[01].*", ff_out.stderr.decode('utf-8'))
        if audio_length <= 181:
            cut_point = audio_length
        elif silence_start:
            cut_point = float(silence_start.group(0).split(" ")[1].strip(" "))
        else:
            noiselvl = "-70"
            ffcommand = f"ffmpeg -hide_banner -i {audio_new} -af silencedetect=noise={noiselvl}dB:d=0.1 -f null -"
            ff_out = run(ffcommand, check=True, shell=True, capture_output=True)

            silence_start = re.search(r"silence_start: 18[01].*", ff_out.stderr.decode('utf-8'))
            if silence_start:
                cut_point = float(silence_start.group(0).split(" ")[1].strip(" "))
            else:
                silence_start = re.search(r"silence_start: 18[0-3].*", ff_out.stderr.decode('utf-8'))
                if silence_start:
                    cut_point = float(silence_start.group(0).split(" ")[1].strip(" "))
                else:
                    cut_point = 180
        soxcommand = f"sox {audio_new} {audio_tmp} trim 0 ={cut_point} pad 0.3 0.3"
        run(soxcommand, check=True, shell=True)
        run(f"rm {audio}", check=True, shell=True)
        run(f"mv {audio_tmp} {audio}", check=True, shell=True)
    shutil.rmtree(audio_tmp_dir)


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


# convert .webm files in audio dir to .wav with encoding = pcm_s32le
print("Converting audio files from .webm to .wav...")
for file in audio_filelist:
    infile = os.path.join(audio_path, file)
    outfile = infile.replace('webm', 'wav')
    run(f"ffmpeg -hide_banner -loglevel error -i {infile} -c:a pcm_s32le {outfile}", shell=True, check=True)
    run(f"rm {infile}", shell=True, check=True)

# move audio files to the correct folder based on task type (words or story)
print("Moving audio files...")
for f in audio_filelist:
    if 'webm' in f:
        f = f.replace('webm', 'wav')
    f_old = os.path.join(audio_path, f)
    if "words" in f:
        f_new = os.path.join(audio_words_path, f)   # keep target as var
        shutil.move(f_old, f_new)                 # move to target location
    elif "story" in f:
        f_new = os.path.join(audio_stories_path, f)     # keep target as var
        shutil.move(f_old, f_new)                     # move to target location
    else:
        f_new = ''

# gather log files in a list and prepare a dict
log_filelist = []
for dirpath, dirnames, filenames in os.walk(log_path):
    for filename in filenames:
        if filename.endswith(".csv"):
            log_filelist.append(filename)
log_files = {}

# move log files and assign their location to their rec id in the dict
print("Moving log files...")
for f in log_filelist:
    f_old = os.path.join(log_path, f)
    if "$" in f:
        f = f"{f.split('-$')[0]}.csv"
    if "words" in f:
        f_new = os.path.join(log_words_path, f)     # keep target as var
        shutil.move(f_old, f_new)                   # move to target location
    elif "story" in f:
        f_new = os.path.join(log_stories_path, f)       # keep target as var
        shutil.move(f_old, f_new)                       # move to target location
    else:
        f_new = ''
    # use the filename to generate a recording ID tag
    rec_id = f.split('.')[0]
    # then link full path to audio to rec ID in a dict
    log_files[rec_id] = f_new

# gather converted audio files in a list and assign their location to their rec id in a dict
audio_files = {}
for dirpath, dirnames, filenames in os.walk(audio_path):
    for filename in filenames:
        if filename.endswith(".wav"):
            rec_id = filename.split('.')[0]
            filepath = os.path.join(dirpath, filename)
            audio_files[rec_id] = filepath

# link the audio file and the corresponding log file to their rec id in a dict
full_dict = {}
for rec_id, audiopath in audio_files.items():
    # print(rec_id, "\t", audio_files[rec_id], "\t", log_files[rec_id])
    full_dict[rec_id] = audiopath, log_files[rec_id]

#  remove stories with faulty recordings from the dataset (specified in a txt file)
for s in faulty_stories:
    full_dict.pop(s)

#  Now we can use the dict to pull matching audio and log files and process them
#  e.g. with sox and pandas, respectively
long_stories = {}  #  dict of story audio files that are over 3 min long and need to be cropped

for rec_id, (audio, log) in full_dict.items():
    # handle story tasks
    if "story" in rec_id:
        # get audio length and check if recordings are over 3 minutes long
        audio_length = float(
            run(['soxi', '-D', audio], stdout=PIPE, check=True).stdout.decode('utf-8').strip("\n "))
        if audio_length > 180:
            # print(f"{rec_id}\t\tThis story reading is {audio_length}s long."
            # "This is longer than 3 minutes, please crop it.")
            long_stories[rec_id] = audio, audio_length
        
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

long_stories_data = pd.DataFrame(long_stories).T.rename_axis("Recording ID")
long_stories_data.columns = ['Path', 'Duration (s)']
long_stories_data.to_excel(os.path.join(audio_path, "long_stories.xlsx"))


print("Trimming stories over 3 mins...")
trim_long_stories(long_stories)

