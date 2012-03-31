import math, random
from ctypes import c_ulong, c_long


from milkyway import *
from graphs import *


# Galaxy size: 8192x8192
# Sol: (5912, 5412)

class StarSystem:
    """A object coordinations
    """

    def __init__(self, x = 0, y = 0, z = 0):
        self.x, self.y, self.z = x, y, z

        self.stardesc = 0
        self.multiple = 0

        self.name = ""
        self.sys_num = 0


        self.UniqueID = 0
        self.population = ""
        self.techlevel = 0 #[0,255]
        self.Chance_CargoCheck = 0



    def info(self):
        output = "Name: %s\n" % self.name
        output += "Coordinates: [%d, %d, %d]\n" % (self.x,self.y,self.z)
        output += "Star type: %s\n" % StarDesc[self.stardesc]
        #output += "Star size: %d\n" % SizeForStar[self.stardesc]
        #output += "Star color: %s\n" % ColorForStar[self.stardesc].show()
        return output

class Seed:
    def __init__(self,seed):
        self.s1 = seed
        self.s2 = seed - int(seed/2)

    def inrange(self, start, stop):
        self._flush()
        return random.randint(start, stop)

    def fromlist(self, somelist):
        self._flush()
        return random.choice(somelist)

    def reseed(self, seed, seed2):
        random.seed((seed ** 8) +  seed2)
        self.s1 = random.random()
        self._flush()


    def _flush(self):
        random.seed(self.s1)
        self.s1 = random.random()*12
        random.seed(self.s1)


class Galaxy:

    def __init__(self):
        self.seed = Seed(1234)

        self.coords = []

        self.left = 0


    def getDensity(self, coordx, coordy, galaxyScale):
        """Magic function holding the universe together."""
    
        if ((coordx > 0x1fff) or (coordy > 0x1fff)):
            return 0

        pixelval = (coordx / 64) + 2 * (coordy & 0x1fc0)

        p1 = TheMilkyWay[pixelval]     # current center
        p2 = TheMilkyWay[pixelval+1]   # next column
        p3 = TheMilkyWay[pixelval+128] # next row
        p4 = TheMilkyWay[pixelval+129] # next row, next column

        coordx = (coordx * 512) & 0x7e00
        coordy = (coordy * 512) & 0x7e00


        ebx = c_ulong((p2-p1)*coordx + (p3-p1)*coordy).value
        esi = c_ulong((coordx*coordy) >> 15).value


        edi = c_ulong(p4 - p3 - p2 + p1).value
        esi = c_ulong(esi * edi).value
        ebx = c_ulong(ebx + esi).value
        ebx = c_ulong(ebx + ebx).value

        p1 = c_ulong(p1 << 16).value
        ebx = c_ulong(ebx + p1).value
        ecx = c_ulong(ebx >> 8).value

        if (galaxyScale < 16):
            ebx = c_ulong(coordx + ecx).value
            eax = c_ulong(coordx * coordy).value
            eax = c_ulong(c_long(eax >> 15).value).value
            ebx = c_ulong(ebx ^ eax).value
            ebx = c_ulong(c_long(ebx >> 5).value).value
            ebx = c_ulong(ebx & 0x7f).value
            eax = SystemDensity[ebx]
            if (galaxyScale):
                edx = c_ulong(16-galaxyScale).value
                edx = c_ulong(edx * eax).value
                edx = c_ulong(c_long(edx >> 5).value).value
                eax = c_ulong(0xffff - edx).value
                ecx = c_ulong(ecx * eax).value
                ecx = c_ulong(ecx >> 16).value
            else:
                ecx = c_ulong(ecx * eax).value
                ecx = c_ulong(ecx >> 16).value


        p1 = ecx
        p1 = c_ulong(p1 >> 10).value
        return p1

    def createSector(self, coordx, coordy):
        self.coords = []

        number_of_systems = self.getDensity(coordx, coordy, 0)
        for i in range(number_of_systems):
            self.seed.reseed(coordx | i, coordy ^ i)

            self.coords.append(StarSystem())

            self.coords[i].x = self.seed.inrange(-63, 63)
            self.coords[i].y = self.seed.inrange(-63, 63)
            self.coords[i].z = self.seed.inrange(-128, 127)

            self.coords[i].multiple = self.seed.fromlist(StarChance_Multiples)
            self.coords[i].stardesc = self.seed.fromlist(StarChance_Type)

            name = self.seed.fromlist(namepart) + self.seed.fromlist(namepart) + self.seed.fromlist(namepart)

            self.coords[i].name = name.capitalize()

    def getSector(self, coordx, coordy):
        self.coords = []
        
        if ((coordx,coordy) not in KnownSpaceCoord):
            return self.createSector(coordx, coordy)
        

        Off = KnownSpaceCoord.index((coordx,coordy))
        for j in range(KnownSpaceNameOffset[Off+1] - KnownSpaceNameOffset[Off]):
            star = StarSystem()

            star.x = KnownSpaceStarCoords[KnownSpaceNameOffset[Off]+j][0]
            star.y = KnownSpaceStarCoords[KnownSpaceNameOffset[Off]+j][1]
            star.z = KnownSpaceStarCoords[KnownSpaceNameOffset[Off]+j][2]

            star.num = j
            star.stardesc = KnownSpaceStarCoords[KnownSpaceNameOffset[Off]+j][3]
            star.multiple = KnownSpaceStarCoords[KnownSpaceNameOffset[Off]+j][4]

            star.name = KnownSpace[KnownSpaceNameOffset[Off]+j]

            self.coords.append(star)

        return j
        
    def test(self):
        self.getSector(5912,5412)

        video = VideoDriver()

        while 1:
            video.DoEvents()
            self.update(video.KeyStatus)

            video.clock.tick(50)
            video.screen.fill((0,32,0))

            coords = []
            for star in self.coords:
                coords.append((star.x, star.y, star.z))
            
            sector = Object3D()
            sector.addNodes(coords)

            pv = ProjectionView(video.screen_size)
            pv.addModel('sector',sector)


            pv.translate('sector', 'x', self.left)
            


            pv.display(video.screen)
            
            video.flush()

    def update(self, KeyStatus):
        if KeyStatus["Left"] and not KeyStatus["Right"]:
            self.left += 1





    

        



c = Galaxy()
c.test()
