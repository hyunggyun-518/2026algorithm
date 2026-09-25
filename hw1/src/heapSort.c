#include "sort.h"
/* [0,n) is the active heap. Children of i are 2*i+1 and 2*i+2. */
static void siftDown(Record *a, size_t root, size_t n, Stats *s) {
    while (root < n / 2) {
        size_t child = 2 * root + 1;
        if (child + 1 < n && compare(a[child], a[child + 1], s) < 0) child++;
        if (compare(a[root], a[child], s) >= 0) break;
        swapRecord(&a[root], &a[child], s);
        root = child;
    }
}
int heapSort(Record *a, size_t n, Stats *s) {
    if (s) *s = (Stats){0, 0, n > 1 ? sizeof(Record) : 0};
    for (size_t i = n / 2; i > 0; i--) siftDown(a, i - 1, n, s);
    for (size_t end = n; end > 1; end--) {
        swapRecord(&a[0], &a[end - 1], s);
        siftDown(a, 0, end - 1, s);
    }
    return 1;
}
