""""
@Author:        Bo Molenaar
@Date:          1 February 2023

@Last edited:    17 March 2023

This script processes SERDA v1 data after they have been organised into task directories.
It requires a dict from serda_data_sel.py with recording IDs and paths to the audio and log for that recording.

Audio files for word tasks are split on single words with added word ID tag.

"""

#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import shutil
import pathlib
from subprocess import run
import pandas as pd


def segment_words(full_rec_path, rec_segments_path, words_dict):
    """
    Takes a dict for 1 word task with items 'prompt_id': ('prompt_id', 'segment_start', 'segment_end').
    Then recalculates start time as word appearance (= prev word end + 1323ms).
    Finally the timestamps are used to create an audio file for each segment.
    """
    segments = list(words_dict.items())
    for counter, (prompt_id, (start_time, end_time)) in enumerate(segments):
        segment_chunks = rec_segments_path[:-4].rsplit("-", 1)
        if prompt_id in {101, 201, 301}:

            # create backup segment starting from the beginning of the recording
            segment_path_start = f"{segment_chunks[0]}_{prompt_id}_taskstart-{segment_chunks[1]}.wav"
            soxcommand_start = f"sox {full_rec_path} {segment_path_start} trim 0 ={end_time/1000} pad 0.3 0.3"
            # print(soxcommand_start)
            run(soxcommand_start, check=True, shell=True)

            # create segment starting from the start_speak timestamp in the task log
            segment_path_timestamp = f"{segment_chunks[0]}_{prompt_id}_logstamp-{segment_chunks[1]}.wav"
            soxcommand_timestamp = f"sox {full_rec_path} {segment_path_timestamp} trim {start_time/1000} ={end_time/1000} pad 0.3 0.3"
            # print(soxcommand_timestamp)
            run(soxcommand_timestamp, check=True, shell=True)
        
        else:
            start_time = segments[counter-1][1][1] + 1323
            segment_path = f"{segment_chunks[0]}_{prompt_id}-{segment_chunks[1]}.wav"
            soxcommand = f"sox {full_rec_path} {segment_path} trim {start_time/1000} ={end_time/1000} pad 0.3 0.3"
            # print(soxcommand)
            run(soxcommand, check=True, shell=True)

            # TODO
            # investigate sox error
            # potential fix is to use end of audio instead of log timestamp


def prepare_data(clean_dirs, full_dict, audio_path, log_path, prompts_source, prompt_path):
    """
    docstring
    """
    words_dir = "words"
    stories_dir = "stories"
    segments_dir = "segments"

    audio_words_path = os.path.join(audio_path, words_dir, "full")
    # audio_stories_path = os.path.join(audio_path, stories_dir)
    # log_words_path = os.path.join(log_path, words_dir)
    # log_stories_path = os.path.join(log_path, stories_dir)
    prompt_words_path = os.path.join(prompt_path, words_dir)
    prompt_stories_path = os.path.join(prompt_path, stories_dir)
    words_segments_path = os.path.join(audio_path, words_dir, segments_dir)

    #  remove working directories for audio and logs and create fresh ones
    if clean_dirs:
        dir_lst = [prompt_words_path, prompt_stories_path,
                   words_segments_path]
        for mydir in dir_lst:
            shutil.rmtree(mydir)
            pathlib.Path(mydir).mkdir(parents=True, exist_ok=True)


    for rec_id, (full_audio, log) in full_dict.items():
        # handle story tasks
        if "story" in rec_id:
            storynum = rec_id.split("-")[1].replace("_", "")
            infile = os.path.join(prompts_source, f"{storynum}_clean.txt")
            outfile = os.path.join(prompt_stories_path, f"{rec_id}.prompt")

            # generate prompt file
            prompt = ""
            with open(infile, "r", encoding="utf-8") as prompt_in, open(outfile, "w", encoding="utf-8") as prompt_out:
                for line in prompt_in.readlines():
                    prompt += line
                prompt_out.write(prompt)
            
            ## NO SEGMENTATION IN THIS SCRIPT ##
            # story segmenting is not possible without timestamps
            # SERDA v1 does not generate these
            # bootstrapped segments can be obtained from ASR output on story tasks
            # for this, run segment_stories.py after running ASR

        # handle word tasks
        elif "words" in rec_id:
            # print(rec_id, full_audio, log)
            word_segments = {}
            audio_segments_path = full_audio.replace(audio_words_path, words_segments_path)
            # load logfile to get the word timestamps
            log_data = pd.read_csv(log, delimiter=";", index_col="user_id")

            for speaker_id, row in log_data.iterrows():
                word_segments[row['prompt_id']] = (row['start_speak'], row['stop_speak'])
                prompt = str(row['prompt'])
                prompt_id = row['prompt_id']
                segment_chunks = rec_id.rsplit("-", 1)
                outfile = os.path.join(prompt_words_path,
                                       f"{segment_chunks[0]}_{prompt_id}-{segment_chunks[1]}.prompt")
                with open(outfile, "w", encoding="utf-8") as prompt_out:
                    prompt_out.write(prompt)

            segment_words(full_audio, audio_segments_path, word_segments)
