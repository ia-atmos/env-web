# The tests of env-web (see tst/run.sh): they need emcc, node with
# Playwright, python3, and a built checkout of ia-atmos/lang in ATMOS.

.PHONY: tests ide site clean

tests:
	tst/run.sh

ide:
	python3 ide/serve.py

# the whole site, as it is published (without ceu/), at http://127.0.0.1:8091/
site:
	python3 site/build.py site/out 4
	python3 -m http.server 8091 -d site/out

clean:
	rm -rf out tst/out ide/out ide/run site/out .cache
