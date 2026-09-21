#include "sort.h"
#include <stdlib.h>
/* Bottom-up merge: no recursion; one reusable n-record buffer.
 * No ordered-boundary shortcut, so the implementation choice is explicit. */
int mergeSort(Record *a, size_t n, Stats *s) {
    if (s) *s = (Stats){0};
    if (n < 2) return 1;
    if (n > SIZE_MAX / sizeof(Record)) return 0;
    Record *buf = malloc(n * sizeof(*buf));
    if (!buf) return 0;
    if (s) s->bufferBytes = n * sizeof(*buf);
    for (size_t w = 1; w < n;) {
        for (size_t lo = 0; lo < n;) {
            size_t mid = lo + (n - lo < w ? n - lo : w);
            size_t hi = mid + (n - mid < w ? n - mid : w);
            size_t i = lo, j = mid, k = lo;
            while (i < mid && j < hi) {
                /* Left wins ties, preserving input order. */
                if (compare(a[i], a[j], s) <= 0) moveRecord(&buf[k++], a[i++], s);
                else moveRecord(&buf[k++], a[j++], s);
            }
            while (i < mid) moveRecord(&buf[k++], a[i++], s);
            while (j < hi) moveRecord(&buf[k++], a[j++], s);
            for (k = lo; k < hi; k++) moveRecord(&a[k], buf[k], s);
            lo = hi;
        }
        if (w > n / 2) break;
        w *= 2;
    }
    free(buf); return 1;
}
