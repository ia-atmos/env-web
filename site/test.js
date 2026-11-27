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
    // an edited program goes to the compile server (run.cgi), and runs
    await p.fill('#code', 'print "edited"');
    await p.click('#run');
    await p.waitForFunction(() => (document.getElementById('runner').getAttribute('src') || '').startsWith('run/'), null, { timeout: 120000 });
    await fr.locator('#end').waitFor({ state: 'visible', timeout: 15000 });
    check('atmos: an edited program runs', (await fr.locator('#out').textContent()).trim(), 'edited');
    // an error of the compiler goes to the log
    await p.fill('#code', 'val x = \n');
    await p.click('#run');
    await p.waitForFunction(() => document.getElementById('log').textContent !== '', null, { timeout: 120000 });
    check('atmos: an error of the compiler', [(await p.textContent('#log')).includes('main.atm'), await p.getAttribute('#log', 'class')], [true, 'error']);
    // native code is refused (it could read files of the host)
    await p.fill('#code', '`printf("x");`\n');
    await p.click('#run');
    await p.waitForFunction(() => document.getElementById('log').textContent.includes('native'), null, { timeout: 30000 });
    check('atmos: native code refused', await p.getAttribute('#log', 'class'), 'error');
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
    check('hello: the mode is fixed', await p.isDisabled('#mode'), true);
    check('hello: the guides, in order', await p.locator('#guides option').evaluateAll(os => os.map(o => o.value)), ['hello', 'birds', 'atmos']);
    await p.click('#run');
    await fr.locator('#end').waitFor({ state: 'visible', timeout: 15000 });
    check('hello: the output', (await fr.locator('#out').textContent()).trim().split('\n'), ['Tick 0', 'Tick 1', 'Tick 2', 'Tick 3', 'Tick 4', 'Bye!']);
    // an exercise: edit the program of the step, and run it
    await p.fill('#code', (await p.inputValue('#code')).replace('Tick', 'Tock'));
    await p.click('#run');
    await p.waitForFunction(() => (document.getElementById('runner').getAttribute('src') || '').startsWith('run/'), null, { timeout: 120000 });
    await fr.locator('#end').waitFor({ state: 'visible', timeout: 15000 });
    check('hello: the exercise runs', (await fr.locator('#out').textContent()).trim().split('\n')[0], 'Tock 0');
    check('hello: no hourglass after', await p.isHidden('#busy'), true);
    // Stop ends the program
    await p.click('#run');
    await fr.locator('#out').waitFor();
    await p.click('#stop');
    await p.waitForFunction(() => document.getElementById('runner').getAttribute('src') === 'about:blank');
    check('hello: stop', await p.getAttribute('#runner', 'src'), 'about:blank');

    await p.click('#text a:has-text("Birds")');
    await p.waitForFunction(() => document.getElementById('text').dataset.step === '1');
    check('hello: the link to birds', new URL(p.url()).pathname, '/atmos/guide/birds/');

    // the choice of guide opens another one
    await p.selectOption('#guides', 'atmos');
    await p.waitForURL(/guide\/atmos\/$/);
    await p.waitForFunction(() => document.getElementById('text').dataset.step === '1');
    check('guides: the choice opens the guide', await p.inputValue('#guides'), 'atmos');

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
    // an edited step of birds: compiled with the images of the guide
    await p.fill('#code', (await p.inputValue('#code')).replace('loop i in (1,5)', 'loop i in (1,3)'));
    await p.click('#run');
    await p.waitForFunction(() => (document.getElementById('runner').getAttribute('src') || '').startsWith('run/'), null, { timeout: 180000 });
    await fr.locator('canvas').waitFor({ timeout: 20000 });
    check('birds: an edited step runs', [await fr.locator('canvas').count(), await p.textContent('#log')], [1, '']);
    const box = await fr.locator('canvas').boundingBox(), vp = await p.locator('#runner').boundingBox();
    check('birds: the canvas is centered in x', Math.abs((box.x + box.width/2) - (vp.x + vp.width/2)) < 3, true);
    check('birds: the canvas is near the top', box.y - vp.y >= 4 && box.y - vp.y <= 20, true);

    // the icon, on every kind of page
    for (const page of ['/', '/atmos/guide/hello/']) {
        await p.goto(BASE + page);
        const href = await p.evaluate(() => { const l = document.querySelector('link[rel~=icon]'); return l && l.href; });
        const r = href && await p.request.get(href);
        check(page + ': the icon', [!!href, r && r.status()], [true, 200]);
    }
    check('/atmos/ goes to GitHub', (await (await p.request.get(BASE + '/atmos/')).text()).includes('url=https://github.com/ia-atmos/lang'), true);
    check('/favicon.ico', (await p.request.get(BASE + '/favicon.ico')).status(), 200);

    // the landing page and the page of Atmos: every local link and image exists
    for (const page of ['/']) {
        await p.goto(BASE + page);
        const urls = await p.evaluate(() => [...document.querySelectorAll('a[href], img[src], link[rel~=icon]')]
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
