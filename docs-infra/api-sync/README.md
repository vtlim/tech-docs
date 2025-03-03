<!-- markdownlint-disable MD029 MD033 -->

# Imply API Docs

This repo contains the Imply API docs. These docs run on [Redoc](https://redocly.com/redoc/). For further information, also see [Confluence: Redoc for API docs](https://implydata.atlassian.net/wiki/spaces/DOCS/pages/2497347611/Redoc+for+API+docs).

## Quickstart

```sh
# Clone this repo
git clone https://github.com/implydata/imply-docs-api.git

# Install dependencies in the freshly cloned repository
cd imply-docs-api
npm install

# Start the site
npm run preview-docs
```

To view all available `npm` commands: `npm run`

## Quick guide to publishing

Use this commands to generate the Polaris API reference docs from their respective source repositories
and publish the resulting HTML file to the staging site.

To publish to dev or prod, replace the [bucket name](https://implydata.atlassian.net/wiki/spaces/DOCS/pages/2604794241/Upload+a+single+file+to+AWS#Bucket-names).

Run these commands in the root directory of the repo, `imply-docs-api`.

```sh
GITHUB_OAUTH_TOKEN="<TOKEN>" npm run sync
npm run publish
aws s3 cp website/polaris/api-reference.html s3://static.imply.io/_staging_docs-site/api/polaris/api-reference.html
```

## Longer guide to preview and publish

### Visual overview

The following diagram shows an overview of publishing docs using this project:

![Redoc workflow](workflow.png)

### Merge OpenAPI specs

At the moment, there isn't a single location containing the Polaris Published API spec. Therefore, we gather the various spec files from various repositories on GitHub and merge them into one file. The references to those files are defined in `scripts/sync` (this is the same process as [`imply-ui's apis package`](https://github.com/implydata/imply-ui/tree/master/packages/apis)).

The merged output is committed to source control at `schemas/merged-upstream-openapi.yaml`.

#### Option 1: Sync from remote GitHub repos

To update the merged schemas:

1. If you haven't already, visit <https://github.com/settings/tokens> and generate a new personal access token with the `repo` scope. Store this in a safe place, like a password manager. It will be needed in Step 4.

2. Prepare your configuration files based on the API docs to generate. Run one of the following commands:

```sh
npm run preprocess:polaris
npm run preprocess:manager
```

2. In `scripts/sync`, update the commit hash for the GitHub repositories from where the spec files will be downloaded.
   1. Go to the [`imply-cloud` commits](https://github.com/implydata/imply-cloud/commits/master).
   2. Copy the SHA for the latest (or specific) commit to sync.
   3. Update the variable for `imply_cloud_revision`.
   4. Repeat these steps for [`imply-ui`](https://github.com/implydata/imply-ui/commits/master) and [`saas-services`](https://github.com/implydata/saas-services/commits/main).

4. Run the following command:

```sh
GITHUB_OAUTH_TOKEN="<your_personal_access_token>" npm run sync
```

#### Option 2: Sync from local GitHub repos

1. Prepare your configuration files based on the API docs to generate. Run one of the following commands:

```sh
npm run preprocess:polaris
npm run preprocess:manager
```

2. Ensure that you have a local copy of these repos: `imply-docs-api`, `imply-cloud`, `imply-ui`, `saas-services`.
   * Store these repos in the same location.
   * Pull the latest updates for each.

3. Run the following command:

```sh
npm run sync-local-polaris
```

Any schema changes should be reflected in `schemas/merged-upstream-openapi.yaml`, which you can now review.

<details>
<summary>Click for more details on internal processing of the OpenAPI schema</summary>

The merged OpenAPI schema (`schemas/merged-upstream-openapi.yaml`) is further processed using `openapi-merge-cli` and the `redocly-cli`.

The processing step currently creates two files in the `dist/` folder: `external.yaml` and `internal.yaml`. The `external.yaml` is stripped of all APIs marked as `x-internal`, whereas the `internal.yaml` contains the specification to all API endpoints. For more information on removing `x-internal`, see [Hide your internal APIs](https://redocly.com/docs/cli/guides/hide-apis/).

To bundle and process the upstream version of the OpenAPI schema:

```sh
npm run bundle:all
```

Note that you generally never need to call this command, since it's automatically run when you call `npm run publish` or `npm run preview-docs`.
</details>

### Preview Redoc documentation

With the OpenAPI specification merged and bundled, we are ready to load the spec into Redoc.

To preview the documentation locally:

```sh
npm run preview-docs
```

For whatever reason that you want to preview only the bits marked `x-internal`, use `npm run preview-docs:internal`.

### Generate Redoc documentation for publication

To generate the output HTML reference doc:

```sh
npm run publish
```

## How to add new API to the Polaris API reference

From the `scripts` folder of the `imply-docs-api` repo, make the following changes to add a new API to the Polaris reference docs.

1. Edit the `sync` script to add a new `download_schema` line within the Polaris `elif` block.
The `download_schema` line uses the following syntax:

```sh
download_schema "REPO-NAME" $REPO_revision "FULL/PATH/TO/API/FILE/IN/REPO.yaml" > upstream/OUTPUT-NAME.yaml
```

The output name of the file is used as a temporary file. Be sure that it is unique so that it doesn't overwrite another Polaris API.
Your new line should look something like this.

```sh
$sync_method "imply-ui" $imply_ui_revision "packages/apis/schemas/embed.yaml" > $UPSTREAM_DIR/pivot/embed.yaml
```

2. Edit the `sync-polaris.json` file to include a new section for `OUTPUT-NAME.yaml`.
Whether or not you need the `prepend` path depends on how the `paths` are defined in the OpenAPI spec, such as `/v2/tables` or `/tables`.
   > The order you add the new section will dictate the ordering of how the new API is displayed in the left navigation of the reference docs.

3. Add the new API to the [Polaris introduction Markdown file](https://github.com/implydata/imply-docs-api/blob/master/docs/polaris/introduction.md).

4. Take a look at the new OpenAPI spec. Look at the `$ref` lines. If any of these point to another YAML file, add the following line within the `sync` script.
   Otherwise, when previewing or publishing the docs, you will get an error similar to `Can't resolve $ref: ENOENT: no such file or directory`.

   1. Add this line in `sync`. Replace `embed` with your YAML file name.
   ```
   npx -y @redocly/cli bundle $UPSTREAM_DIR/embed.yaml         --output $UPSTREAM_DIR/embed_bundled.yaml
   ```

   2. Redo step 2, and update `sync-polaris.json` with the bundled file name, like `embed_bundled.yaml`.

 
4. Run the steps in [Merge OpenAPI specs](#merge-openapi-specs).

5. Build and preview the docs.
   1. To see the reference docs using the OpenAPI specs directly from GitHub, call `npm run sync` and `npm run publish`.
   2. To see the reference docs based on the local versions of the files, first
      ensure you have these repos in the same folder as `imply-docs-api` and that they are all up-to-date:
       * `imply-cloud`
       * `imply-ui`
       * `saas-services`

      Call `npm run sync-local-polaris` and `npm run publish`.

6. View the generated file in your browser. For example, `open website/polaris/api-reference.html`.

## How to add new API specs

To add a new __set__ of API docs to this package, you need to add a few configuration files and commands.
Follow the steps below, updating `newdoc` to a pattern that you choose (just be consistent!).

1. Edit the `scripts/sync` script to add a new download command in the `if/else` block before `fi`.
The `download_schema` function is in the sync script and requires the GitHub repo name, commit hash, and path.
The new snippet should look something like this:

```sh
if [[ "$api_docs" = "newdoc" ]] ; then

  # Public Manager API
  download_schema "imply-cloud" $imply_cloud_revision "aws/src/main/resources/openapi/clusters.yaml" > upstream/clusters.yaml
```

2. Create a JSON file in `scripts` called `sync-newdoc.json`.
List all the input files, and name the output file `merged-upstream-newdoc.yaml`.
The JSON file can only accept relative paths, relative to `scripts`.
This file gets called by `merge-local` as a prerequisite to publishing.
The JSON file should look something like this:

```json
{
  "inputs": [
    {
      "inputFile": "./upstream/clusters.yaml"
    }
  ],
  "output": "../schemas/merged-upstream-newdoc.yaml"
}
```

3. Create a file in `schemas` called `intro-newdoc.yaml`.
Provide a title and description for the API reference docs.
Example:

```yaml
openapi: 3.0.3
info:
  title: Imply New Docs API
  version: 1.0.0
  description: |-
    Imply's new API lets you do x, y, and z.
```

This YAML file can reference a Markdown file.
If you decide to write intro content in a separate Markdown file,
create the file in `docs` and properly reference it, such as the following snippet:

```yaml
  description:
    $ref: ../docs/polaris/introduction.md
```

4. Edit `package.json` to add a line to `scripts`. It should look something like this:

```json
"preprocess:newdoc": "scripts/preprocess newdoc",
```

5. Run the sync, merge, and publish process as usual. For example:

```sh
npm run preprocess:newdoc
npm run publish
```

6. Aside from the new configuration and docs created from the steps above, you should have the new files generated:

* `schemas/merged-upstream-newdoc.yaml`
* `website/newdoc/api-reference.html`

## Contents

The `imply-docs-api` repo contains the following structure:

```text
.
├── README.md
├── _old                                Manager API reference docs using openapi-generator + Docusaurus v1
│   ├── docs                            reference docs in Markdown format
│   ├── openapi-generator               scripts and templates to generate the old version of API docs
│   ├── openapitools.json               config called by openapi-generator-cli
│   ├── specs                           OpenAPI YAML file used to generate docs
│   ├── stubs                           Markdown snippets imported in other docs
│   └── website
├── dist                                intermediate YAML files generated by redocly; not checked into GitHub
│   ├── manager
│   └── polaris
├── docs                                Markdown files to reference from schemas/intro-*.yaml
│   └── polaris
├── node_modules
├── package-lock.json
├── package.json                        npm dependencies and project settings including "npm run <command>" scripts
├── redocly.yaml                        redocly config to strip x-internal components
├── schemas                             OpenAPI specs from GitHub (-upstream-) and merged with local specs (-docs-)
│   ├── intro-manager.yaml
│   ├── intro-polaris.yaml
│   ├── merged-upstream-manager.yaml
│   └── merged-upstream-polaris.yaml    -upstream- YAML generated from component specs using sync script
├── scripts                             scripts called via "npm run <command>"
│   ├── merge-local
│   ├── merge-local.json
│   ├── postprocess
│   ├── preprocess
│   ├── strip-resolved-tags.js
│   ├── sync
│   ├── sync-manager.json
│   └── sync-polaris.json
└── website                             contains HTML output from redoc-cli via "npm run publish"
    ├── build
    ├── manager
    ├── node_modules
    ├── plugins
    ├── polaris
    └── static
```

The Markdown source for the Cloud Manager API lives in this repo in `_old`.
We don't want to remove these yet since the docs add some information that aren't in (but should be moved to) the source specs.

These docs were built with Docusuaurus v1 and haven't been updated since their addition.
See changes (e.g, formatting or link fixes) in the `imply-docs` repo [here](https://github.com/implydata/imply-docs/tree/main/published_versions/api/manager).
