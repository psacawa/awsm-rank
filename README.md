### awsm-rank

A simple script that searches a web page for all linked Github repos, and ranks them by number of stars. Use it on the pages from the *awesome* series of pages, or other pages listing open source projects.

### Installation 

```
pip install awsm-rank
```

### Usage

Get the URL of a page like [awesome JS](https://github.com/sorrycc/awesome-javascript) list github projects. Then run,

```
awsm-rank https://github.com/sorrycc/awesome-javascript
```

Use `--limit $num` to only show the top `$num` results.

For large pages, you will to supply a Github API token or hit the rate limiting. You can supply it either through the `GITHUB_API_TOKEN` environmental variable or the  `--token` option.


### Bugs

- Does not handle relative (i.e. same-origin hrefs)
- Fails critically on nonrepo github links

