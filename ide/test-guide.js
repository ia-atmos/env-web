// The test of a guide in the IDE, in Chromium: start
// `python3 ide/serve.py 8090`, then `node ide/test-guide.js [dir for screenshots]`.
const { chromium } = require('playwright');
const URL = process.env.URL || 'http://127.0.0.1:8090/guide/birds';
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
    await p.goto(URL);
    await p.waitForFunction(() => document.getElementById('code').value !== '');
    check('the title', await p.textContent('#title'), 'Birds: a tutorial of Atmos with pico');
    check('11 steps', await p.locator('#step option').count(), 11);
    check('the mode of the guide', await p.inputValue('#mode'), 'pico');
    check('step 1: its title', await p.textContent('#text h2'), '1. A task');
    check('step 1: its program', (await p.inputValue('#code')).includes('spawn Bird(0.33, 0.15)'), true);

    // every step has exactly two exercises
    const exs = [];
    for (let i = 1; i <= 11; i++) {
        await p.selectOption('#step', String(i));
        await p.waitForFunction((i) => document.querySelector('#text h2').textContent.startsWith(i + '. '), i);
        exs.push(await p.locator('#text ol li').count());
    }
    check('two exercises in each step', exs, Array(11).fill(2));

    // prev and next, and reset after an edit
    await p.click('#prev');
    await p.waitForFunction(() => document.querySelector('#text h2').textContent.startsWith('10. '));
    check('prev: step 10', await p.inputValue('#step'), '10');
    await p.selectOption('#step', '2');
    await p.waitForFunction(() => document.querySelector('#text h2').textContent.startsWith('2. '));
    await p.waitForFunction(() => document.getElementById('code').value.includes('mouse.button.dn'));
    const code = await p.inputValue('#code');
    await p.fill('#code', 'x');
    await p.click('#reset');
    await p.waitForFunction(() => document.getElementById('code').value !== 'x');
    check('reset: the program of the step again', await p.inputValue('#code'), code);

    // run the step: the birds on a canvas
    await p.click('#run');
    const f = p.frameLocator('#runner');
    await f.locator('canvas').waitFor({ timeout: 120000 });
    await p.waitForTimeout(2500);
    check('run: no error', await p.textContent('#log'), '');
    if (SHOTS) await p.screenshot({ path: SHOTS + '/guide-birds.png' });

    check('no page error', errs, []);
    await b.close();
    console.log(fails ? fails + ' failed' : 'all passed');
    process.exit(fails ? 1 : 0);
})();
