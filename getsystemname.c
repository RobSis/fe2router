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

unsigned int _rotl(const unsigned int value, int shift) {
    if ((shift &= sizeof(value)*8 - 1) == 0)
        return value;
    return (value << shift) | (value >> (sizeof(value)*8 - shift));
}
 
unsigned int _rotr(const unsigned int value, int shift) {
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

    int part1, part2, part3;

    int i;
    for (i=0; i<15; i++)
    {
        coordx = 5912 + sectorX;
        coordy = 5412 + sectorY;
        
        coordx += i;
        coordy += coordx;
        coordx = _rotl(coordx, 3);
        coordx += coordy;
        coordy = _rotl (coordy, 5);
        coordy += coordx;
        coordy = _rotl (coordy, 4);
        coordx = _rotl (coordx, i);
        coordx += coordy;

        part1 = (coordx >> 2) & 31;
        coordx = _rotr (coordx, 5);
        
        part2 = (coordx >> 2) & 31;
        coordx = _rotr (coordx, 5);
        
        part3 = (coordx >> 2) & 31;

        printf("%s%s%s\n",namepart[part1],namepart[part2],namepart[part3]);
    }

    return 0;
}
