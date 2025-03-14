#!/usr/bin/python

"""
ui_copy.py

Version:        12 Mar 2025

Purpose:        Scrapes docs to pull out copy for the IOW UI
                Looks for content in the Lumi docs folder
                for anything within Markdown comments
                {/* ui_label_start /*} and {/* ui_label_end /*}

How to use:     $ python ui_copy.py
                (run from anywhere)

                $ python ui_copy.py --crossref
                (to crossref against IOW code, assumes you have
                the iow repo at the same level at imply-docs-saas)

TODO:           Link to docs file in CSV
                Link to UI file in CSV

"""

import csv
import os
import re
import shutil
import sys


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

    # trim leading or trailing newlines
    copy_string = copy_string.rstrip().lstrip()

    return copy_string


def write_snippet(output_dir, filename, copy_string):
    out_file = os.path.join(output_dir, filename)
    with open(out_file, "w") as outfile:
        outfile.write(copy_string)
        print(f"\tWrote {filename}")

def process_grep_results(results_list, search_term):
    # split results by filename
    processed = results_list.decode('ascii').split(search_term)
    # remove leading or trailing whitespace
    processed = [x.lstrip().rstrip() for x in processed]
    # remove everything after : in the string
    processed = [re.sub(':.*$', '', x, flags=re.MULTILINE) for x in processed]
    # remove everything before 'iow' in the string
    processed = [re.sub('^.*iow', 'iow', x, flags=re.MULTILINE) for x in processed]
    # only consider the react files
    processed = [x for x in processed if x[-4:]=='.tsx']
    # TEMP TODO -- for now drop dir path and keep filename only
    processed = [re.sub('^.*/', '', x, flags=re.MULTILINE) for x in processed]
    # convert list of filename(s) to string then return
    processed = ' '.join(processed)
    return processed


def crossref(dir_path, latest_output):
    import subprocess
    label_code = {}
    print(f"\n\n✨ Cross-referencing labels in iow/ui-app\n")

    # location of ui-app in iow repo
    iow_repo = os.path.join(dir_path, "../../../iow")
    if not os.path.exists(iow_repo):
        sys.exit(f"ERROR: Can't find iow repo {iow_repo}")

    for line in latest_output[1:]:
        tokens = line.split(',')
        # get label
        label = tokens[0] + tokens[1]
        # get name of react component
        words = tokens[1].split('_')
        react_name = ''.join(map(str.capitalize, words))

        # define search parameters
        search_term = '<' + react_name + ' />'
        search_loc = iow_repo + '/ui-app'
        print(f"Searching for '{search_term}'")

        # look for where it's used
        try:
            results = subprocess.check_output(f"grep -r '{search_term}' {search_loc}", shell=True)
            # clean up results
            processed = process_grep_results(results, search_term)
            label_code[label] = processed
            print("\tFound in", processed)
        except subprocess.CalledProcessError:
            continue

    return label_code

def write_csv(dir_path, ref_file, ref_content, do_crossref):

    #file exists and crossref
    #file exists, no crossref
    #file !exist and crossref
    #file !exist, no crossref

    def update_ui_files(ref_content, crossref_dict):
        # update new content with existing ui_files
        ref_content2 = ["doc_file,label,ui_file,copy_text"]
        for line in ref_content[1:]:
            new_tokens = line.split(',')
            # check if this label is in dict
            new_ids = new_tokens[0] + new_tokens[1]
            # if yes, always use the dict version
            # (either value from file or iow crossref)
            if new_ids in crossref_dict:
                new_tokens[2] = crossref_dict[new_ids]
            # regenerate the string
            update_line = ','.join(new_tokens)
            ref_content2.append(f'{update_line}')

        return ref_content2


    # if file exists, get the existing list of ui_files
    ref_exists = os.path.exists(ref_file)
    if ref_exists:

        f = open(ref_file, 'r')
        csv_file = list(csv.reader(f))[1:]
        f.close()

        # get list of existing ui_files
        label_code_file = {}
        for tokens in csv_file:
            ids = tokens[0] + tokens[1]
            code = tokens[2]
            label_code_file[ids] = code

        ref_content = update_ui_files(ref_content, label_code_file)


    # if crossref, compare with iow code
    if do_crossref:
        # get the list of cross-referenced files
        label_code_crossref = crossref(dir_path, ref_content)
        ref_content = update_ui_files(ref_content, label_code_crossref)

    # if both conditionals were false, ref_content is same output as scrape_docs
    with open(ref_file, "w") as f:
        output_string = "\n".join(ref_content)
        f.write(output_string)
    print(f"\n🏁 Finished. See the list of results in lumi_ui_copy.csv")

# ------------------------------------------ #

def scrape_docs(dir_path):

    # prep content for csv reference file
    ref_content = ["doc_file,label,ui_file,copy_text"]

    # input docs files
    directory_path = os.path.join(dir_path, "../../lumi")
    if not os.path.exists(directory_path):
        sys.exit(f"ERROR: Can't find input docs folder {directory_path}")

    # create a temporary output directory
    temp_output_dir = os.path.join(dir_path, "../../temp_ui_copy")
    if not os.path.exists(temp_output_dir):
        os.makedirs(temp_output_dir)

    print(f"\n\n✨ Extracting copy from {directory_path}\n")
    file_list = sorted(os.listdir(directory_path))
    for filename in file_list:
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

                # record for the reference doc
                # wrap copy_string in quotation marks for newlines
                ref_content.append(f"{filename},{label_id},--,\"{copy_string}\"")

    #shutil.rmtree(temp_output_dir)
    return ref_content





def main():
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument("--crossref",
                        default=False,
                        action='store_true',
                        help="Cross-reference copy between docs and UI code.\
                              Assumes you have the IOW repo at the same\
                              location as imply-docs-saas."
                       )

    args = parser.parse_args()

    # figure out where the script lives
    dir_path = os.path.dirname(os.path.realpath(__file__))

    # name the output reference file
    ref_file = os.path.join(dir_path, "../../lumi_ui_copy.csv")

    # scrape docs
    ref_content = scrape_docs(dir_path)

    # write the output
    write_csv(dir_path, ref_file, ref_content, args.crossref)

if __name__ == "__main__":
    main()

