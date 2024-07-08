## script to publish docs to s3
import argparse, json
import os, sys, subprocess

## configure docs location
## this is relative to `imply-docs/website/`
build_dir = '../build/'
root_dir = os.path.realpath(build_dir)

# Amazon S3 bucket & prefixes for Imply Docs site
bucket = 'static.imply.io'
s3info = {
    'stage':['_staging_docs-site', 'https://staging-docs.imply.io/'],
    'dev':['_dev_docs-site', 'https://dev-docs.imply.io/'],
    'prod':['_docs-site','https://docs.imply.io/']
}
published = []

def publishVersion(version, environment):
        source_dir = '%s/%s'%(root_dir, version)
        source_exists = os.path.exists(source_dir)
        if source_exists == True:
            prefix = s3info[environment][0]
            dest = f's3://{bucket}/{prefix}/{version}'
            print('Processing directory: %s.\n'%(version))
            print('Running the following:\n\n aws s3 sync --exact-timestamps --delete %s, %s\n'%(source_dir, dest))
            result = subprocess.run(['aws','s3', 'sync', '--exact-timestamps', '--delete', source_dir, dest])
            print("stdout:", result.stdout)
            print("stderr:", result.stderr)
            if version == "latest":
                print ("Publishing index for latest.\n")
                index = root_dir+'/index.html'
                indexDest = f's3://{bucket}/{prefix}/index.html'
                print('Running the following:\n\n aws s3 cp %s, %s\n'%(index, indexDest))
                result = subprocess.run(['aws','s3', 'cp', index, indexDest])
                print("stdout:", result.stdout)
                print("stderr:", result.stderr)
                print ("Publishing versions for latest.\n")
                enDir = root_dir+'/en/'
                enDest = f's3://{bucket}/{prefix}/en/'
                print(f'Running the following:\n\n aws s3 sync {enDir}, {enDest}\n')
                result = subprocess.run(['aws','s3', 'sync', enDir, enDest])
                print("stdout:", result.stdout)
                print("stderr:", result.stderr)
        else:
            print(f"\nCouldn't find source directory {source_dir}.\n")



if __name__ == "__main__":
    description = """
    Publish Imply Docs to S3.\n
    By default, the script publishes the docs versions to the development
    environment based upon a `pub_versions.conf` file within the
    `imply-docs/website/script` directory.\n
    The versions file is a JSON formatted list (array) of versions to publish.
    If you publish `latest` as a version, the script also publishes
    the top level Imply docs in `imply-docs/build/en`. Syntax:\n
    `{"versions":["2021.08", "2021.09", "latest"]}\n
    Assumes you have already run the appropriate build scripts and the docs to
    publish reside underneath `imply-docs/build/`.\n
    Default vaules assume you're running the script from within `imply-docs\website`.'
    """
    arg_parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    # Add the arguments
    arg_parser.add_argument('--conf', 
                    metavar='configuration_path',
                    type=str,
                    help='Path to the version configuration file. Default: ./script/pub_versions.conf',
                    default='./script/pub_versions.conf')
    arg_parser.add_argument('--env', 
                    metavar='s3_environment',
                    type=str,
                    help='S3 environment: development (dev) [default], staging (stage), or production (prod) .',
                    choices=['dev', 'stage', 'prod'],
                    default='dev')
    arg_parser.add_argument('--update_style',
                    help='Set --update_style to update /css and /img directories.',
                    action="store_true",
                    default=False)

    # Execute the parse_args() method
    args = arg_parser.parse_args()
    version_file = os.path.realpath(args.conf)
    versions = []
    try:
        with open(version_file, 'r') as conf:
            version_list = json.load(conf)
            versions = version_list["versions"]
    except:
        print("Couldn't open versions configuration:\n %s"%(version_file))
        sys.exit()
    environment = args.env

    print("Publishing versions:\n %s\nto %s.\n"%('\n '.join(versions), environment.upper()))
    if environment == 'prod':
        proceed = input("You have chosen to publish to production. Type 'OK' to continue: ").lower()
        if proceed == 'ok':
            print("\nPublishing production. Hold on to your hats!\n")
        else:
            print("Maybe next time.")
            sys.exit()

    # Loop through versions list and sync indivually to s3.
    for version in versions:
        try:
            publishVersion(version, environment)                    
            published.append((s3info[environment][1]+version))
        except:
            print ("Something went wrong for version %s. Try a manual sync.\n"%(version))
    
    # Update front matter if necessary
    if args.update_style:
        dirs = ['css', 'img']
        prefix = s3info[environment][0]
        for dir in dirs:
            source = f'{root_dir}/{dir}'
            dest = f's3://{bucket}/{prefix}/{dir}/'
            print(f'Running the following:\n\n aws s3 cp {source}, {dest}\n')
            result = subprocess.run(['aws','s3', 'cp', source, dest, '--recursive'])
    
    #Print published docs URLs
    print("\nDocs are available at:")
    for url in published:
        print(url)
                
        
        
        
