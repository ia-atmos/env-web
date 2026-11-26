// The test of the guides in the IDE, in Chromium: start
// `python3 ide/serve.py 8090`, then `node ide/test-guide.js [dir for screenshots]`.
const { chromium } = require('playwright');
const BASE = process.env.URL || 'http://127.0.0.1:8090';
const SHOTS = process.argv[2];
let fails = 0;
const check = (name, got, exp) => {
    const ok = JSON.stringify(got) === JSON.stringify(exp);
    if (!ok) fails++;
    console.log((ok ? 'ok  ' : 'FAIL') + ' ' + name + (ok ? '' : ' : got ' + JSON.stringify(got) + ', expected ' + JSON.stringify(exp)));
};
const step = async (p, i) => {
    await p.selectOption('#step', String(i));
    await p.waitForFunction((i) => document.getElementById('text').dataset.step === String(i), i);
};

// the parts common to every guide
const open = async (b, name, title, mode, n) => {
    const p = await b.newPage({ viewport: { width: 1400, height: 700 } });
    p.errs = [];
    p.on('pageerror', e => p.errs.push(e.message));
    await p.goto(BASE + '/guide/' + name);
    await p.waitForFunction(() => document.getElementById('text').dataset.step === '1');
    check(name + ': the title', await p.textContent('#title'), title);
    check(name + ': the mode', await p.inputValue('#mode'), mode);
    check(name + ': the steps', await p.locator('#step option').count(), n);
    const exs = [];
    for (let i = 1; i <= n; i++) {
        await step(p, i);
        exs.push(await p.locator('#text h3:has-text("Exercises") + ol > li').count());
    }
    check(name + ': two exercises in each step', exs, Array(n).fill(2));
    return p;
};

(async () => {
    const b = await chromium.launch();

    // birds (pico)
    let p = await open(b, 'birds', 'Birds: a tutorial of Atmos with pico', 'pico', 11);
    await step(p, 1);
    check('birds: step 1', [await p.textContent('#text h2'), (await p.inputValue('#code')).includes('spawn Bird(0.33, 0.15)')], ['1. A task', true]);
    await p.click('#next');
    await p.waitForFunction(() => document.getElementById('text').dataset.step === '2');
    check('birds: next', await p.inputValue('#step'), '2');
    const code = await p.inputValue('#code');
    await p.fill('#code', 'x');
    await p.click('#reset');
    await p.waitForFunction(() => document.getElementById('code').value !== 'x');
    check('birds: reset', await p.inputValue('#code'), code);
    await p.click('#run');
    await p.frameLocator('#runner').locator('canvas').waitFor({ timeout: 120000 });
    await p.waitForTimeout(2500);
    check('birds: run, no error', await p.textContent('#log'), '');
    if (SHOTS) await p.screenshot({ path: SHOTS + '/guide-birds.png' });
    check('birds: no page error', p.errs, []);
    await p.close();

    // atmos (text): the output of a step is the one that its text shows
    p = await open(b, 'atmos', 'A tour of Atmos', 'text', 21);
    for (const i of [3, 13, 17]) {
        await step(p, i);
        const exp = await p.textContent('#text h3:has-text("Output") + pre');
        const src = await p.getAttribute('#runner', 'src');
        await p.click('#run');
        await p.waitForFunction((src) => document.getElementById('runner').getAttribute('src') !== src, src, { timeout: 120000 });
        const f = p.frameLocator('#runner');
        await f.locator('#end:has-text("ended")').waitFor({ timeout: 120000 });
        // in the IDE the program is `main.atm`, whatever its name in the guide
        const got = (await f.locator('#out').textContent()).replace(/main\.atm/g, 'NAME.atm');
        check('atmos: step ' + i + ' prints what its text shows', got, exp.replace(/[\w-]+\.atm/g, 'NAME.atm'));
        if (SHOTS && i === 13) await p.screenshot({ path: SHOTS + '/guide-atmos.png' });
    }
    check('atmos: no page error', p.errs, []);
    await p.close();

    await b.close();
    console.log(fails ? fails + ' failed' : 'all passed');
    process.exit(fails ? 1 : 0);
})();
