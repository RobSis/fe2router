import math, random
from ctypes import c_ulong, c_long, c_byte, c_ushort, c_uint

import milkyway as data
from grid import GalaxyMap

def ROR(x, n, bits=16):
    mask = (2L**n) - 1
    mask_bits = x & mask
    return c_ushort(x >> n).value | c_ushort(mask_bits << (bits - n)).value

def ROL(x, n, bits=16):
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
        output = "Name: %s (%s)\n" % (self.name,self.uid)
        output += "Coordinates: [%d, %d, %d]\n" % (self.x,self.y,self.z)
        output += "Star type: %s\n" % data.StarDesc[self.stardesc]

        output += "Star size: %d\n" % data.SizeForStar[self.stardesc]
        #output += "Star color: %s\n" % ColorForStar[self.stardesc].show()
        return output


class Seed:
    def __init__(self):
        self.s0 = 0
        self.s1 = 0

    def rotate_some(self):
        tmp1 = c_uint(self.s0 << 3).value | c_uint(self.s0 >> 29).value
        tmp2 = c_uint(self.s0 + self.s1).value
        tmp1 = c_uint(tmp1 + tmp2).value
        
        self.s0 = tmp1
        self.s1 = c_uint(tmp2 << 5).value | c_uint(tmp2 >> 27).value


class Galaxy:

    def __init__(self):
        self.seed = Seed()

        self.stars = []

        self.left = 0
        self.up = 0
        self.into = 0


    def _getDensity(self, coordx, coordy, galaxyScale):
        """Magic function holding the universe together.
        Dissasembled by Jongware from original data."""
    
        if ((coordx > 0x1fff) or (coordy > 0x1fff)):
            return 0

        pixelval = (coordx / 64) + 2 * (coordy & 0x1fc0)

        p1 = data.TheMilkyWay[pixelval]     # current center
        p2 = data.TheMilkyWay[pixelval+1]   # next column
        p3 = data.TheMilkyWay[pixelval+128] # next row
        p4 = data.TheMilkyWay[pixelval+129] # next row, next column

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
            eax = data.SystemDensity[ebx]
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

    def _getSystemName(self, coordx, coordy, sysNum):
        coordx = coordx + sysNum
        coordy = coordy + coordx
        coordx = ROL(c_ushort(coordx).value, 3)
        coordx += coordy
        coordy = ROL(c_ushort(coordy).value, 5)
        coordy += coordx
        coordy = ROL(c_ushort(coordy).value, 4)
        coordx = ROL(c_ushort(coordx).value, sysNum)
        coordx += coordy

        name = ""
        for i in range(3):
            name += data.namepart[(coordx >> 2) & 31]
            coordx = ROR(c_ushort(coordx).value, 5)
        return name.capitalize()


    # Create pseudorandom sector
    def _createSector(self, coordx, coordy):
        self.stars = []

        self.seed.s0 = c_ulong(c_ulong(coordx << 16).value + coordy).value
        self.seed.s1 = c_ulong(c_ulong(coordy << 16).value + coordx).value

        self.seed.rotate_some()
        self.seed.rotate_some()
        self.seed.rotate_some()

        number_of_systems = self._getDensity(coordx, coordy, 0)
        for i in range(number_of_systems):            
            star = StarSystem()

            self.seed.rotate_some()

            star.z = c_byte(c_ulong(self.seed.s0 & 0xff0000).value >> 16).value
            star.y = c_byte(self.seed.s0 >> 8).value
            star.y /= 2
            star.x = c_byte(c_ulong(self.seed.s0 & 0x0001fe).value >> 1).value
            star.x /= 2


            star.multiple = data.StarChance_Multiples[c_ulong(self.seed.s1 & 0x1f).value]
            star.stardesc = data.StarChance_Type[c_ulong(self.seed.s1 >> 16).value & 0x1f]

            star.sys_num = i
            star.coordx = coordx
            star.coordy = coordy
            star.uid = (i<<26) + (coordy<<13) + (coordx)

            star.name = self._getSystemName(coordx, coordy, i)

            self.stars.append(star)

    # Get or create sector
    def getSector(self, coordx, coordy):
        self.stars = []
        
        if ((coordx,coordy) not in data.KnownSpaceCoord):
            return self._createSector(coordx, coordy)
        

        Off = data.KnownSpaceCoord.index((coordx,coordy))
        for j in range(data.KnownSpaceNameOffset[Off+1] - data.KnownSpaceNameOffset[Off]):
            star = StarSystem()

            star.x = data.KnownSpaceStarCoords[data.KnownSpaceNameOffset[Off]+j][0]
            star.y = data.KnownSpaceStarCoords[data.KnownSpaceNameOffset[Off]+j][1]
            star.z = data.KnownSpaceStarCoords[data.KnownSpaceNameOffset[Off]+j][2]

            star.sys_num = j
            star.coordx = coordx
            star.coordy = coordy
            star.uid = (j<<26) + (coordy<<13) + (coordx)
           
            star.stardesc = data.KnownSpaceStarCoords[data.KnownSpaceNameOffset[Off]+j][3]
            star.multiple = data.KnownSpaceStarCoords[data.KnownSpaceNameOffset[Off]+j][4]

            star.name = data.KnownSpace[data.KnownSpaceNameOffset[Off]+j]

            self.stars.append(star)

        
    def test(self, (centerX, centerY), width, height):

        map = GalaxyMap()

        map.width = width
        map.height = height

        map.grid()

        for y in range(-width / 2, width / 2 + 1):
            for x in range(-width / 2, width / 2 + 1):
                self.getSector(centerX+x,centerY+y)
                map.sector(x+width / 2,y + width / 2,self.stars)
        
        map.save("/home/rob/Games/Pylot/test.png")
 
c = Galaxy()
c.test( (5912, 5412), 5, 5)
