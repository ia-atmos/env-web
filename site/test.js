// The test of the static site, in Chromium: build it (site/build.py),
// serve its folder (`python3 -m http.server 8091 -d <outdir>`), then
// `node site/test.js [dir for screenshots]`.
const { chromium } = require('playwright');
const BASE = process.env.URL || 'http://127.0.0.1:8091';
const SHOTS = process.argv[2];
let fails = 0;
const check = (name, got, exp) => {
    const ok = JSON.stringify(got) === JSON.stringify(exp);
    if (!ok) fails++;
    console.log((ok ? 'ok  ' : 'FAIL') + ' ' + name + (ok ? '' : ' : got ' + JSON.stringify(got) + ', expected ' + JSON.stringify(exp)));
};
(async () => {
    const b = await chromium.launch();
    const p = await b.newPage({ viewport: { width: 1400, height: 700 } });
    const errs = [];
    p.on('pageerror', e => errs.push(e.message));
    const open = async (name) => {
        await p.goto(BASE + '/atmos/guide/' + name + '/');
        await p.waitForFunction(() => document.getElementById('text').dataset.step === '1');
    };

    // atmos (text): step 1 runs as it is, and prints what its .out says
    await open('atmos');
    check('atmos: the steps', await p.locator('#step option').count(), 21);
    await p.click('#run');
    const fr = p.frameLocator('#runner');
    await fr.locator('#end').waitFor({ state: 'visible', timeout: 15000 });
    const out = await fr.locator('#out').textContent();
    check('atmos: step 1 printed something', out.trim().length > 0, true);
    // an edited program needs a server
    await p.fill('#code', 'print "x"');
    await p.click('#run');
    await p.waitForFunction(() => document.getElementById('log').textContent.includes('no compile server'));
    check('atmos: edited program, no server', await p.getAttribute('#log', 'class'), 'error');
    // reset gives the guide's program back, and Run shows it again
    await p.click('#reset');
    await p.waitForFunction(() => document.getElementById('code').value !== 'print "x"');
    await p.click('#run');
    await p.waitForFunction(() => document.getElementById('log').textContent === '');
    check('atmos: reset then run', await p.getAttribute('#log', 'class') === 'error', false);

    // hello (the example of the landing): runs, two exercises, and its
    // link to birds opens birds in the same page
    await open('hello');
    check('hello: one step', await p.locator('#step option').count(), 1);
    check('hello: two exercises', await p.locator('#text h3:has-text("Exercises") + ol > li').count(), 2);
    check('hello: the mode', await p.inputValue('#mode'), 'text');
    await p.click('#run');
    await fr.locator('#end').waitFor({ state: 'visible', timeout: 15000 });
    check('hello: the output', (await fr.locator('#out').textContent()).trim().split('\n'), Array(4).fill('Hello World!'));
    await p.click('#text a:has-text("Birds")');
    await p.waitForFunction(() => document.getElementById('text').dataset.step === '1');
    check('hello: the link to birds', new URL(p.url()).pathname, '/atmos/guide/birds/');

    // birds (pico): a canvas appears in the runner
    await open('birds');
    check('birds: the steps', await p.locator('#step option').count(), 11);
    await p.selectOption('#step', '3');
    await p.waitForFunction(() => document.getElementById('text').dataset.step === '3');
    await p.click('#run');
    await fr.locator('canvas').waitFor({ timeout: 20000 });
    await p.waitForTimeout(1500);
    if (SHOTS) await p.screenshot({ path: SHOTS + '/site-birds-3.png' });
    check('birds: step 3 has a canvas', await fr.locator('canvas').count(), 1);

    // the landing page and the page of Atmos: every local link and image exists
    for (const page of ['/', '/atmos/']) {
        await p.goto(BASE + page);
        const urls = await p.evaluate(() => [...document.querySelectorAll('a[href], img[src]')]
            .map(e => e.href || e.src).filter(u => u.startsWith(location.origin) && !u.includes('/ceu/')));
        const bad = [];
        for (const u of new Set(urls.map(u => u.split('#')[0]))) {
            const r = await p.request.get(u);
            if (r.status() !== 200) bad.push(u.slice(BASE.length) + ' ' + r.status());
        }
        check(page + ': local links', bad, []);
    }
    check('no page error', errs, []);
    console.log(fails ? fails + ' failed' : 'all passed');
    await b.close();
    process.exit(fails ? 1 : 0);
})();
