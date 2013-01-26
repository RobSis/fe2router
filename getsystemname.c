#include <stdio.h>

char *namepart[] = {
    "en" , "la" , "can", "be" ,
    "and", "phi", "eth", "ol" ,
    "ve" , "ho" , "a"  , "lia",
    "an" , "ar" , "ur" , "mi" ,
    "in" , "ti" , "qu" , "so" ,
    "ed" , "ess", "ex" , "io" ,
    "ce" , "ze" , "fa" , "ay" ,
    "wa" , "da" , "ack", "gre"
};

unsigned short _rotl(const unsigned short value, int shift) {
    if ((shift &= sizeof(value)*8 - 1) == 0)
        return value;
    return (value << shift) | (value >> (sizeof(value)*8 - shift));
}
 
unsigned short _rotr(const unsigned short value, int shift) {
    if ((shift &= sizeof(value)*8 - 1) == 0)
        return value;
    return (value >> shift) | (value << (sizeof(value)*8 - shift));
}

int main() {
    /* [0, 3] */
    int sectorX = -3;
    int sectorY = 0;
    
    unsigned int coordx;
    unsigned int coordy;

    char part1, part2, part3;

    int sysnum;
    for (sysnum=0; sysnum < 15; sysnum++)
    {
        coordx = 5912 + sectorX;
        coordy = 5412 + sectorY;
        //sysnum = d5
        //coordx = d3
        //coordy = d4
        //
        coordx += sysnum;               // d3 += d5
        coordy += coordx;               // d4 += d3
        coordx = _rotl (coordx, 3);     // d3 = rol(d3, 3)
        coordx += coordy;               // d3 += d4
        coordy = _rotl (coordy, 5);     // d4 = rol(d4, 5)
        coordy += coordx;               // d4 += d3
        coordy = _rotl (coordy, 4);     // d4 = rol(d4, 4)
        coordx = _rotl (coordx, sysnum);// d3 = rol(d3, d5)
        coordx += coordy;               // d3 += d4

        printf("%d\n",coordx);

        part1 = (coordx >> 2) & 31;
        coordx = _rotr (coordx, 5);
        
        part2 = (coordx >> 2) & 31;
        coordx = _rotr (coordx, 5);
        
        part3 = (coordx >> 2) & 31;

        printf("%s%s%s\n",namepart[part1],namepart[part2],namepart[part3]);

    }

    return 0;
}
