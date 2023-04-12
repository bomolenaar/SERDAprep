# SERDAprep

This is a collection of scripts to gather, organise and preparare data collected with SERDA within the ASTLA project.
The scripts require some manual steps before running.

First, some data needs to be downloaded from Citolab manually. Then, audio data can be downloaded through a script + urls of the audio files stored at Cito.

# Example run

1.0 MANUAL-0  
Set your working directory where you will download this repository and download/copy all other necessary files:

    SERDAdir="/vol/tensusers5/bmolenaar/SERDA"
    git clone https://github.com/bomolenaar/SERDAprep $SERDAdir
    cd $SERDAdir


1.1 MANUAL-1  
Manual download of log file zip from `serda-admin.azurewebsites.net` using the top right button <img src="https://i.imgur.com/FdySJhk.png" height="25" /> and upload to Ponyland at `$SERDAdir/my_log.zip`.

1.2. MANUAL-2  
Manual download of prompts for story tasks, uploaded to Ponyland at `$SERDAdir/raw_prompts/`.

2. AUDIO DOWNLOAD

        audio_zip=$SERDAdir/my_audio/
        urls=$SERDAdir/urls.txt

        download.sh $audio_zip $urls

3. UBER_SERDA

        project=$SERDAdir/myproject
        log_zip=$SERDAdir/my_log.zip
        raw_prompts=$SERDAdir/docs/raw_prompts
        ignore_list=$SERDAdir/recs_to_ignore.txt

        python3 uber_serda.py -clean -a $audio_zip -l $log_zip $project audio logs prompts $raw_prompts $ignore_list

4. MANUAL-3  
Decode the files in `$project/audio/stories` and place the ASR output in `$project/asr/stories/`.

5. SEGMENT_STORIES_ASR
        
        python3 segment_stories_ASR.py $project audio asr prompts

# Explanation of steps

## 1. Manual downloads

1. Manually download the zip of log files from the SERDA admin environment (`serda-admin.azurewebsites.net`) and copy them to your desired folder (e.g. on Ponyland). This zip should contain [6 * number of speakers] .csv log files. Example: `2RRDV-words_1-20230113140713310.csv`.
2. Manually download the prompts for story tasks (either from Cito or copy them from Bo's folder on Ponyland: `/vol/tensusers5/bmolenaar/SERDA/docs/raw_prompts`). The files should be named `story{1/2/3}_clean.txt` and contain 1 sentence per line. Don't put these in your project folder or they'll get removed later (e.g. place the folder one level up).

## 2. `download.sh`

This is the script to download audio files stored at Cito.

### Usage

    download.sh [target directory] [list of URLs]

The script will download the files from the provided URLs, simplify the filenames, zip the folder and remove the original unzipped folder.  
There should be 12 files per speaker:

* 6 audio files
  * words_1, words_2, words_3
  * story_1, story_2, story_3
* 6 log files
  * words_1, words_2, words_3
  * story_1, story_2, story_3

## 3. `uber_serda.py`

This script does data selection and preparation by running two separate scripts: `serda_data_sel.py` and `serda_data_prep.py`.

### Usage

    uber_serda.py [--clean] [-a/--audiozip AUDIOZIP] [-l/--logzip LOGZIP] project_dir audio_dir log_dir prompt_dir raw_prompts_dir recs_to_ignore.txt

* `--clean` is an optional flag that determines whether the script will generate clean directories under `project_dir`, starting from just your audio and logs zips. Default behaviour is `False`.  
When using `--clean`, it's required to specify the path to your audio zip with `-a` or `--audiozip`. Similarly, `-l` or `--logzip` is also required and specifies the path to your logs zip.

* `project_dir` is the parent directory for your project that will contain `audio_dir`, `log_dir` and `prompt_dir`.

* `raw_prompts` is the path to the directory where you put the story prompt files from step 1.2.

* `recs_to_ignore.txt` is a .txt file specifying recording IDs (**! not paths**) of faulty recordings. For example: `ABCDE-story_1-20230101090012345` One rec ID per line. Faulty recordings can only really occur for story tasks, so this will be a list of story task IDs. The script will look for the corresponding audio files in your `audio_dir` during data selection and simply ignore them for the rest of the process.

### `serda_data_sel.py`

If called with `--clean`, this script unzips the provided audio and logs zips and sorts the audio and log files into the corresponding folders. Files are also sorted on task type, i.e. `words` and `story`. Note that they are **not** separated on task number (e.g. no different folders for task words_1 and words_2).

The audio files obtained from Cito are originally `.webm` format, so they are converted to `.wav` using ffmpeg before further operations. The script does not ask the user to specify an encoding and uses `pcm_s32le` by default, but this can be changed in the script itself if desired. Before conversion, faulty recordings are removed from the dataset based on the list of recording IDs specified `recs_to_ignore.txt`.

The log files obtained from the SERDA admin environment have some redundant information in the filenames. This is removed in this script.

A dict is then created where each recording ID is paired with a 2-tuple of the corresponding audio and log filepaths. This dict is used as input for `serda_data_prep.py`.

Due to an oversight during data collection, some recordings for story tasks are over 3 minutes long, which is not intended. Recordings over 180 seconds long are identified and trimed to the nearest silence after 180s. Original long files are kept in `audio_dir/long_stories`.

After running this script, you should have a your parent directory with subdirectories for audio and logs, e.g.:

    myproject
        audio
            long_stories
            stories
                speaker1_story1.wav, speaker1_story2.wav, etc.
            words
                full
                    speaker1_words1.wav, speaker1_words2.wav, etc.
        logs
            stories
                speaker1_story1.csv, speaker1_story2.csv, etc.
            words
                speaker1_words1.csv, speaker1_words2.csv, etc.

### `serda_data_prep.py`

This script is not ran separately, only from `uber_serda.py` because it takes a `serda_data_sel` dict as input. If you only want to redo data prep, run `uber_serda.py` without --clean.

This data preparation script matches prompts to audio. The `prompt_dir` and `raw_prompts` arguments from your `uber_serda.py` call are used here. For story tasks, whole prompts are assigned since there are no segments available at this stage. For word tasks, the prompted words are assigned to individual word segments.

Next, word task recordings are segmented into separate files for each word, based on timestamps from the corresponding log file. There is a special case for the first word in each task, since there is no unambiguous timestamp for when the segment starts. As such, 2 segments are generated: one from the start of the recording and one from the assumed start time of the child speaking.

After segmentation, there should be 153 word segment audiofiles per speaker. For round 1 of data collection, this amounts to `197 * 153 = 30,141` files. Prompt files do not have 2 variants for the first word in each word task, so the number should be 150 per speaker.

Your directory structure should now look like this:

    myproject
        audio
            long_stories
            stories
                speaker1_story1.wav, speaker1_story2.wav, etc.
            words
                full
                    speaker1_words1.wav, speaker1_words2.wav, etc.
                segments
                    speaker1_words1_102.wav, speaker1_words_103.wav, etc.
        logs
            stories
                speaker1_story1.csv, speaker1_story2.csv, etc.
            words
                speaker1_words1.csv, speaker1_words2.csv, etc.
        prompts
            stories
                speaker1_story1.prompt, speaker1_story2.prompt, etc.
            words
                speaker1_words1_102.prompt, speaker1_words_103.prompt, etc.

## 4. Run ASR on all audio files: words and stories

Here you can use the files prepared by `uber_serda.py` to run ASR and get timestamps, segments, (confidence scores), etc.  
ASR output should be placed under `{uber_serda.py parent directory}/asr` for the final step.

Expected format of ASR output is `.json` (this is the extension used by WhisperX, which was our preferred ASR for bootstrapping segments).

## 5. `segment_stories_ASR.py`

Finally, when ASR output is in place, we can use it to bootstrap segments (=sentences) for each line in story prompts. This script is TODO.

### Usage

        segment_stories_ASR.py $project_dir $audio_dir $asr_dir $prompt_dir

* `project_dir`, `audio_dir` and `prompt_dir` are the same folders you used for `uber_serda.py` at step 3.

* `asr_dir` is the folder you placed the ASR output in at step 4 (should be `$project_dir/asr`).

\# TODO what does this script do

### \# TODO expected output at the end
