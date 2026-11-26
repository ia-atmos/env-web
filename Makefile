# The tests of env-web (see tst/run.sh): they need emcc, node with
# Playwright, python3, and a built checkout of ia-atmos/lang in ATMOS.

.PHONY: tests clean

tests:
	tst/run.sh

clean:
	rm -rf out tst/out
