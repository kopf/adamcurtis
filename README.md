# adamcurtis.py

[Adam Curtis](http://en.wikipedia.org/wiki/Adam_Curtis) is a British documentary film-maker who also happens to have [a great blog](http://www.bbc.co.uk/blogs/adamcurtis) on the BBC's website.

His blogposts are typically very long, however, and often contain many audio-visual elements necessary for setting additional context. As a result, finding the time to read and watch these can prove rather difficult.

`adamcurtis.py` is a script that will save these blog-posts - including all multimedia - for reading and watching at a later date (e.g. on long journeys without internet connectivity). 

# Installation and usage

## OS X

````
git clone https://github.com/kopf/adamcurtis.git
cd adamcurtis
curl -O https://raw.githubusercontent.com/get-iplayer/get_iplayer/latest/get_iplayer
pip install -r requirements.txt
brew install rtmpdump
./adamcurtis.py --help
````

## Linux

Follow the instructions for OS X, replacing the `brew install rtmpdump` with a similar command to your package manager to install the package `rtmpdump`.

## Windows

You're on your own, I'm afraid.

# Tests?

![](http://ahye.zzzz.io/s/1ef79443e75d491bde5ef8dcf2214bef.jpg)
