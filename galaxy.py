# Licensed under the terms of the GPL v3. See LICENCE for details
# This file contains pseduo-randomizing algorithms dissasembled
# from original Atari ST binary of Frontier: Elite II.

import math
import random
from ctypes import c_ulong, c_long, c_byte, c_ushort, c_uint

import milkyway as data


def ROR(x, n, bits=16):
    mask = c_ulong(2L ** c_ushort(n).value - 1).value
    mask_bits = x & mask
    return c_ushort(x >> c_ushort(n).value).value | \
            c_ushort(mask_bits << (bits - n)).value


def ROL(x, n, bits=16):
    return ROR(x, bits - n, bits)


class StarSystem(object):
    def __init__(self, x=0, y=0, z=0):
        if (isinstance(x, StarSystem)):
            # copy constructor
            self.x, self.y, self.z = x.x, x.y, x.z

            self.coordx = x.coordx
            self.coordy = x.coordy
            self.num = x.num

            self.name = x.name
            self.starType = x.starType
            self.multiple = x.multiple
        else:
            self.x, self.y, self.z = x, y, z

            self.coordx = 0
            self.coordy = 0
            self.num = 0

            self.name = ""
            self.starType = 0
            self.multiple = 0

    def uid(self):
        return (self.num << 26) + (self.coordy << 13) + self.coordx

    # String representation (built-in)
    def __repr__(self):
        output = "Name: %s\n" % self.name
        output += "Coordinates: [%d, %d, %d]\n" % (self.x, self.y, self.z)
        output += "Star type: %s\n" % data.StarDesc[self.starType]

        if (self.multiple > 0):
            output += data.StarMultiple[self.multiple - 1] + "."

        #output += "Star size: %d\n" % data.SizeForStar[self.starType]
        #output += "Star color: %s\n" % ColorForStar[self.starType].show()
        return output

    def distance(self, star):
        """Differs from game a bit,
        probably due to implementation of sqrt, or rounding."""
        x = star.x + (star.coordx - self.coordx) * 128
        y = star.y + (star.coordy - self.coordy) * 128
        z = star.z

        dist = abs(self.x - x) ** 2 + abs(self.y - y) ** 2 + \
               abs(self.z - z) ** 2
        dist = math.sqrt(dist) / 16
        return dist


class Sector:
    def __init__(self):
        # List of StarSystems
        self.stars = []

        self.coordx = 0
        self.coordy = 0

        # Nebulae, text, ...
        self.specialObject = None

    def __repr__(self):
        output = "Sector [%d, %d]\n" % (self.coordx, self.coordy)
        return output


class Galaxy:
    def __init__(self):
        # randomizer variables
        self.s0 = 0
        self.s1 = 0

    def _rotate_some(self):
        tmp1 = c_uint(self.s0 << 3).value | c_uint(self.s0 >> 29).value
        tmp2 = c_uint(self.s0 + self.s1).value
        tmp1 = c_uint(tmp1 + tmp2).value

        self.s0 = tmp1
        self.s1 = c_uint(tmp2 << 5).value | c_uint(tmp2 >> 27).value

    def _getDensity(self, coordx, coordy, galaxyScale):
        """Get number of stars in given sector."""
        # just dissasembled. rewrite!
        if ((coordx > 0x1fff) or (coordy > 0x1fff)):
            return 0

        pixelval = (coordx / 64) + 2 * (coordy & 0x1fc0)

        p1 = data.TheMilkyWay[pixelval]        # current center
        p2 = data.TheMilkyWay[pixelval + 1]    # next column
        p3 = data.TheMilkyWay[pixelval + 128]  # next row
        p4 = data.TheMilkyWay[pixelval + 129]  # next row, next column

        coordx = (coordx * 512) & 0x7e00
        coordy = (coordy * 512) & 0x7e00

        ebx = c_ulong((p2 - p1) * coordx + (p3 - p1) * coordy).value
        esi = c_ulong((coordx * coordy) >> 15).value

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
                edx = c_ulong(16 - galaxyScale).value
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
        """Compute the name from the star system coordinations."""

        cx = coordx + sysNum
        cy = coordy + cx
        cx = ROL(c_ushort(cx).value, 3) + cy
        cy = ROL(c_ushort(cy).value, 5) + cx
        cx = ROL(c_ushort(cx).value, sysNum)
        cx += ROL(c_ushort(cy).value, 4)

        name = ""
        for i in range(3):
            name += data.NamePart[(cx >> 2) & 31]
            cx = ROR(c_ushort(cx).value, 5)
        return name.capitalize()

    def _createSector(self, coordx, coordy):
        """Create the new sector."""

        sector = Sector()
        sector.coordx = coordx
        sector.coordy = coordy

        self.s0 = c_ulong(c_ulong(coordx << 16).value + coordy).value
        self.s1 = c_ulong(c_ulong(coordy << 16).value + coordx).value

        self._rotate_some()
        self._rotate_some()
        self._rotate_some()

        number_of_systems = self._getDensity(coordx, coordy, 0)
        for j in range(number_of_systems):
            star = StarSystem()

            self._rotate_some()

            star.z = c_byte((self.s0 & 0xff0000) >> 16).value
            star.y = c_byte(self.s0 >> 8).value
            star.y /= 2
            star.x = c_byte((self.s0 & 0x0001fe) >> 1).value
            star.x /= 2

            star.multiple = data.StarChance_Multiples[self.s1 & 0x1f]
            star.starType = data.StarChance_Type[(self.s1 >> 16) & 0x1f]

            star.num = j
            star.coordx = coordx
            star.coordy = coordy

            star.name = self._getSystemName(coordx, coordy, j)

            sector.stars.append(star)

        return sector

    def sanityTest(self):
        c = Galaxy()
        sec = c.getSector(data.SolX - 6, data.SolY - 2)
        assert len(sec.stars) == 2

        exquho = sec.stars[0]
        assert exquho.name == "Exquho"
        assert exquho.starType == 2
        assert exquho.multiple == 2
        assert exquho.x == -37
        assert exquho.y == 3
        assert exquho.z == -6

        sec2 = c.getSector(data.SolX + 1008, data.SolY - 2260)
        assert len(sec2.stars) == 6
       
        q = sec2.stars[3]
        assert q.name == "Olackfa"
        assert q.starType == 6
        assert q.multiple == 4
        assert q.x == -45
        assert q.y == 58
        assert q.z == -109

    # Get or create sector
    def getSector(self, coordx, coordy):
        """Create or load a sector."""

        if ((coordx, coordy) not in data.KnownSpaceCoord):
            return self._createSector(coordx, coordy)

        # Sector is from known universe
        sector = Sector()
        sector.coordx = coordx
        sector.coordy = coordy

        Off = data.KnownSpaceCoord.index((coordx, coordy))
        for j in range(data.KnownSpaceNameOffset[Off + 1] - \
                       data.KnownSpaceNameOffset[Off]):
            star = StarSystem()

            star.num = j
            star.coordx = coordx
            star.coordy = coordy

            rec = data.KnownSpaceStarCoords[data.KnownSpaceNameOffset[Off] + j]
            (star.x, star.y, star.z, star.starType, star.multiple) = rec

            star.name = data.KnownSpace[data.KnownSpaceNameOffset[Off] + j]

            sector.stars.append(star)

        return sector
