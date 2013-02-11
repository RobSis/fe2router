#!/usr/bin/env python
# Licensed under the terms of the GPL v3. See LICENCE for details

from galaxy import Galaxy
from grid import GalaxyMap
from pathfinder import find_path

# startStar = [0, 0] # Sol
# endStar = [-3, 0] # Tiafa
# hyper-jump range = 8ly
# --------------
# - find the (shortest?) path
# - show it on the map
jumpRange = 8

c = Galaxy()
c.sanityTest()

map = GalaxyMap((800, 800))

sector1 = c.getSector(5912, 5412)
sector2 = c.getSector(5909, 5412)

sol = sector1.stars[0]
tiafa = sector2.stars[0]

path = find_path(c, sol, tiafa, jumpRange)

prevStep = None
if path is not None:
    for step in path:
        print step.name,
        if (prevStep != None):
            print ":", "(%.3f ly)" % prevStep.distance(step)
        else:
            print
        prevStep = step

map.path = path

map.grid = True
map.labels = True

map.save(c, (0, 0), 6, 6)
