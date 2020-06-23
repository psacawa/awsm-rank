#!/usr/bin/env python3.7
import re
import argparse
import asyncio
from pprint import pprint

import aiohttp
import requests
from bs4 import BeautifulSoup

def main():
    """Scrape and parse a github page. For all linked github projects, determine the number
    of stars asynchronously. Order the results by decreasing number of stars."""
    parser = argparse.ArgumentParser ()
    parser.add_argument ('url', type=str)
    args = parser.parse_args()

    projects = get_linked_projects(args.url)

def get_linked_projects(url):
    """get github projects linked a given webpage"""
    response = requests.get (url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a')
    links = [a['href'] for a in links]
    pattern = r'^https://github.com/\w+/[^/]+$'
    #  pattern = r'^https://github.com'
    prog = re.compile(pattern).search
    links = list (filter (prog, links))
    return  links

    
if __name__ == "__main__":
    main()
