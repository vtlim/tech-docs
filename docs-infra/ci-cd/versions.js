//Variables are used in docs like this https://docs.imply.io/latest/apache-druid-doc/

/* The Druid version associated with the Imply Enterprise release.
Get this from the monthly release cluster.
Format is 202N.NN.N-iap */
const DRUIDVERSION = "2025.01.0-iap";

/* Version of the docs you're releasing, whether that's LTS or STS.
Examples: "2025.01", "2024.10.2", "2025.01-lts" "2024.01.15-LTS"
For the first release of an STS, there is no `.0` hotfix version.
For STS patches or hotfixes, it becomes 202N.NN.NN */
const IMPLYVERSION = "2025.01";

/* STS OR LTS version without the hotfix, so 2024.02 or 2024.01-lts.
Used for third-party license page and top nav version.
This is what we use for the URL path. */
const BASEVERSION = "2025.01";

/* Kind of like BASEVERSION but stripped down further without '-lts' suffix.
Used for the download link for LTS Imply Manager */
const LTSMANAGER = "2025.01";

/* If true, build docs for BASEVERSION, latest, and polaris.
Latest STS must republish Polaris so the Polaris docs top nav shows the correct STS version. */
const build_latest = true;

/* Agent for Imply Manager. Not updated very often */
const imply_agent = "7";

module.exports = {
  DRUIDVERSION,
  IMPLYVERSION,
  BASEVERSION,
  LTSMANAGER,
  build_latest,
  imply_agent
};
