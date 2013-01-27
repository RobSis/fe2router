import sys

from PIL import Image, ImageDraw
import milkyway as data

class GalaxyMap():
    def __init__(self):
        self.screensize = (800,800)
        self.bgcolor = (16, 32, 112, 255)

        self.width = 4
        self.height = 4

        self.center = (5912,5412) # Sol

        self.im = Image.new('RGBA', self.screensize, self.bgcolor)
        self.draw = ImageDraw.Draw(self.im) # Create a draw object

    def grid(self):
        factX = self.screensize[0] / self.width / 2
        factY = self.screensize[1] / self.height / 2

        for y in range(self.height*2):
            for x in range(self.width*2):
                self.draw.rectangle((x * factX, y * factY, (x+1) * factX, (y+1) * factY), outline="green")

    def sector(self,cx,cy,sector):
        factX = self.screensize[0] / self.width
        factY = self.screensize[1] / self.height
        
        label = "[%d,%d]" % (sector.coordx - self.center[0],sector.coordy - self.center[1])
        if (sector.coordx == 5912) and (sector.coordy == 5413):
            self.draw.text((factX * cx, factY * cy), label, fill="red")
        else:
            self.draw.text((factX * cx, factY * cy), label, fill="grey")

        for star in sector.stars:
            absX = factX * (star.x + 63) / 126 + factX*cx
            absY = factY * (-star.y + 63) / 126 + factY*cy
            color = data.ColorForStar[star.starType]

            self.draw.ellipse((absX - 6, absY - 6, absX + 6, absY + 6), fill=color) # Draw a circle
            self.draw.text((absX + 3, absY + 3), star.name, fill="black")
            self.draw.text((absX + 3, absY + 3), star.name, fill="white")

    def save(self, path):
        self.im.save(path, 'PNG')
