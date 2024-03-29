"""
@Author: Bo Molenaar
@Date: 22 March 2023
@Last edited: 3 April 2023

This script can be ran after uber_serda.py to generate bootstrapped segments for SERDA v1 story tasks.
It uses ASR output to get timestamps for end of utterances automatically.
Ideally these correspond to the end of the sentences/lines in the reading prompts.

Input: 
1.  path to directory of story task audio
2.  path to directory of ASR output for these recordings
3.  path to directory to place audio segments

Output:
Segmented audio in dir 3.
"""

# create a dict with rec_id, story audio, story AO


# then run segmentation on each entry

def segment_story(full_rec_path, rec_AO, full_prompt_path,  rec_segments_path):
    """
    Takes a story audio file and matches it to its story prompt.
    Then, bootstrapped segments generated by WhisperX ASR are searched 
    to identify start/end timestamps in the audio for each line in the prompt.
    
    """

    # first off let's store all prompt lines in memory
    # because it will be much easier to deal with than nested loops
    prompt_segments = {}
    with open(full_prompt_path, 'r', encoding='utf-8').readlines() as prompt_lines:
        for prompt_nr, prompt_text in enumerate(prompt_lines):
            prompt_segments[prompt_nr] = prompt_text

    # make a dict of segments in the ASR output
    # key = 'id'
    # value = 3-tuple of (start, end, text)
    ao_segments = {}
    with open(rec_AO, 'r', encoding='utf-8').readlines() as ao_lines:
        for i, line in enumerate(ao_lines):
            if (i >= 3) and ('{' in line):

                # collect segment details in a dict
                seg_nr = ao_lines[i+1]
                seg_start = ao_lines[i+3]
                seg_end = ao_lines[i+4]
                seg_text = ao_lines[i+5]

                ao_segments[seg_nr] = seg_start, seg_end, seg_text

    # now do something with them


    # this is probably better to leave for version 2 of this script
    if len(prompt_segments.items()) == len(ao_segments.items()):
        # this is the ideal case where the number of
        # lines in the prompt is equal to the number of
        # segments in the ASR output
        # TODO
        # probably get start time with ao_segments[prompt_nr][0]
        # and end time with  ao_segments[prompt_nr][1]

        print('great! there are as many prompt as ao segments.')

    else:
        # in this case, there will be >= 1 major differences between prompt and ao segments
        # TODO
        # do something
        # think about what we want in this scenario
        # we can probably still match the prompt_nr to ao segment start and end
        # but then we're left with a bunch of segments after prompt line enumerator runs out
        print('the number of segments in ao is not equal to the number of lines in the prompt')

        # do manual inspection for case 2.
        # this works best if subset 2 is small,
        # so try to write a small script to check the distribution over these two cases.

