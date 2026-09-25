#ifndef SORT_H
#define SORT_H
#include <stddef.h>
#include <stdint.h>
typedef struct { int key; size_t tag; } Record;
typedef struct { uint64_t compares, moves; size_t bufferBytes; } Stats;
typedef int (*SortFn)(Record *, size_t, Stats *);
typedef struct { const char *name; int stable; SortFn sort; } Algorithm;
extern const Algorithm algorithms[3];
int insertionSort(Record *, size_t, Stats *);
int mergeSort(Record *, size_t, Stats *);
int heapSort(Record *, size_t, Stats *);
/* key comparisons only; tag must never influence ordering. */
static inline int compare(Record a, Record b, Stats *s) {
    if (s) s->compares++;
    return (a.key > b.key) - (a.key < b.key);
}
static inline void moveRecord(Record *a, Record b, Stats *s) {
    *a = b; if (s) s->moves++;
}
static inline void swapRecord(Record *a, Record *b, Stats *s) {
    Record temp; moveRecord(&temp, *a, s); moveRecord(a, *b, s); moveRecord(b, temp, s);
}
#endif
