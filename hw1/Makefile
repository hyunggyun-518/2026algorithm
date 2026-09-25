CC = cc
CFLAGS = -std=c17 -Wall -Wextra -Wpedantic -O2
SRC = src/common.c src/insertionSort.c src/mergeSort.c src/heapSort.c
HEADERS = src/sort.h src/common.h
.PHONY: all test sanitize bench clean
all: test
src/bench.out: src/bench.c $(SRC) $(HEADERS)
	$(CC) $(CFLAGS) -Isrc $< $(SRC) -o $@
tests/test_sort.out: tests/test_sort.c $(SRC) $(HEADERS)
	$(CC) $(CFLAGS) -Isrc $< $(SRC) -o $@
test: tests/test_sort.out
	./tests/test_sort.out
sanitize:
	$(CC) -std=c17 -Wall -Wextra -Wpedantic -g -O1 -fsanitize=address,undefined -Isrc tests/test_sort.c $(SRC) -o tests/sanitize.out
	./tests/sanitize.out
bench: src/bench.out
	./src/bench.out > data/raw.csv
clean:
	rm -f src/*.out tests/*.out
.PHONY: large report
large: src/bench.out
	./src/bench.out --large > data/large-raw.csv
report:
	python3 tools/analyze.py
