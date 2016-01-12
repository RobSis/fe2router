# fe2router #

*Recreating the universe from games Frontier: Elite II
and Frontier: First Encounters for purposes of making 
a map tool, which would help with planning routes between stars.*


## Usage ##
~~~
./fe2router [-h] [-r RANGE] [-n] [-s SCREEN] [-t TILES] start end

positional arguments:
  start                 Starting star system
  end                   Ending star system

optional arguments:
  -h, --help            show this help message and exit
  -r RANGE, --range RANGE
                        Specify jump range (default 10ly)
  -n, --nomap           Do not generate map
  -s SCREEN, --screen SCREEN
                        Screen size. Default 800x800
  -t TILES, --tiles TILES
                        Map size. Format: WIDTHxHEIGHT
~~~


![grid view](http://i.imgur.com/1V1CtxT.png)
