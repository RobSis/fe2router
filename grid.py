import sys
from PIL import Image, ImageDraw
import milkyway as data

class GalaxyMap():
    def __init__(self):
        self.screensize = (640, 640)
        self.bgcolor = (16, 32, 112, 255)

        self.width = 4
        self.height = 4

        self.im = Image.new('RGBA', self.screensize, self.bgcolor)
        self.draw = ImageDraw.Draw(self.im) # Create a draw object

    def grid(self):
        factX = self.screensize[0] / self.width
        factY = self.screensize[1] / self.height
        for y in range(self.height):
            for x in range(self.width):
                self.draw.rectangle((x * factX, y * factY, (x+1) * factX, (y+1) * factY), outline="green")

    def sector(self,x,y,listOfStars):
        factX = self.screensize[0] / self.width
        factY = self.screensize[1] / self.height
        for starSystem in listOfStars:
            absX = factX * (starSystem.x + 63) / 126 + factX*x
            absY = factY * (-starSystem.y + 63) / 126 + factY*y

            self.draw.ellipse((absX - 1, absY - 1, absX + 1, absY + 1), fill=data.ColorForStar[starSystem.stardesc]) # Draw a circle

    def save(self, path):
        self.im.save(path, 'PNG')
