#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import argparse
import shutil
from subprocess import run, PIPE
import re
import pathlib
import pandas as pd


""""
@Author:        Bo Molenaar
@Date:          13 March 2023

@Last edited:    13 March 2023

This script takes SERDA v1 audio and log files and sorts them on task.
The audio files are .webm format, so ffmpeg is called to convert them into .wav (maintaining 32-bit encoding)
Log files are matched to the corresponding audio file in a dict.
Audio files for story tasks with duration > 3 minutes are trimmed to 3 minutes.
Audio files for word tasks are split on single words with added word ID tag.
"""



def gen_clean_dict(audio_dir, log_dir, ignore_recs, clean_dirs, audio_raw = None, log_raw = None):
    """
    This function encapsulates the entire data selection procedure,
    from audio and log zips + prompt files to directories of stories and segmented words.
    Story audio over 3 minutes is trimmed and specified recordings are ignored.
    """

    # declare some directories to use
    words_dir = "words"
    stories_dir = "stories"
    long_stories_dir = "long_stories"

    audio_words_path = os.path.join(audio_dir, words_dir, "full")
    audio_stories_path = os.path.join(audio_dir, stories_dir)
    log_words_path = os.path.join(log_dir, words_dir)
    log_stories_path = os.path.join(log_dir, stories_dir)

    long_stories_path = os.path.join(audio_dir, long_stories_dir)

    # load lists of recordings to ignore because they are faulty
    # (you need to manually create this list)
    with open(ignore_recs, "r", encoding="utf-8") as recs:
        faulty_stories = {x.strip("\n ") for x in recs.readlines()}

    if clean_dirs:
        print("\tCreating new subfolders...")

        dir_lst = [audio_words_path, audio_stories_path,
                log_words_path, log_stories_path,
                long_stories_path]
        for mydir in dir_lst:
            pathlib.Path(mydir).mkdir(parents=True, exist_ok=True)
        print("\tDone.")

        # unzip audio and log files into the path specified at call
        print("\tUnzipping audio files...")
        run(f"unzip -ojqq {audio_raw} -d {audio_dir}", shell=True, check=True)
        print("\tDone.")
        print("\tUnzipping log files...")
        run(f"unzip -ojqq {log_raw} -d {log_dir}", shell=True, check=True)
        print("\tDone.")

        # gather audio files in a list
        audio_filelist = []
        for dirpath, dirnames, filenames in os.walk(audio_dir):
            for filename in filenames:
                if filename.endswith(".webm"):
                    #  remove stories with faulty recordings from the dataset
                    rec_id = filename.rstrip('.webm')
                    if rec_id in faulty_stories:
                        # print(os.path.join(dirpath, filename))
                        run(f"rm {os.path.join(dirpath, filename)}", shell=True, check=True)
                    else:
                        audio_filelist.append(filename)
        # print([f for f in audio_filelist if "story" in f])
        
        # convert .webm files in audio dir to .wav with encoding = pcm_s32le
        print("\tConverting audio files from .webm to .wav...")
        for file in audio_filelist:
            infile = os.path.join(audio_dir, file)
            outfile = infile.replace('webm', 'wav')
            run(f"ffmpeg -hide_banner -loglevel error -i {infile} -c:a pcm_s32le {outfile}", shell=True, check=True)
            run(f"rm {infile}", shell=True, check=True)
        print("\tDone.")

        # move audio files to the correct folder based on task type (words or story)
        print("\tMoving audio files...")
        for f in audio_filelist:
            f_old = os.path.join(audio_dir, f)
            if "words" in f:
                f_new = os.path.join(audio_words_path, f)   # keep target as var
                shutil.move(f_old, f_new)                 # move to target location
            elif "story" in f:
                f_new = os.path.join(audio_stories_path, f)     # keep target as var
                shutil.move(f_old, f_new)                     # move to target location
            else:
                f_new = ''
        print("\tDone.")

        # gather log files in a list and prepare a dict
        log_filelist = []
        for dirpath, dirnames, filenames in os.walk(log_dir):
            for filename in filenames:
                if filename.endswith(".csv"):
                    log_filelist.append(filename)
        log_files = {}

        # move log files and assign their location to their rec id in the dict
        print("\tMoving log files...")
        for f in log_filelist:
            f_old = os.path.join(log_dir, f)
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
        print("\tDone.")

    else:
        # gather log files in a list and prepare a dict
        log_filelist = []
        log_files = {}
        for dirpath, dirnames, filenames in os.walk(log_dir):
            for filename in filenames:
                if filename.endswith(".csv"):
                    log_filelist.append(filename)
                    rec_id = filename.split('.')[0]
                    log_files[rec_id] = os.path.join(dirpath, filename)

    # gather converted audio files in a list and assign their location to their rec id in a dict
    audio_files = {}
    for dirpath, dirnames, filenames in os.walk(audio_dir):
        for filename in filenames:
            if (filename.endswith(".wav")) and ('segments' not in dirpath):
                rec_id = filename.split('.')[0]
                filepath = os.path.join(dirpath, filename)
                audio_files[rec_id] = filepath

    # link the audio file and the corresponding log file to their rec id in a dict
    full_dict = {}
    for rec_id, audiopath in audio_files.items():
        # print(rec_id, "\t", audio_files[rec_id], "\t", log_files[rec_id])
        full_dict[rec_id] = audiopath, log_files[rec_id]
    # print(list(full_dict.items())[:10])

    if clean_dirs:
        #  Now we can use the dict to pull matching audio and log files and process them
        #  e.g. with sox and pandas, respectively
        long_stories = {}  #  dict of story audio files that are over 3 min long and need to be cropped

        for rec_id, (audio, log) in full_dict.items():
            if "story" in rec_id:
                # get audio length and check if recordings are over 3 minutes long
                audio_length = float(
                    run(['soxi', '-D', audio], stdout=PIPE, check=True).stdout.decode('utf-8').strip("\n "))
                if audio_length > 180:
                    # print(f"{rec_id}\t\tThis story reading is {audio_length}s long."
                    # "This is longer than 3 minutes, please crop it.")
                    long_stories[rec_id] = audio, audio_length

        long_stories_data = pd.DataFrame(long_stories).T.rename_axis("Recording ID")
        long_stories_data.columns = ['Path', 'Duration (s)']
        long_stories_data.to_excel(os.path.join(audio_dir, "long_stories.xlsx"))

        trim_long_stories(long_stories, audio_dir)

    return full_dict


def trim_long_stories(stories_dict, audio_dir):
    """
    Takes a dict with items 'rec_id': ('audio path', 'audio duration').
    Recs in this dict should be audio of length > 180s.
    Tries to find the first 0.1s silence after 180s, trims the file from start to
    that silence marker, then saves it, overwriting the original file.
    If no silence is found, trims at 180s.
    """
    print(f"\tTrimming {len(stories_dict.items())} stories to 3 mins...")
    
    audio_tmp_dir = os.path.join(audio_dir, "tmp")
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
    print("\tDone.")

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--clean', help = "Flag specifying whether you want to generate new directories. Default=False", action = 'store_true', required=False)
    parser.add_argument('-a', '--audiozip', required='--clean' in sys.argv, help = "Path to raw audio zip. Required when using --clean.")
    parser.add_argument('-l', '--logzip', required='--clean' in sys.argv, help = "Path to raw log zip. Required when using --clean")
    parser.add_argument('project_dir',
                    help = "Parent project directory where you want to process and store audio, logs, prompts and ASR transcriptions.")
    parser.add_argument('audio_dir', help = "Name of audio processing and storing dir")
    parser.add_argument('log_dir', help = "Name of log processing and storing dir")
    parser.add_argument('recs_to_ignore', help = "Location of a file specifying recordings to ignore")
    args = parser.parse_args()
    if args.clean and (args.audiozip is None or args.logzip is None):
        parser.error("--clean requires --audiozip and --logzip.")
        
    audio_path = os.path.join(args.project_dir, args.audio_dir)
    log_path = os.path.join(args.project_dir, args.log_dir)

    if args.clean:
        gen_clean_dict(audio_path, log_path, args.recs_to_ignore, args.clean, args.audiozip, args.logzip)
    else:
        gen_clean_dict(audio_path, log_path, args.recs_to_ignore, args.clean)
