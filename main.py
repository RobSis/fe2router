#!/usr/bin/env python
# Licensed under the terms of the GPL v3. See LICENCE for details

import sys
import argparse

from galaxy import Galaxy
from pathfinder import find_path
import config as conf
try:
    from grid import GalaxyMap
    pil = True
except ImportError as e:
    if "PIL" in e.message:
        pil = False
    else:
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find the path between the "
                                        "star systems in Frontier: Elite II.")
    parser.add_argument(
            "start", type=str,
            help="Starting star system")
    parser.add_argument(
            "end", type=str,
            help="Ending star system")
    parser.add_argument(
            "-r", "--range", type=int, default=conf.RANGE,
            help="Specify jump range (default %dly)" % conf.RANGE)
    parser.add_argument(
            "-n", "--nomap", action="store_true", default=False,
            help="Do not generate map")
    defScreen = str(conf.SCREENWIDTH) + "x" + str(conf.SCREENHEIGHT)
    parser.add_argument(
            "-s", "--screen", type=str, default=defScreen,
            help="Screen size. Default " + defScreen)
    parser.add_argument(
            "-t", "--tiles", type=str, default="",
            help="Map size. Format: WIDTHxHEIGHT")

    args = parser.parse_args()

    jumpRange = args.range
    if (pil):
        pil = not args.nomap
    screen = args.screen.split("x")
    if len(screen) != 2 or not screen[0].isdigit() or not screen[1].isdigit():
        parser.print_usage()
        print("error: argument -s/--screen: Invalid value: '%s'" % args.screen)
        sys.exit(1)
    else:
        scrSize = (int(screen[0]), int(screen[1]))

    mapSize = (0, 0)
    if (len(args.tiles) > 0):
        tilesStr = args.tiles.split("x")
        if len(tilesStr) != 2 or not tilesStr[0].isdigit() or\
                                 not tilesStr[1].isdigit():
            parser.print_usage()
            print("error: argument -t/--tiles: Invalid value: '%s'" %
                        args.tiles)
            sys.exit(1)
        else:
            mapSize = int(tilesStr[0]), int(tilesStr[1])

    # TODO #1: find the stars by the name
    c = Galaxy()
    c.sanityTest()

    sector1 = c.getSector(5912, 5412)
    sector2 = c.getSector(5908, 5412)

    # c.findStar(args.start)
    # c.findStar(args.end)
    sol = sector1.stars[0]
    tiafa = sector2.stars[0]

    path = find_path(c, sol, tiafa, jumpRange)

    prevStep = None
    if path is not None:
        for step in path:
            print(step.name),
            if (prevStep != None):
                print(": (%.3f ly)" % prevStep.distance(step)),

            print
            prevStep = step

    if (pil):
        map = GalaxyMap(scrSize)

        map.grid = True
        map.labels = True
        map.path = path

        if (mapSize == (0, 0)):
            # TODO #2 determine mapSize, so the whole path can be seen
            mapSize = (7, 7)

        map.save(c, (0, 0), mapSize)
