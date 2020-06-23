#!/usr/bin/env python3.7
import re
import sys
import argparse
import asyncio
import json
from typing import List
from pprint import pprint
import logging

from aiohttp import ClientSession, ClientError
import requests
from bs4 import BeautifulSoup
from tabulate import tabulate

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def main():
    """Scrape and parse a github page. For all linked github projects, determine the number
    of stars asynchronously. Order the results by decreasing number of stars."""
    parser = argparse.ArgumentParser()
    parser.add_argument("url", type=str)
    parser.add_argument("--token", type=str)
    args = parser.parse_args()
    url = args.url
    token = args.token

    projects = get_linked_projects(url)
    repo_endpoints = get_repo_api_endpoints(projects)
    ranking = asyncio.run(get_stargazer_counts(repo_endpoints, token=token))
    print_ranking(ranking)


def print_ranking(ranking):
    print(tabulate(ranking, headers="keys"))


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
        if group["user"] != "site"
    ]


async def get_ranking_data(session: ClientSession, repo_url):
    """Get individual repos data"""
    logging.debug(f"beginning request to {repo_url}")
    try:
        async with session.get(repo_url,) as response:
            logging.debug(f"get response to {repo_url}")
            data = await response.text()
            data = json.loads(data)
            return {
                "name": data["name"],
                "owner": data["owner"]["login"],
                "stargazers": data["stargazers_count"],
            }
    except KeyError as e:
        logging.error("Response malformed - authentication failed?")
    except ClientError:
        logging.error("Request failed")


async def get_stargazer_counts(repos, token=None):
    auth_header = {"Authorization": f"token {token}"} if token else {}
    async with ClientSession(headers=auth_header) as session:
        logging.debug("beginning session")
        tasks = [get_ranking_data(session, repo) for repo in repos]
        ranked_repos = await asyncio.gather(*tasks)
    ranked_repos = sorted(ranked_repos, key=lambda x: x["stargazers"], reverse=True)
    return ranked_repos


if __name__ == "__main__":
    main()
