# Licensed under the terms of the GPL v3. See LICENCE for details

import sys
from PIL import Image, ImageDraw

import milkyway as data
import config as conf


class GalaxyMap():
    def __init__(self, screensize=None):
        if (screensize != None):
            self.screensize = (screensize[0], screensize[1])
        else:
            self.screensize = (conf.SCREENWIDTH, conf.SCREENHEIGHT)

        self.width = conf.WIDTH
        self.height = conf.HEIGHT

        self.center = (5912, 5412)

        # Show star names
        self.labels = True
        self.grid = True

        # List of stars representing the path
        self.path = []

        self.im = Image.new(conf.COLORMODE, self.screensize, conf.BGCOLOR)
        self.draw = ImageDraw.Draw(self.im)  # Create a draw object

    def _grid(self):
        """Draw a grid."""

        factX = self.screensize[0] / self.width / 2.0
        factY = self.screensize[1] / self.height / 2.0

        for y in range(self.height * 2):
            for x in range(self.width * 2):
                self.draw.rectangle(
                    (x * factX, y * factY, (x + 1) * factX, (y + 1) * factY),
                    outline=conf.GRID)

        factX = self.screensize[0] / self.width
        factY = self.screensize[1] / self.height

        for y in range(self.height):
            for x in range(self.width):
                self.draw.rectangle(
                    (x * factX, y * factY, (x + 1) * factX, (y + 1) * factY),
                    outline=conf.GRID2)

    def _sector(self, sector):
        """Draw one sector."""

        cx = sector.coordx - self.center[0] + self.width / 2
        cy = sector.coordy - self.center[1] + self.height / 2

        factX = self.screensize[0] / self.width
        factY = self.screensize[1] / self.height

        if (self.grid):
            label = " %d,%d" % (sector.coordx - data.SolX,
                                sector.coordy - data.SolY)
            self.draw.text((factX * cx, self.screensize[1] - factY * (cy + 1)),
                            label, fill=conf.COORDS)

        for star in sector.stars:
            absX = factX * (star.x + 63) / 126 + factX * cx
            absY = factY * (star.y + 63) / 126 + factY * cy
            absY = self.screensize[1] - absY

            color = data.ColorForStar[star.starType]
            size = round(20 * data.SizeForStar[star.starType] / 1400)

            self.draw.ellipse(
                          (absX - size, absY - size, absX + size, absY + size),
                          fill=color)  # Draw a circle

            if (self.labels):
                self.draw.text((absX + size + 1, absY - size / 2),
                                star.name, fill="black")

                self.draw.text((absX + size, absY - size / 2),
                                star.name, fill=conf.LABEL)

    def _path(self):
        factX = self.screensize[0] / self.width
        factY = self.screensize[1] / self.height

        prevX, prevY = None, None

        for star in self.path:
            cx = star.coordx - self.center[0] + self.width / 2
            cy = star.coordy - self.center[1] + self.height / 2

            absX = factX * (star.x + 63) / 126 + factX * cx
            absY = factY * (star.y + 63) / 126 + factY * cy
            absY = self.screensize[1] - absY

            if (prevX != None and prevY != None):
                self.draw.line((prevX, prevY, absX, absY),
                                fill=conf.PATH)

            prevX, prevY = absX, absY

    def save(self, galaxy, (cx, cy), (width, height)):
        """Generate the map and save to PNG file."""

        centerX = data.SolX + cx
        centerY = data.SolY + cy

        self.width = width
        self.height = height
        self.center = (centerX, centerY)

        if (self.grid):
            self._grid()

        # Draw sectors
        rangeX = range(width / -2, width / 2 + 1)
        rangeY = range(height / -2, height / 2 + 1)

        for y in rangeY:
            for x in rangeX:
                sector = galaxy.getSector(centerX + x, centerY + y)
                self._sector(sector)

        if (self.path != None and len(self.path) > 0):
            self._path()

        self.im.save(conf.OUTPUT, conf.FORMAT)
