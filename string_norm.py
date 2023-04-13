""""
@Author:        Bo Molenaar
@Date:          3 June 2022

@Lastedited:    12 April 2023

This script performs text_filter.py for a given input folder 
and stores filtered output to given output folder.
Optionally you can select to use text_filter_no-unk.py with opt -u False or --unk=False

Expected input: 1) folder to read files from, 2) folder to place output, 
3) extension of files to read, 4) optional -u or --unk flag
"""

#!usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import getopt
import ast

unk = True
infolder = sys.argv[1]
outfolder = sys.argv[2]
filetype = sys.argv[3]
argv = sys.argv[4:]

try:
    opts, args = getopt.getopt(argv, "u:", ["unk="])
except getopt.GetoptError as err:
    print(err)
    opts = []

for opt, arg in opts:
    if opt in ["-u", "--unk"]:
        unk = ast.literal_eval(unk)


def string_norm(infolder, outfolder, use_unk):
    # location of text_filter script (originally by Cristian Tejedor Garcia, edited by Bo Molenaar)
    if not use_unk:
        textfilter_path = './string_norm/text_filter_no-unk.py'
    else:
        textfilter_path = './string_norm/text_filter_adapt.py'

    # get files from indir to be filtered
    file_lst = []
    for dirpath, dirnames, filenames in os.walk(infolder):
        for file in filenames:
            if (filetype in file) and ('_tmp' not in file) and ('README' not in file):
                file_lst.append(file)
    print(f"Normalising {len(file_lst)} {filetype} files...")

    # make a temp dir to put the text filter output if infolder name = outfolder name
    if infolder == outfolder:
        outfolder = outfolder.rstrip('/', 2) + '_filtered/'

        if os.path.isdir(outfolder):
            shutil.rmtree(outfolder)
        os.mkdir(outfolder)

        # handle archiving of original files > indir_unfiltered
        infolder_archive = ""
        infolder_fields = infolder.split('/')
        if infolder_fields[-1] != "":
            infolder_archive = "/".join(infolder_fields[:-1]) + "/." + infolder_fields[-1] + "_unfiltered"
        else:
            infolder_archive = "/".join(infolder_fields[:-2]) + "/." + infolder_fields[-2] + "_unfiltered"

        # start with a clean indir archive
        if os.path.isdir(infolder_archive):
            shutil.rmtree(infolder_archive)

        # run the filter for each file in indir
        for file in file_lst:
            os.system(f"python3 {textfilter_path} {infolder}{file} {outfolder}{file}")

        print("Done.\nMoving files...")

        # make outdir name = indir name
        os.system(f"mv {infolder} {infolder_archive}")
        os.system(f"mv {outfolder} {infolder}")

        print(f"Done.\nNormalised files are in {infolder}."
              f"\nOriginal files are in {infolder_archive}")

    else:
        if os.path.isdir(outfolder):
            shutil.rmtree(outfolder)
        os.mkdir(outfolder)

        # run the filter for each file in indir
        for file in file_lst:
            os.system(f"python3 {textfilter_path} {os.path.join(infolder, file)} {os.path.join(outfolder, file)}")

        print(f"Done.\nNormalised files are in {outfolder}.")

if __name__ == "__main__":
    string_norm(infolder, outfolder, unk)
