#include "common.h"
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static size_t checks=0;
static int intCompare(const void *a,const void *b) {int x=*(const int*)a,y=*(const int*)b;return (x>y)-(x<y);}
static void require(int ok,const char *label) {checks++;if(!ok){fprintf(stderr,"FAIL: %s\n",label);exit(1);}}
static void check(const int *keys,size_t n) {
    Record input[600],a[600]; int want[600];
    for(size_t i=0;i<n;i++){input[i]=(Record){keys[i],i};want[i]=keys[i];}
    qsort(want,n,sizeof(int),intCompare);
    for(size_t k=0;k<3;k++) {
        memcpy(a,input,n*sizeof(Record)); Stats s;
        require(algorithms[k].sort(a,n,&s),"sort success");
        require(validResult(input,a,n),"order and permutation");
        for(size_t i=0;i<n;i++) require(a[i].key==want[i],"qsort key match");
        if(algorithms[k].stable) require(stableResult(a,n),"stable algorithm preserves ties");
        memcpy(a,input,n*sizeof(Record));
        require(algorithms[k].sort(a,n,NULL) && validResult(input,a,n),"uninstrumented path");
    }
}
int main(void) {
    int keys[600];
    /* All ternary-key arrays, lengths 0..8: 9841 complete inputs. */
    size_t count=1;
    for(size_t n=0;n<=8;n++) {
        for(size_t code=0;code<count;code++) {
            size_t x=code;for(size_t i=0;i<n;i++){keys[i]=(int)(x%3)-1;x/=3;}check(keys,n);
        }
        count*=3;
    }
    for(size_t n=0;n<=513;n++) for(int kind=0;kind<5;kind++) {
        Record a[600];makeInput(a,n,kind,20260921u+(uint32_t)n);
        for(size_t i=0;i<n;i++)keys[i]=a[i].key;
        check(keys,n);
    }
    int extremes[]={INT_MIN,INT_MAX,0,INT_MIN,-1,INT_MAX};check(extremes,6);
    Record equal[]={{1,0},{1,1}};Stats s;
    require(heapSort(equal,2,&s) && !stableResult(equal,2),"heap instability witness");
    Record sorted[]={{0,0},{1,1},{2,2},{3,3}};
    insertionSort(sorted,4,&s);require(s.compares==3 && s.moves==0,"insertion best case counters");
    Record x[]={{2,0},{1,1}};
    heapSort(x,2,&s);require(s.compares==1 && s.moves==3,"heap two element counters");
    mergeSort(x,2,&s);require(s.moves==4 && s.bufferBytes==2*sizeof(Record),"merge buffer accounting");
    Record original[]={{1,0},{2,1}},bad[]={{1,0},{1,0}};
    require(!validResult(original,bad,2),"validator rejects record loss");
    printf("PASS: %zu assertions; exhaustive ternary inputs n=0..8; five shapes n=0..513; extremes; stability; counters.\n",checks);
    return 0;
}
