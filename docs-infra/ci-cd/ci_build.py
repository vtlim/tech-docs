#!/usr/bin/python

"""
ci_build.py

Version:        28 Feb 2025

Purpose:        Build the Imply docs for Polaris and Enterprise.
                https://implydata.atlassian.net/wiki/spaces/DOCS/pages/1146683404/Developing+the+docs

Process:        1. Open imply-docs-saas/website/static/js/versions.js
                2. Ensure the versions are up to date.
                3. If you're publishing the latest STS or Polaris, ensure `build_latest` is true.

Variables:      Set build_latest=false, to only publish content in docs folder (202x.xx)
                Set build_latest=true,  to publish 202x.xx and `latest/` AND polaris AND
                the individual pages for home, version, search, lifecycle, 404.

Help:           python ci_build.py --help

Manual build:   python script/ci_build.py --manual
                Build manually for previously released versions.
                Remember to update versions.js beforehand.

"""

import fileinput
import os
import re
import shutil
import subprocess
import sys

def add_auth():
    """
    Adds auth for Lumi docs for publishing

    Root.js adds the auth component to every page in docusaurus. It lives as
    an unused file named authfile so that when we do yarn start, auth doesn't get loaded
    For builds that use the build script (e.g. for publishing), the file gets renamed
    so that auth gets added to every page
    """
    try:
        os.rename('./src/theme/authfile', './src/theme/Root.js')
        print("File renamed from authfile to Root.js to add auth.")
    except FileNotFoundError:
        print("Error: Couldn't find ./website/src/theme/authfile.")

def revert_auth():
    """
    Removes auth for Lumi docs for working
    """
    try:
        os.rename('./src/theme/Root.js', './src/theme/authfile')
        print("File renamed from Root.js to authfile to remove auth..")
    except FileNotFoundError:
        print("Error: Couldn't find ./website/src/theme/Root.js.")


def tpl_links(restore_text=""):
    """
    Removes links from third-party licenses, except for download.
    Set restore_text to the text to be restored.
    The text was returned from the first run of this function.

    Imply third-party software licenses
    is generated from a script, but has many broken links.
    https://docs.imply.io/latest/third-party-licenses/
    """

    # check for the file
    filename = '../enterprise/third-party-licenses.md'
    if not os.path.exists(filename):
        print("Error: Can't find third-party-licenses.md")
        return

    # restore the file to what it was before the build
    if restore_text != "":
        with open(filename, "w") as f:
            f.write(restore_text)
        return

    print("hi")
    # read the file
    with open(filename) as f:
        orig_str = f.read()

    # regex replacement
    new_str = re.sub(r'](.*)\)', '', orig_str)
    new_str = re.sub(r'\| \[', '| ', new_str)

    # write the file
    with open(filename, "w") as f:
        f.write(new_str)
        return orig_str

def build_docs(v, use_yarn):
    """
    Builds the docs for a specified version v.
    """

    print(f"Building the docs for version '{v}'...")

    # update redirects to replace "latest" to the version being built
    if v != "latest":
        for line in fileinput.input("redirects.js", inplace=1):
            print(line.replace("/latest/", f"/{v}/"), end='')

    # set this version in "buildVersion" variable in docusaurus.config.js
    # buildVersion != base version since it can be `latest` or the base version
    replacement = f'var buildVersion = "{v}";'
    for line in fileinput.input("./docusaurus.config.js", inplace=1):
        print(re.sub(r"^var buildVersion.*", replacement, line), end='')

    # build the docs
    if not use_yarn:
        subprocess.run(["npm", "run", "build"])
    else:
        subprocess.run(["yarn", "build"])

    # move output to temporary directory since docusaurus 2
    # overwrites build directory with each build.
    if not os.path.isdir("build"):
        sys.exit("ERROR: The docs were not built. Check Docusaurus logs.")
    shutil.copytree("build", "build__temp", dirs_exist_ok=True)

    # restore the redirect file back to URLs with "latest"
    if v != "latest":
        for line in fileinput.input("redirects.js", inplace=1):
            print(line.replace(f"/{v}/", "/latest/"), end='')


def get_version(is_manual):
    """
    Determines what STS version of the doc to build
    and whether to also build the latest version.
    """

    # open the versions.js file
    try:
        f = open("static/js/versions.js", "r")
    except FileNotFoundError:
        sys.exit("Error: Can't find static/js/versions.js. "
            "Are you in the website directory?\n")

    # read the variables
    # assumes that BASEVERSION is before build_latest
    print("\n-----------------------------------")
    print("Variables from versions.js:")
    lines = f.readlines()
    for l in lines:
        if l.startswith("const BASEVERSION"):
            print(l, end="")
            match = re.search(r'"(.*?)"', l)
            base_version = match.group(1)
        if l.startswith("const build_latest"):
            print(l)
            if "true" in l.lower():
                build_latest = True
            else:
                build_latest = False
            break

    # generate the versions list
    # the "latest" version is built last to maintain the non-docs content
    versions = [str(base_version)]
    if build_latest:
        versions.append("latest")

    # confirm with writer
    if is_manual:
        confirm_text = "-----------------------------------\n"
        confirm_text += f"Confirm these versions to build: {versions}\n"
        confirm_text += "Does this look correct? (y/n) "
        proceed = input(confirm_text).lower()
        if proceed != 'y':
            sys.exit("The versions were not confirmed. Exiting.")

        if build_latest:
            proceed_latest = input("/latest will also be built. Confirm (y/n) ")
        else:
            proceed_latest = 'y'
        if proceed_latest != 'y':
            sys.exit("The versions were not confirmed. Exiting.")

        print("\nProceeding with build...\n")

    return versions


def main(do_install, use_yarn, is_manual):
    """
    Orchestrates collecting versions and building docs
    for each of those versions. Does file management with
    with the build directory.
    """

    # rename authfile to Root.js
    add_auth()

    # removes links in third-party-licenses
    # do this before build to not repeat for every version
    prev_text = tpl_links()

    # get version(s) from version.js. if latest is included,
    # it's last in order to maintain the non-docs content
    versions = get_version(is_manual)

    # install docusaurus 2
    if do_install:
        print("Installing Docusaurus 2...")

        if not use_yarn:
            subprocess.run(["npm", "install"])
        else:
            subprocess.run(["yarn", "install"])

    # remove the old build directory before building anew
    shutil.rmtree('build', ignore_errors=True)

    # do the actual build
    for v in versions:
        build_docs(v, use_yarn)

    # after all version builds, rename the temp directory back to "build"
    shutil.rmtree("build")
    shutil.move("build__temp", "build")

    # rename Root.js back to authfile
    revert_auth()

    # undo the tpl links
    tpl_links(prev_text)


if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument("--install", default=False,
                        help="Install Docusaurus 2 before building. Uses npm "
                             "by default, unless you call --yarn",
                        action='store_true')

    parser.add_argument("--yarn", default=False,
                        help="Use yarn to install and build instead of npm",
                        action='store_true')

    parser.add_argument("--manual", default=False,
                        help="Set this flag when you're building manually. "
                        "Otherwise assumes this script is used in automation.",
                        action='store_true')

    args = parser.parse_args()

    main(args.install, args.yarn, args.manual)
