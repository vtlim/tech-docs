import errno
import os
import subprocess

"""
Use this script to upload a single updated published file to the docs site.
For example, if you update a single file called sql-operators.md, the updated
build files will be sql-operators.html and sql-operators/index.html.
This script automates uploading both files to the docs site and for
multiple doc versions, such as latest and 2023.01.

Syntax:
python publish_select.py -n <FILENAME NO EXTENSION> -v <VERSION(S)> [--production]

Examples:
python3 ../../website/script/publish_select.py -n druid/querying/sql-operators  -v latest 2023.01
python3 ../../website/script/publish_select.py -n druid/querying/sql-operators  -v latest 2023.01 --production

Notes:
- Run the script from a build directory, for example:
  https://github.com/implydata/imply-docs/tree/main/published_versions/2023.01
- Do not specify './' or '../' in the -n option since aws will create a literal
  path of '.' or '..' and will not upload your file to the correct location.

"""

def main(fname, versions, production):

    path_prefix = "s3://static.imply.io/"

    if production:
        bucket_name = "_docs-site/"
    else:
        bucket_name = "_staging_docs-site/"

    files_to_upload = [f"{fname}.html", f"{fname}/index.html"]
    for f in files_to_upload:
        if not os.path.exists(f):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), f)

        for v in versions:
            dest = f"{path_prefix}{bucket_name}{v}/{f}"
            full_cmd = ["aws", "s3", "cp", f, dest]
            print("Running the following command:\n", *full_cmd)
            result = subprocess.run(full_cmd)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument("-n", "--name",
        help="Filename to upload. For example, '-n versions' will "
             "update 'versions.html' and 'versions/index.html'")

    parser.add_argument("-v", "--versions", nargs="+",
        help="Versions of the doc to update. Multiple arguments "
             "accepted. For example, '-v latest 2023.01'")

    parser.add_argument("--production", action="store_true", default=False,
        help="Specify to publish to production, otherwise files are uploaded "
             "to staging.")

    args = parser.parse_args()
    main(args.name, args.versions, args.production)
