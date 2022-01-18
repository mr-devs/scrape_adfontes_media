"""
Purpose: Scrape the Ad Fontes Media Bias and Reliability chart.
    - Reference: (https://adfontesmedia.com/static-mbc/).

How it works:
The script visits a single source page - which links to all of the sources rated by Ad Fontes
Media - and then follows each link to the page that contains the actual ratings. As a result,
the Ad Fontes site will block the script for automated visits if not other precautions are taken.
In order to avoid being IP blocked, the script implements a random wait period between 1 and 10
seconds before visiting each new page. As a result, the script takes a while to complete and
should be run in the background.

Output:
- A CSV file where the columns are: source, reliability, and bias.

Ad Fontes says that they update their chart on a regular basis, so the script should probably be run once a month.
"""
import random
import requests
import time
from collections import defaultdict

import pandas as pd
from bs4 import BeautifulSoup


SOURCE_WEB_PAGE = "https://adfontesmedia.com/rankings-by-individual-news-source/"

def extract_name_and_link(a_object):
    """
    Get the source name and url if it's present.

    Parameters:
    ----------
    - a_object (bs4.element.Tag - `a`) : an a object html tag parsed by beautiful soup 4

    Returns:
    ----------
    - source_name (str) : the plain text source name as included by Ad Fontes Media
    - link (str) : the url location where Ad Fontes Media stores the reliability and bias data
    """
    if (a_object is not None) and (a_object["href"] is not None) and (a_object["href"].startswith("https://adfontesmedia.com")):
        source_name, link = a_object.get_text(), a_object["href"]
        source_name = source_name.replace(" Bias and Reliability", "")
        return source_name, link
    else:
        return None, None


def get_all_rated_sources():
    """
    Collect all of the rated sources and the url location where Ad Fontes Media
    stores the reliability and bias data.

    Return:
    ---------
    - rated_sources (list of tuples) : a list of tuples of the following form
        [(site_name1, site_url1), (site_name2, site_url2), ...]
    """
    print("Extracting links for the rated sources...")
    html_text = requests.get(SOURCE_WEB_PAGE).text
    soup = BeautifulSoup(html_text, 'html.parser')
    
    rated_sources = []
    for item in soup.find_all("h2"):
        a_obj = item.find("a")
        source_name, link = extract_name_and_link(a_obj)
        if (source_name is not None) and (link is not None):
            rated_sources.append( (source_name, link) )
    
    return rated_sources


def get_reliability_and_bias_info(rated_sources):
    """
    Visit and extract the rated sources gathered from As Fontes.
    
    Parameters:
    ----------
    - rated_sources (list of tuples) : a list of tuples of the following form
        [(site_name1, site_url1), (site_name2, site_url2), ...]

    Returns:
    ---------
    - scraped_info (defaultdict) : a dictionary of the following form
        {'site 1': {'reliability': XXX, 'bias': XXX},
         'site 2': {'reliability': XXX, 'bias': XXX},
         ....
        }
    """
    num_sites_2_scrape = len(rated_sources)
    sitecount = 0

    scraped_info = defaultdict(dict)

    print(f"Extracting reliability and bias scores from {num_sites_2_scrape} sites")
    for site_name, site_url in rated_sources:
        random_num_seconds = random.randrange(1,10)
        print(f"Waiting for {random_num_seconds} seconds so we don't get blocked.")
        time.sleep(random_num_seconds)

        html_text = requests.get(site_url).text
        html_soup = BeautifulSoup(html_text, 'html.parser')

        if sitecount % 25 == 0:
            print(f"{sitecount} sites processed...")
        sitecount += 1

        for item in html_soup.find_all("p"):

            rating = item.find("strong")
            if (rating is not None) and (":" in rating.get_text()):
                split_metric = tuple(rating.get_text().split(": "))
                metric_name, metric_score = split_metric[0].lower(), float(split_metric[1])

                scraped_info[site_name].update({
                    metric_name : metric_score
                })

    return scraped_info


if __name__ == "__main__":
    
    rated_sources = get_all_rated_sources()
    scraped_info = get_reliability_and_bias_info(rated_sources)
    scraped_info_df = pd.DataFrame.from_dict(scraped_info, orient="index").reset_index()
    scraped_info_df = scraped_info_df.rename(columns = {"index":"source"})
    scraped_info_df.to_csv("ad_fontes_media_sources_ratings.csv", index=False)
    print("--- Script Complete ---")