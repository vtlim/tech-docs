#!/usr/bin/python

"""
ui_copy.py

Version:        27 Feb 2025

Purpose:        Parses docs to pull out copy for the X UI
                Looks for content in the X docs folder
                for anything within Markdown comments
                {/* ui_label_start /*} and {/* ui_label_end /*}

Help:           python ui_copy.py --help

How to use:     python ui_copy.py
                (should be able to run from anywhere)

"""

import os
import re
import shutil
import sys

# figure out where I am
dir_path = os.path.dirname(os.path.realpath(__file__))

# input docs files
directory_path = os.path.join(dir_path, "../../x")

# output files
temp_output_dir = os.path.join(dir_path, "../../temp_ui_copy")

# reference file
ref_file = os.path.join(dir_path, "../../x_ui_copy.csv")
ref_content = "docs_file,label_ui_file,copy_text\n"

def grab_label(lines):
    label = ""
    label_end = ""

    # parse the label ID out of the Markdown comment, ex. hec_iam_token
    label_pattern_start = r"\{\/\*\s*ui_(.*?)_start\s*\*\/\}"
    label_pattern_end = r"\{\/\*\s*ui_(.*?)_end\s*\*\/\}"
    label_match_start = re.search(label_pattern_start, lines[0])
    label_match_end = re.search(label_pattern_end, lines[-1])

    if label_match_start:
        label = label_match_start.group(1)
    if label_match_end:
        label_end = label_match_end.group(1)

    # for each label ID, verify that the start and end matches
    if label != label_end:
        return {"status": False, "label": label, "label_end": label_end}
    else:
        return {"status": True, "label": label}


def parse_text(lines):

    # grab line numbers for start and end patterns
    start_locs = [i for i, line in enumerate(lines) if "_start" in line]
    end_locs = [i for i, line in enumerate(lines) if "_end" in line]

    # basic checks
    num_start = len(start_locs)
    num_end = len(end_locs)
    if num_start != num_end:
        return {"status": False, "num_start": num_start, "num_end": num_end}

    # get text in between lines
    copies = []
    for start, end in zip(start_locs, end_locs):

        # store the copy in the dictionary
        # including start and end comments
        this_copy = lines[start:end+1]
        copies.append(this_copy)

    # return successful result
    return {
        "status": True,
        "num_start": num_start,
        "num_end": num_end,
        "start_locs": start_locs,
        "copies": copies
    }

def resolve_links(copy):
    # TODO
    cleaned_copy = copy
    return cleaned_copy

def polish_copy(copy):
    # resolve any md links to html ones
    copy_resolved_links = resolve_links(copy)
    # turn it from list to string
    copy_string = "".join(copy_resolved_links)
    return copy_string

def write_snippet(output_dir, filename, copy_string):
    out_file = os.path.join(output_dir, filename)
    with open(out_file, "w") as outfile:
        outfile.write(copy_string)
        print(f"\tWrote {filename}")


# ------------------------------------------ #

# create a temporary output directory
if not os.path.exists(temp_output_dir):
    os.makedirs(temp_output_dir)

print(f"\n\n🏁 Looking for copy in\n{directory_path}\n")
for filename in os.listdir(directory_path):
    fn = os.path.join(directory_path, filename)

    # skip directories such as assets
    if os.path.isdir(fn):
        print(f"Skipped directory [{filename}]")
        continue

    print(f"Reading {filename}")
    with open(fn, 'r') as f:
        try:
            lines = f.readlines()
        except UnicodeDecodeError:
            print(f"!! Unable to read {filename}")
            continue

        # parse raw markdown text in the file
        parse_result = parse_text(lines)
        if not parse_result["status"]:
            num_start = parse_result["num_start"]
            num_end = parse_result["num_end"]
            sys.exit(f"\nERROR in {fn}: found {num_start} start lines and {num_end} end lines.")
        copies = parse_result["copies"]

        # iterate over each copy item in the file
        for copy in copies:

            # extract label from Markdown comment
            label_result = grab_label(copy)
            if not label_result["status"]:
                sys.exit(f"\nERROR in {fn}: error with label starting with "
                         f"[ {label_result['label']} ] and ending with "
                         f"[ {label_result['label_end']} ]")

            # format string for output
            copy_string = polish_copy(copy[1:-1])

            # generate the output file name
            # replace _ with - to satisfy iow filename-naming-convention check
            label_id = label_result['label']
            copy_file = label_id + '.md'
            copy_file = copy_file.replace("_", "-")

            # write output file
            write_snippet(temp_output_dir, copy_file, copy_string)

            # escape any " in the content to ""
            # do this for csv output only, not for md output
            copy_string = copy_string.replace("\"", "\"\"")

            # record in the reference doc
            ref_content += f"{filename},{copy_file},\"{copy_string}\""
            ref_content += "\n"

with open(ref_file, "w") as reffile:
    reffile.write(ref_content)
    print(f"\n🏁 Finished. See the list of results in x_ui_copy.csv")

#shutil.rmtree(temp_output_dir)
