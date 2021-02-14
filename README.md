# RssCast

Convert (forward) Youtube RSS channels to podcast RSS.

Main rationale behind the project was to provide simple and lightweight application allowing to
provide Youtube videos in form of audio feed. Application does not need any form of Youtube API key.
The goal is achieved using third party webside executing the conversion. 


By default each converted audio feed is available at address: _http://{local_ip}:8080/feed/{id}/rss_ 


## Screens

[![Server tab](doc/mainwindow-server-small.png "Server tab")](doc/mainwindow-server-big.png)
[![Feed tab](doc/mainwindow-feed-small.png "Feed tab")](doc/mainwindow-feed-big.png)


## Disclaimer

Application uses `http.server` module. Accourding to module's home page:
 
> `http.server` is not recommended for production. It only implements basic security checks.

so it's advisable not to expose the server to public network.


## Similar projects

- YouCast
- podsync


## References:

- https://www.rssboard.org/rss-profile
- https://yt1s.com
