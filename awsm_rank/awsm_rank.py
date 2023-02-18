#!/usr/bin/env python3
import argparse
import asyncio
import json
import logging
import re
import subprocess
import sys
import typing
import webbrowser
from os import environ
from pprint import pprint
from typing import List
from urllib.parse import urlparse

import requests
import shtab
from aiohttp import ClientError, ClientSession
from bs4 import BeautifulSoup
from tabulate import tabulate

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

GITHUB_TOPLEVEL_PATH_BLACKLIST = ["apps", "site", "topics"]


def get_parser():
    """Generate ArgumentParser object"""
    parser = argparse.ArgumentParser()
    #  shell completions with shtab
    shtab.add_argument_to(parser, ["-s", "--print-completion"])
    parser.add_argument("url", type=str)
    parser.add_argument("--token", type=str)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--debug", dest="debug", action="store_true")
    parser.add_argument("--open", dest="open", action="store_true")
    return parser


def main():
    """Scrape and parse a github page. For all linked github projects, determine the number
    of stars asynchronously. Order the results by decreasing number of stars.
    Authentication can be provided by the GITHUB_API_TOKEN environmental variable, or
    preferentially via the --token argument. If not given, am unauthenticated query will
    be attempted.
    """
    parser = get_parser()
    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)

    token = environ.get("GITHUB_API_TOKEN", None) or args.token
    logger.debug(f"Using authentication token: {token}")

    repo_endpoints = get_repo_api_endpoints(args.url)
    ranking = asyncio.run(get_stargazer_counts(repo_endpoints, token=token))
    if args.limit:
        ranking = ranking[: args.limit]
    if args.open:
        open_urls(ranking)
    else:
        print_ranking(ranking)


def print_ranking(ranking):
    #  don't display urls
    for item in ranking:
        item.pop("url")
    print(tabulate(ranking, headers="keys"))


def open_urls(ranking):
    """Open the urls in the ranking in firefox. Add option to choose the web browser?"""
    urls = [item["url"] for item in ranking]
    for url in urls:
        webbrowser.open_new_tab(url)


def get_repo_api_endpoints(main_url: str):
    """Get github projects linked in a given webpage"""
    #  get list of links
    response = requests.get(main_url)
    soup = BeautifulSoup(response.text, "html.parser")
    link_tags = soup.find_all("a")
    links: List[str] = [a["href"] for a in link_tags if "href" in a.attrs]

    #  filter them
    repo_links: List[str] = []
    for link in links:
        url = urlparse(link)
        match = re.match(r"^/(?P<user>[\w-]+)/(?P<user>[\w-]+)/?$", url.path)
        if url.hostname not in ["github.com", None]:
            logger.info(f"Skipping non-Github URL {link}")
            continue
        if match is None or match.group("user") in GITHUB_TOPLEVEL_PATH_BLACKLIST:
            logger.info(f"Skipping non-repo Github URL {link}")
            continue

            url.hostname = "api.github.com"

    return repo_links


async def get_ranking_data(session: ClientSession, repo_url):
    """Get individual repos data"""
    logger.debug(f"beginning request to {repo_url}")
    try:
        async with session.get(repo_url) as response:
            logger.debug(f"get response to {repo_url}")
            data = await response.text()
            data = json.loads(data)
            return {
                "name": data["name"],
                "owner": data["owner"]["login"],
                "stargazers": data["stargazers_count"],
                "url": data["html_url"],
            }
    except KeyError as e:
        logger.error(f"Response malformed at {repo_url}")
    except ClientError:
        logger.error(f"Request failed at {repo_url}")


async def get_stargazer_counts(repos, token=None):
    auth_header = {"Authorization": f"token {token}"} if token else {}
    async with ClientSession(headers=auth_header) as session:
        logger.debug("beginning session")
        tasks = [get_ranking_data(session, repo) for repo in repos]
        ranked_repos = await asyncio.gather(*tasks)
        ranked_repos = [r for r in ranked_repos if r and "stargazers" in r]
        logger.debug(ranked_repos)
    ranked_repos = sorted(ranked_repos, key=lambda x: x["stargazers"], reverse=True)
    return ranked_repos


if __name__ == "__main__":
    main()
