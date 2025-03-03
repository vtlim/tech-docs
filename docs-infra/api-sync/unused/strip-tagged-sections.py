#!/usr/bin/python

"""
strip-tagged-sections.py

Purpose: Remove sections of OpenAPI spec that are associated
    with a certain custom tag.

Example: python strip-tagged-sections.py
            -i <input.yaml> -t <custom-tag> -o <output.json>
"""

import copy
import json
import operator
import os
import sys
import yaml

from functools import reduce


# modified from https://stackoverflow.com/a/47911802
def delete_key_path(dictionary, key_list):
    *path, key = key_list
    del reduce(operator.getitem, path, dictionary)[key]
    return dictionary

# modified from https://stackoverflow.com/a/50444005
def gen_dict_extract(var, tag, upper_key=[]):
    if isinstance(var, dict):
        for k in reversed(var.keys()):
            if k == tag:
                yield upper_key
            if isinstance(var[k], (dict, list)):
                yield from gen_dict_extract(var[k], tag, upper_key + [k])
    elif isinstance(var, list):
        for d in reversed(var):
            yield from gen_dict_extract(d, tag, upper_key)


def strip_tagged(input_spec, tags_list, output):

    # open and parse the input file
    with open(input_spec, "r") as stream:
        try:
            content = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            sys.exit(exc)

    # collect paths for components to delete
    paths_to_del = []
    for tag in tags_list:
        paths_to_del.append(list(gen_dict_extract(content, tag)))
    paths_to_del = [item for sublist in paths_to_del for item in sublist]

    # delete marked components
    new_content = copy.deepcopy(content)
    for p in paths_to_del:
        new_content = delete_key_path(new_content, p)

    # write out the new file
    with open(output, "w") as f:
        json.dump(new_content, f, indent=2)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Remove sections containing "
                        "the specified tags from an OpenAPI specification. "
                        "Generates a JSON version of the OpenAPI spec. "
                        "Example: python strip-tagged-sections.py "
                        "-i openapi.yaml -t x-docs-internal "
                        "-o openapi_stripped.json")

    parser.add_argument("-i", "--input-spec",
                        help="Name of input OpenAPI specification")

    parser.add_argument('-t', '--tags', action='store', dest='tags_list',
                        type=str, nargs='*',
                        help="Tag(s) labeling parts to remove from spec. "
                             "Example: -t x-internal x-docs-internal")

    parser.add_argument("-o", "--output",
                        help="Name of the output OpenAPI specification")

    args = parser.parse_args()

    if not os.path.isfile(args.input_spec):
        sys.exit(f"\nERROR: Could not find input file {args.input_spec}\n")

    strip_tagged(args.input_spec, args.tags_list, args.output)

if __name__ == "__main__":
    main()
