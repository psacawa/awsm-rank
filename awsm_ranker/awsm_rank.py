#!/usr/bin/env python3.7
import re
import sys
import argparse
import asyncio
import json
from os import environ
from typing import List
from pprint import pprint
import logging
import subprocess

from aiohttp import ClientSession, ClientError
import requests
from bs4 import BeautifulSoup
from tabulate import tabulate

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))


def main():
    """Scrape and parse a github page. For all linked github projects, determine the number
    of stars asynchronously. Order the results by decreasing number of stars.
    Authentication can be provided by the GITHUB_API_TOKEN environmental variable, or
    preferentially via the --token argument. If not given, am unauthenticated query will
    be attempted.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("url", type=str)
    parser.add_argument("--token", type=str)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--debug", dest="debug", action="store_true")
    parser.add_argument("--open", dest="open", action="store_true")
    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)

    token = environ.get("GITHUB_API_TOKEN", None) or args.token
    logger.debug(f"Using authentication token: {token}")

    projects = get_linked_projects(args.url)
    repo_endpoints = get_repo_api_endpoints(projects)
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
    firefox_cmd = "firefox".split() + urls
    logger.debug(f"Executing: {' '.join (firefox_cmd)}")
    subprocess.run(firefox_cmd)


def get_linked_projects(url):
    """Get github projects linked a given webpage"""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a")
    links = [a["href"] for a in links]
    pattern = r"^https://github.com/(?P<user>\w+)/(?P<repo>[^/]+)$"
    prog = re.compile(pattern).search
    matches = map(prog, links)
    repos = list(filter(None, matches))
    return repos


def get_repo_api_endpoints(projects: List[re.Match]):
    """ Transform a project URL into an API repo endpoint"""
    groups = [project.groupdict() for project in projects]
    return [
        f"https://api.github.com/repos/{group['user']}/{group['repo']}"
        for group in groups
        if group["user"] not in ["apps", "site"]
    ]


async def get_ranking_data(session: ClientSession, repo_url):
    """Get individual repos data"""
    logger.debug(f"beginning request to {repo_url}")
    try:
        async with session.get(repo_url,) as response:
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
        logger.error(f"Response malformed at {repo_url}- authentication failed?")
    except ClientError:
        logger.error(f"Request failed at {repo_url}")


async def get_stargazer_counts(repos, token=None):
    auth_header = {"Authorization": f"token {token}"} if token else {}
    async with ClientSession(headers=auth_header) as session:
        logger.debug("beginning session")
        tasks = [get_ranking_data(session, repo) for repo in repos]
        ranked_repos = await asyncio.gather(*tasks)
        logger.debug(ranked_repos)
    ranked_repos = sorted(ranked_repos, key=lambda x: x["stargazers"], reverse=True)
    return ranked_repos


if __name__ == "__main__":
    main()
