#!/usr/bin/python

"""
combine_druid_docs.py

Version:        14 Sep 2021

Purpose:        Compare Druid docs from apache/druid to those in imply-docs.
                Copy any changed files over to imply-docs. Only files that exist in both druid/docs and imply-docs/docs get copied over. So if there are new file(s) from druid/docs, you need to manually copy them over to imply-docs the first time. New files are shown in the Comparison results.

Help:           python combine_druid_docs.py --help

Example call:   python combine_druid_docs.py -i input.conf -o output.txt

Example config:
{
    "druid_oss_docs": "$HOME/codebase/druid/docs",
    "druid_imply_docs": "$HOME/codebase/imply-docs/docs/druid"
}

"""

import filecmp
import json
import os
import re
import shutil
import sys


def read_config_file(input_conf):

    try:
        with open(input_conf, 'r') as conf:
            config_data = json.load(conf)
    except:
        sys.exit(f"\nERROR: Couldn't open config file: {input_conf}"
                "\nCheck that JSON is properly formatted.\n")

    return config_data


def list_diff_files(dcmp, output_left, output_right, output_common):
    """Modified from https://docs.python.org/3/library/filecmp.html"""

    for lname in dcmp.left_only:
        output_left.append(dcmp.left + "/" + lname)
    for rname in dcmp.right_only:
        output_right.append(dcmp.right + "/" + rname)
    for name in dcmp.diff_files:
        output_common.append(dcmp.left + "/" + name)

    # iterate over the subdirectories in common
    for sub_dcmp in dcmp.subdirs.values():
        list_diff_files(sub_dcmp, output_left, output_right, output_common)

    return output_left, output_right, output_common


def write_output_section(file_obj, header, left_only, right_only, changed_files):

    heading_separator = "*******************\n"
    full_heading = "\n\n" + heading_separator + header + "\n" + heading_separator

    # define a few variables to make the output more helpful and readable
    pretty_left = '\n - '.join(left_only)
    pretty_right = '\n - '.join(right_only)
    pretty_changed = '\n - '.join(changed_files)
    len_l = len(left_only)
    len_r = len(right_only)
    len_c = len(changed_files)

    # write the output
    file_obj.write(full_heading)
    file_obj.write(f"\nFiles only in OSS Druid ({len_l}):\n - {pretty_left}\n\n")
    file_obj.write(f"Files only in Imply Druid ({len_r}):\n - {pretty_right}\n\n")
    file_obj.write(f"Changed files ({len_c}):\n - {pretty_changed}")


def combine_druid_docs(input_conf, output_file):

    # assign variables from config file
    # - druid_oss   is "left" in comparison
    # - druid_imply is "right" in comparison
    config_data = read_config_file(input_conf)
    druid_oss = config_data["druid_oss_docs"]
    druid_imply = config_data["druid_imply_docs"]
    ignore_list = config_data["ignore_list"]

    # open output file and record a few things
    f = open(output_file, "a")
    f.write(f"Source of OSS Druid docs: {druid_oss}\n")
    f.write(f"Source of Imply Druid docs: {druid_imply}\n")
    f.write(f"Files ignored in comparison: {ignore_list}")

    # run overall comparison
    doc_diff = filecmp.dircmp(druid_oss, druid_imply, ignore_list)

    output_left = []
    output_right = []
    output_common = []

    # aggregate results, recursively
    output_left, output_right, output_common = list_diff_files(
        doc_diff, output_left, output_right, output_common)

    # write output
    write_output_section(
        f,
        "Comparison results",
        output_left,
        output_right,
        output_common)

    f.close()

    # ask to confirm copying over common files that have been changed
    pretty_changed2 = '\n'.join(output_common)
    val = input(f"The following files in {doc_diff.left} will overwrite "
          f"their counterparts in {doc_diff.right}.\n\n"
          f"{pretty_changed2}\n\nContinue? (y/n) ")

    if val.lower() != 'y':
        sys.exit("\nExiting without copying files.")

    # define the location of where the files will be copied
    output_common_absdirname = [os.path.normpath(p) for p in output_common]
    output_common_reldirname = [re.sub(r".+docs/", "", p) for p in output_common_absdirname]
    output_common_sink = [os.path.join(doc_diff.right, mydir)
                            for mydir in output_common_reldirname]

    # do the file copying
    for source, sink in zip(output_common, output_common_sink):
        #print(f"coyping from {source} to {sink}")
        shutil.copyfile(source, sink)


def main():
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input-conf",
                        help="Name of input configuration file; "
                             "should be in JSON format with keys "
                             "for \"druid_oss_docs\", "
                             "\"druid_imply_docs\", \"ignore_list\"")

    parser.add_argument("-o", "--output",
                        help="Name of the output text file")

    args = parser.parse_args()

    if not os.path.isfile(args.input_conf):
        sys.exit(f"\nERROR: Could not find input file {args.input_conf}\n")

    combine_druid_docs(args.input_conf, args.output)

if __name__ == "__main__":
    main()

