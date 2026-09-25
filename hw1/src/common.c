#include "common.h"
#include <stdlib.h>
const Algorithm algorithms[3] = {{"insertion",1,insertionSort},{"merge",1,mergeSort},{"heap",0,heapSort}};
const char *kinds[5] = {"random","sorted","reversed","few_unique","nearly_sorted"};
static uint32_t nextRandom(uint32_t *x) { *x ^= *x << 13; *x ^= *x >> 17; *x ^= *x << 5; return *x; }
void makeInput(Record *a, size_t n, int kind, uint32_t seed) {
    uint32_t state = seed ? seed : 1;
    for (size_t i=0; i<n; i++) {
        int key = (int)(nextRandom(&state) % 1000001u) - 500000;
        if (kind == 1 || kind == 4) key = (int)i;
        if (kind == 2) key = (int)(n-i);
        if (kind == 3) key = (int)(nextRandom(&state) % 8u);
        a[i] = (Record){key,i};
    }
    if (kind == 4 && n > 1) {
        for (size_t i=0; i<n/100; i++) {
            size_t j=nextRandom(&state)%(n-1);
            int temp=a[j].key; a[j].key=a[j+1].key; a[j+1].key=temp;
        }
    }
}
int stableResult(const Record *a,size_t n) {
    for(size_t i=1;i<n;i++) if(a[i-1].key==a[i].key && a[i-1].tag>a[i].tag) return 0;
    return 1;
}
/* Check ordering AND exact preservation of input records using unique input tags. */
int validResult(const Record *input,const Record *a,size_t n) {
    unsigned char *seen=calloc(n?n:1,1); if(!seen) return 0;
    int ok=1;
    for(size_t i=0;i<n;i++) {
        size_t t=a[i].tag;
        if((i && a[i-1].key>a[i].key) || t>=n || seen[t] || a[i].key!=input[t].key) {ok=0;break;}
        seen[t]=1;
    }
    free(seen); return ok;
}
