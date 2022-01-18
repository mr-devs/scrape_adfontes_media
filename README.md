# scrape_adfontes_media

This repo contains a script for scraping the [Ad Fontes Media Bias and Reliability chart](https://adfontesmedia.com/static-mbc/).

It relies on `Beautiful Soup 4` and outputs a CSV file where the columns are: source, reliability, and bias.

The script goes to [this page](https://adfontesmedia.com/rankings-by-individual-news-source/) - which links to all of the sources rated by Ad Fontes Media - and then follows each link to the page that contains the actual ratings. As a result, the Ad Fontes site will block the script for automated visits if not other precautions are taken. In order to avoid being IP blocked, the script implements a random wait period between 1 and 10 seconds before visiting each new page.

Ad Fontes says that they update their chart on a regular basis, so the script should probably be run once a month.