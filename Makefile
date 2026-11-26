# The tests of env-web (see tst/run.sh): they need emcc, node with
# Playwright, python3, and a built checkout of ia-atmos/lang in ATMOS.

.PHONY: tests ide clean

tests:
	tst/run.sh

ide:
	python3 ide/serve.py

clean:
	rm -rf out tst/out ide/out ide/run .cache
