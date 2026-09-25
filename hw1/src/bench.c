#include "common.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
static volatile unsigned long consumed=0;
static void fail(const char *message){fprintf(stderr,"%s\n",message);exit(1);}
int main(int argc, char **argv) {
    int large = argc > 1 && strcmp(argv[1], "--large") == 0;
    setvbuf(stdout, NULL, _IOLBF, 0);
    const size_t smallSizes[]={256,512,1024,2048,4096,8192};
    const size_t largeSizes[]={8192,16384,32768,65536,131072,262144,524288,1048576};
    const size_t *sizes=large?largeSizes:smallSizes;
    printf("kind,n,seed,repeat,algo,ms,batch,compares,moves,buffer_bytes,stable_observed,record_bytes\n");
    for(size_t z=0;z<(large?8u:6u);z++) for(int kind=0;kind<(large?1:5);kind++) for(uint32_t seed=1;seed<=3;seed++) {
        size_t n=sizes[z];Record *input=malloc(n*sizeof(Record)),*work=malloc(n*sizeof(Record));
        if(!input||!work) fail("allocation failure");
        makeInput(input,n,kind,20260921u+seed);
        size_t first=0;
        size_t count=3-first;
        Stats stats[3];int stable[3];size_t batch[3];
        for(size_t k=first;k<3;k++) {
            memcpy(work,input,n*sizeof(Record));
            if(!algorithms[k].sort(work,n,&stats[k])||!validResult(input,work,n))fail("invalid instrumented result");
            stable[k]=stableResult(work,n);
            /* Warm up and calibrate batch for ~5 ms of sorting, max 4096 arrays. */
            memcpy(work,input,n*sizeof(Record));clock_t begin=clock();
            if(!algorithms[k].sort(work,n,NULL))fail("warmup failed");
            double sec=(double)(clock()-begin)/CLOCKS_PER_SEC;
            batch[k]=sec>0?(size_t)(0.005/sec)+1:4096;
            if(batch[k]>4096)batch[k]=4096;
            size_t cap=64u*1024u*1024u/(n*sizeof(Record));
            if(batch[k]>cap)batch[k]=cap;
            if(batch[k]<1)batch[k]=1;
        }
        for(int rep=0;rep<(large?3:5);rep++) for(size_t offset=0;offset<count;offset++) {
            size_t k=first+((size_t)rep+seed+offset)%count,b=batch[k];
            Record *many=malloc(b*n*sizeof(Record));if(!many)fail("batch allocation failed");
            for(size_t j=0;j<b;j++)memcpy(many+j*n,input,n*sizeof(Record));
            clock_t begin=clock();
            for(size_t j=0;j<b;j++)if(!algorithms[k].sort(many+j*n,n,NULL))fail("timed sort failed");
            clock_t end=clock();
            for(size_t j=0;j<b;j++) {
                if(!validResult(input,many+j*n,n))fail("invalid timed result");
                if(algorithms[k].stable&&!stableResult(many+j*n,n))fail("stability violated");
                consumed+=(unsigned long)many[j*n].tag;
            }
            printf("%s,%zu,%u,%d,%s,%.9f,%zu,%llu,%llu,%zu,%d,%zu\n",kinds[kind],n,20260921u+seed,rep,algorithms[k].name,
                (double)(end-begin)*1000/CLOCKS_PER_SEC/b,b,
                (unsigned long long)stats[k].compares,(unsigned long long)stats[k].moves,stats[k].bufferBytes,stable[k],sizeof(Record));
            free(many);
        }
        free(work);free(input);
    }
    return 0;
}
