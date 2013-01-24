import math, random
from ctypes import c_ulong, c_long, c_byte


from milkyway import *
from graphs import *


def ROR(x, n, bits=64):
    mask = (2L**n) - 1
    mask_bits = x & mask
    return (x >> n) | (mask_bits << (bits - n))

def ROL(x, n, bits=64):
    return ROR(x, bits - n, bits)

# Galaxy size: 8192x8192
# Sol: (5912, 5412)

class StarSystem:
    """A object coordinations
    """

    def __init__(self, x = 0, y = 0, z = 0):        
        self.x, self.y, self.z = x, y, z

        self.uid = 0
        self.coordx = 0
        self.coordy = 0
        self.sys_num = 0
       
        self.name = ""      
        self.stardesc = 0
        self.multiple = 0


    def info(self):
        output = "Name: %s\n" % self.name
        output += "Coordinates: [%d, %d, %d]\n" % (self.x,self.y,self.z)
        output += "Star type: %s\n" % StarDesc[self.stardesc]
        
        star = StarSystem()
        star.x = 0
        star.y = 16
        star.z = -54
        star.coordx = 5912
        star.coordy = 5412
 
        output += "Distance to Sol: %f\n" % self.distance(star)
        #output += "Star size: %d\n" % SizeForStar[self.stardesc]
        #output += "Star color: %s\n" % ColorForStar[self.stardesc].show()
        return output

    def distance(self, star):
        """not working"""
        factor = 16.05

        x = star.x + (star.coordx - self.coordx)*128
        y = star.y + (star.coordy - self.coordy)*128

        print (star.coordx - self.coordx)
        print (star.coordy - self.coordy)


        z = star.z

        dist = abs(self.x - x)**2 + abs(self.y - y)**2\
            + abs(self.z - z)**2
        dist = math.sqrt(dist) / factor

        return dist

class Seed:
    def __init__(self,seed):
        self.s0 = 0
        self.s1 = 0

    def rotate_some(self):
        tmp1 = c_ulong(c_ulong(self.s0 << 3).value | c_ulong(self.s0 >> 29).value).value
        tmp2 = c_ulong(self.s0 + self.s1).value
        tmp1 = c_ulong(tmp1 + tmp2).value
        
        self.s0 = tmp1
        self.s1 = c_ulong(c_ulong(tmp2 << 5).value | c_ulong(tmp2 >> 27).value).value



class Galaxy:

    def __init__(self):
        self.seed = Seed(1234)

        self.coords = []

        self.left = 0
        self.up = 0


    def getDensity(self, coordx, coordy, galaxyScale):
        """Magic function holding the universe together.
        Dissasembled by Jongware from original data."""
    
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

    def getSystemName(self, coordx, coordy, sysNum):
        coordx = c_ulong(coordx + sysNum).value
        coordy = c_ulong(coordy + coordx).value
        coordx = ROL(coordx, 3)
        coordx += coordy
        coordy = ROL(coordy, 5)
        coordy += coordx
        coordy = ROL(coordy, 4)
        coordx = ROL(coordx, sysNum)
        coordx += coordy

        name = ""
        for i in range(3):
            name += namepart[(coordx >> 2) & 31]
            coordx = ROR(coordx, 5)
        return name.capitalize()


    # Create pseudorandom sector
    def createSector(self, coordx, coordy):
        self.coords = []

        self.seed.s0 = c_ulong(c_ulong(coordx << 16).value + coordy).value
        self.seed.s1 = c_ulong(c_ulong(coordy << 16).value + coordx).value

        self.seed.rotate_some()
        self.seed.rotate_some()
        self.seed.rotate_some()

        number_of_systems = self.getDensity(coordx, coordy, 0)
        for i in range(number_of_systems):
            self.seed.rotate_some()
            
            star = StarSystem()

            star.z = c_byte(c_ulong(self.seed.s0 & 0xff0000).value >> 16).value
            star.y = c_byte(self.seed.s0 >> 8).value
            star.y /= 2
            star.x = c_byte(c_ulong(self.seed.s0 & 0x0001fe).value >> 1).value
            star.x /= 2

            star.multiple = StarChance_Multiples[c_ulong(self.seed.s1 & 0x1f).value]
            star.stardesc = StarChance_Type[c_ulong(self.seed.s1 >> 16).value & 0x1f]

            star.sys_num = i
            star.name = self.getSystemName(coordx, coordy, i)

            self.coords.append(star)

    # Get or create sector
    def getSector(self, coordx, coordy):
        self.coords = []
        
        if ((coordx,coordy) not in KnownSpaceCoord):
            return self.createSector(coordx, coordy)
        

        Off = KnownSpaceCoord.index((coordx,coordy))
        for j in range(KnownSpaceNameOffset[Off+1] - KnownSpaceNameOffset[Off]):
            star = StarSystem()

            star.uid = (j<<26) + (coordy<<13) + (coordx)

            star.x = KnownSpaceStarCoords[KnownSpaceNameOffset[Off]+j][0]
            star.y = KnownSpaceStarCoords[KnownSpaceNameOffset[Off]+j][1]
            star.z = KnownSpaceStarCoords[KnownSpaceNameOffset[Off]+j][2]

            star.coordx = coordx
            star.coordy = coordy

            star.sys_num = j
            star.stardesc = KnownSpaceStarCoords[KnownSpaceNameOffset[Off]+j][3]
            star.multiple = KnownSpaceStarCoords[KnownSpaceNameOffset[Off]+j][4]

            star.name = KnownSpace[KnownSpaceNameOffset[Off]+j]

            self.coords.append(star)

        
    def test(self, x, y):
        self.getSector(5912+x,5412+y)
        
        for starSystem in self.coords:
            print starSystem.info()

#        #video = VideoDriver()
#
#        while 0:
#            video.DoEvents()
#            self.update(video.KeyStatus)
#
#            video.clock.tick(50)
#            video.screen.fill((0,32,0))
#
#            coords = []
#            for star in self.coords:
#                coords.append((star.x, star.y, star.z))
#            
#            sector = Object3D()
#            sector.addNodes(coords)
#
#            pv = ProjectionView(video.screen_size)
#            pv.addModel('sector',sector)
#
#
#            pv.translate('sector', 'x', self.left)
#            pv.translate('sector', 'y', self.up)
#           
#
#
#            pv.display(video.screen)
#            
#            video.flush()

    def update(self, KeyStatus):
        if KeyStatus["Left"] and not KeyStatus["Right"]:
            self.left += 1
        if KeyStatus["Up"] and not KeyStatus["Down"]:
            self.up += 1
    
c = Galaxy()
c.test(0, 3)
