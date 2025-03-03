#!/usr/bin/python

"""
combine_druid_docs.py

Version:        29 January 2025

Purpose:        This script updates Druid docs in Imply
                from the Imply fork of apache/druid.
                Compares these git repos:
                - implydata/druid/docs
                - imply-docs/docs/druid

Help:           python combine_druid_docs.py --help

Example call:   python combine_druid_docs.py -i combine.conf -o output.txt

Example combine.conf:
{
    "imply_fork_druid_docs": "$HOME/codebase/druid/docs",
    "druid_imply_docs": "$HOME/codebase/imply-docs-saas/enterprise/druid",
    "ignore_dirs": ["tutorials"]
    "ignore_list": ["_bin", ".DS_Store", "configuration/logging.md"]
}

"""

import filecmp
import json
import os
import re
import shutil
import subprocess
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


def write_output_section(file_obj, header, left_only, right_only):

    heading_separator = "*******************\n"
    full_heading = "\n\n" + heading_separator + header + "\n" + heading_separator

    # define a few variables to make the output more helpful and readable
    pretty_left = '\n - '.join(left_only)
    pretty_right = '\n - '.join(right_only)
    len_l = len(left_only)
    len_r = len(right_only)

    # write the output
    file_obj.write(full_heading)
    file_obj.write(f"\nFiles only in OSS Druid ({len_l}):\n - {pretty_left}\n\n")
    file_obj.write(f"Files only in Imply Druid ({len_r}):\n - {pretty_right}\n\n")


def combine_druid_docs(input_conf, output_file):
    """
    THIS IS THE WORKHORSE
    """

    # assign variables from config file
    # - druid_imply_fork is "left" in comparison
    # - imply_docs is "right" in comparison
    config_data = read_config_file(input_conf)
    druid_imply_fork = config_data["imply_fork_druid_docs"]
    imply_docs = config_data["druid_imply_docs"]
    ignore_dirs = config_data["ignore_dirs"]
    ignore_list = config_data["ignore_list"]

    # check branches
    branch_result = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=druid_imply_fork, capture_output=True)
    os_branch = branch_result.stdout.decode('ascii').strip()
    tag_result = subprocess.run(["git", "describe", "--tags", "HEAD"], cwd=druid_imply_fork, capture_output=True)
    os_tag = tag_result.stdout.decode('ascii').strip()

    # print info to terminal
    print(f"---------------------------------------------")
    print(f"Source of OSS Druid docs: {druid_imply_fork}")
    print(f"\tbranch = {os_branch}")
    print(f"\ttag = {os_tag}\n")
    print(f"Source of Imply Druid docs: {imply_docs}")
    print(f"---------------------------------------------\n")

    # open output file and record a few things
    f = open(output_file, "w")
    f.write(f"\nSource of OSS Druid docs: {druid_imply_fork}\n")
    f.write(f"\tbranch = {os_branch}\n")
    f.write(f"\ttag = {os_tag}\n\n")
    f.write(f"Source of Imply Druid docs: {imply_docs}\n\n")
    f.write(f"Directories ignored in comparison: {ignore_dirs}\n\n")
    f.write(f"Files ignored in comparison: {ignore_list}")

    # run overall comparison
    doc_diff = filecmp.dircmp(druid_imply_fork, imply_docs, ignore_dirs)

    output_left = []
    output_right = []
    output_common = []

    # aggregate results, recursively
    output_left, output_right, output_common = list_diff_files(
        doc_diff, output_left, output_right, output_common)

    # remove files that are in the ignore list from comparison
    for fn in ignore_list:
        test_string = f"{doc_diff.left}/{fn}"
        if test_string in output_left: output_left.remove(test_string)
        test_string = f"{doc_diff.right}/{fn}"
        if test_string in output_right: output_right.remove(test_string)
        test_string = f"{doc_diff.left}/{fn}"
        if test_string in output_common: output_common.remove(test_string)

    # write output
    write_output_section(
        f,
        "Comparison results",
        output_left,
        output_right)
    f.close()

    # ----------------------------------------------------------------------
    # Stage 1: FILES IN COMMON
    # copy over ALL files in common
    print(f"Overwriting files in common from {doc_diff.left} "
          f"to {doc_diff.right}.")

    # define the location of where the files will be copied
    output_common_absdirname = [os.path.normpath(p) for p in output_common]
    output_common_reldirname = [re.sub(r".+docs/", "", p) for p in output_common_absdirname]
    output_common_sink = [os.path.join(doc_diff.right, mydir)
                            for mydir in output_common_reldirname]

    # do the file copying
    changed_files = []
    for source, sink in zip(output_common, output_common_sink):
        changed_files.append(sink)
        shutil.copyfile(source, sink)
    # ----------------------------------------------------------------------
    # Stage 2: FILES ONLY IN OS DRUID
    # ask to confirm copying EACH file at a time
    print("\nFor each of the following files only in OSS Druid, confirm "
        "(y/n) whether it should be copied over to Imply docs.\n")

    for osfile in output_left:

        # generate the destination path
        basename = "/".join(osfile.split("/")[3:])
        sink = os.path.join(doc_diff.right, basename)

        # if it's a folder, just create it
        # potentially won't be used, but git won't check empty folders
        if os.path.isdir(osfile) and not os.path.isdir(sink):
            os.makedirs(sink)
            continue

        # if it's a file, ask for copy confirmation
        answer = input(f"{osfile} ")
        if answer.lower() != 'y':
            continue
        print(f"copying from {osfile} to {sink}\n"
              f"🚨 add {sink} to the sidebar\n\n")
        changed_files.append(sink)
        shutil.copyfile(osfile, sink)

    # Check if "sql-functions.md" was copied
    if any(file.endswith("sql-functions.md") for file in changed_files):
        print("🚨 sql-functions.md has changed. Create a follow up PR to update ./polaris/druid-sql/sql-functions.md to match, e.g. add a new function")


    # request checks
    print("\n👋 hi writer, what to do next:\n"
          "1. Do all the things marked by alarm bells above. Can ignore extension files in sidebar.\n"
          "2. 👀 Review output.txt. Remove any deprecated files listed under 'Files only in Imply Druid'\n"
          "3. Add the changed files and create the PR.\n"
          "4. Cherry-pick the differences between Apache/Imply docs."
         )
    return changed_files


def fix_up_oss_docs(file_list):
    """
    1) Add the import statement for tabs
    2) Change the OSS Druid version variable to what Imply/Docusaurus2 uses
    3) Turns off Vale checking for all changed Druid docs.
       https://vale.sh/docs/topics/config/#markdown-amp-html
    """
    def find_header_close(lst):
        hyphen_locations = [i for i, x in enumerate(lst) if x.strip() == '---']
        return hyphen_locations[1]

    for fn in file_list:

        # only open .md files, skip things like images
        _, file_extension = os.path.splitext(fn)
        if file_extension != ".md" and file_extension != ".mdx":
            continue

        with open(fn, 'r') as f:
            lines = f.readlines()

            try:
                where_to_insert = find_header_close(lines) + 1
            except IndexError:
                print("\n🚨 ERROR: File missing Docusaurus header. Add the header and Vale ignore in "
                      f"{fn}")
                continue
            lines.insert(where_to_insert, '\nimport {DRUIDVERSION} from "@site/static/js/versions.js"\n\n')

            where_to_insert = find_header_close(lines) + 2
            lines.insert(where_to_insert, "<!-- vale off -->\n")
            lines.insert(len(lines), "\n\n<!-- vale on -->")

            for i, line in enumerate(lines):
                if "{{DRUIDVERSION}}" in line:
                    lines[i] = line.replace("{{DRUIDVERSION}}", "{DRUIDVERSION}")

        with open(fn, 'w') as f:
            f.writelines(lines)

def main():
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input-conf",
                        help="Name of input configuration file; "
                             "should be in JSON format with keys "
                             "for \"imply_fork_druid_docs\", "
                             "\"druid_imply_docs\", \"ignore_list\"")

    parser.add_argument("-o", "--output",
                        help="Name of the output text file")

    args = parser.parse_args()

    if not os.path.isfile(args.input_conf):
        sys.exit(f"\nERROR: Could not find input file {args.input_conf}\n")

    # do the main file checking and copying
    file_list = combine_druid_docs(args.input_conf, args.output)

    # tell vale not to lint the newly added druid docs
    fix_up_oss_docs(file_list)

if __name__ == "__main__":
    main()
