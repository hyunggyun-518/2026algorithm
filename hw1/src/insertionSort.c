#include "sort.h"
int insertionSort(Record *a, size_t n, Stats *s) {
    if (s) *s = (Stats){0, 0, n > 1 ? sizeof(Record) : 0};
    for (size_t i = 1; i < n; i++) {
        if (compare(a[i - 1], a[i], s) <= 0) continue;
        Record temp; moveRecord(&temp, a[i], s);
        size_t j = i;
        while (j && compare(a[j - 1], temp, s) > 0) {
            moveRecord(&a[j], a[j - 1], s); j--;
        }
        moveRecord(&a[j], temp, s);
    }
    return 1;
}
