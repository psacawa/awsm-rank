## awsm-rank

![pypi](https://github.com/psacawa/awsm-rank/actions/workflows/python-publish.yml/badge.svg)

A simple script that searches a web page for all linked Github repositories, and ranks them by number of populatarity (as measured by **github stars**). Use it on the pages from the **awesome** series of pages ([https://github.com/sindresorhus/awesome](https://github.com/sindresorhus/awesome)), or other pages listing open source projects.

### Installation 

```
pip install awsm-rank
```

### Usage

Get the URL of a page like [Awesome JS](https://github.com/sorrycc/awesome-javascript), which lists open source Github projects. 

For large pages, you will need to supply a Github API token or you'll hit the API rate limiting. You can supply it either through the `GITHUB_API_TOKEN` environmental variable or the  `--token` option.

```
epport GITHUB_API_TOKEN=...
```


Then run,
```
> awsm-rank https://github.com/sorrycc/awesome-javascript
name                               owner                stargazers
---------------------------------  -----------------  ------------
awesome                            sindresorhus             278573
vue                                vuejs                    205809
javascript-algorithms              trekhleb                 177417
You-Dont-Know-JS                   getify                   173093
react-native                       facebook                 112959
d3                                 d3                       106702
axios                              axios                    102558
angular                            angular                   92122
clean-code-javascript              ryanmcdermott             86832
puppeteer                          puppeteer                 85124
svelte                             sveltejs                  73933
webpack                            webpack                   63684
awesome-react                      enaqx                     59348
awesome-interview-questions        DopplerHQ                 59230
lodash                             lodash                    57936
strapi                             strapi                    57415
echarts                            apache                    57141
playwright                         microsoft                 56780
html5-boilerplate                  h5bp                      55423
gatsby                             gatsbyjs                  54809
docusaurus                         facebook                  49526
moment                             moment                    47579
prettier                           prettier                  47270
dayjs                              iamkun                    44707
Ghost                              TryGhost                  44445
meteor                             meteor                    43852
jest                               jestjs                    42980
...
```

Use `--limit $num` to only show the top `$num` results.
