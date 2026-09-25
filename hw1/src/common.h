#ifndef COMMON_H
#define COMMON_H
#include "sort.h"
extern const char *kinds[5];
void makeInput(Record *, size_t, int, uint32_t);
int validResult(const Record *, const Record *, size_t);
int stableResult(const Record *, size_t);
#endif
