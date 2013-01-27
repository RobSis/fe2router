import sys

from PIL import Image, ImageDraw
import milkyway as data


class GalaxyMap():
    def __init__(self, (width, height)):
        self.screensize = (width, height)
        self.bgcolor = (16, 32, 112, 255)

        self.width = 4
        self.height = 4

        self.center = (5912, 5412)

        # Show star names
        self.labels = True
        self.grid = True

        self.im = Image.new('RGBA', self.screensize, self.bgcolor)
        self.draw = ImageDraw.Draw(self.im)  # Create a draw object

    def _grid(self):
        """Draw a grid."""

        factX = self.screensize[0] / self.width / 2
        factY = self.screensize[1] / self.height / 2

        for y in range(self.height * 2):
            for x in range(self.width * 2):
                self.draw.rectangle(
                    (x * factX, y * factY, (x + 1) * factX, (y + 1) * factY),
                    outline="darkgreen")

        factX = self.screensize[0] / self.width
        factY = self.screensize[1] / self.height

        for y in range(self.height):
            for x in range(self.width):
                self.draw.rectangle(
                    (x * factX, y * factY, (x + 1) * factX, (y + 1) * factY),
                    outline="lightgreen")

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
                            label, fill="gray")

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
                self.draw.text((absX + 3, absY + 3), star.name, fill="black")
                self.draw.text((absX + 3, absY + 3), star.name, fill="white")

    def save(self, galaxy, (cx, cy), width, height):
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

        self.im.save("/home/rob/Games/Pylot/test.png", 'PNG')
