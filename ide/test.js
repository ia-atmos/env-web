// The test of the IDE, in Chromium: start `python3 ide/serve.py 8090`,
// then `node ide/test.js [dir for screenshots]`.
const { chromium } = require('playwright');
const URL = process.env.URL || 'http://127.0.0.1:8090/';
const SHOTS = process.argv[2];
let fails = 0;
const check = (name, got, exp) => {
    const ok = JSON.stringify(got) === JSON.stringify(exp);
    if (!ok) fails++;
    console.log((ok ? 'ok  ' : 'FAIL') + ' ' + name + (ok ? '' : ' : got ' + JSON.stringify(got) + ', expected ' + JSON.stringify(exp)));
};
(async () => {
    const b = await chromium.launch();
    const p = await b.newPage({ viewport: { width: 1100, height: 600 } });
    const errs = [];
    p.on('pageerror', e => errs.push(e.message));
    await p.goto(URL);
    await p.waitForTimeout(500);
    check('the sample of the mode web', (await p.inputValue('#code')).startsWith(';; The DOM'), true);

    // web: run, then use the program inside the frame
    await p.click('#run');
    const f = p.frameLocator('#runner');
    await f.locator('#inc').click({ timeout: 60000 });
    await f.locator('#inc').click();
    check('web: the program runs in the frame', await f.locator('#count').textContent(), ' 2');
    check('web: no error', await p.textContent('#log'), '');
    if (SHOTS) await p.screenshot({ path: SHOTS + '/ide-web.png' });

    // an error of the compiler goes to the log
    await p.fill('#code', 'val x = \n');
    await p.click('#run');
    await p.waitForFunction(() => document.getElementById('log').textContent !== '', null, { timeout: 60000 });
    check('error: in the log', [(await p.textContent('#log')).includes('main.atm'), await p.getAttribute('#log', 'class')], [true, 'error']);
    if (SHOTS) await p.screenshot({ path: SHOTS + '/ide-error.png' });

    // pico: the mode changes the sample; run, and a canvas is drawn
    await p.selectOption('#mode', 'pico');
    check('the sample of the mode pico', (await p.inputValue('#code')).startsWith(';; pico'), true);
    await p.click('#run');
    await f.locator('canvas').waitFor({ timeout: 120000 });
    await p.waitForTimeout(1500);
    check('pico: no error', await p.textContent('#log'), '');
    const box = await f.locator('canvas').boundingBox();
    check('pico: a canvas with a size', box.width > 100 && box.height > 100, true);
    if (SHOTS) await p.screenshot({ path: SHOTS + '/ide-pico.png' });

    check('no page error', errs, []);
    await b.close();
    console.log(fails ? fails + ' failed' : 'all passed');
    process.exit(fails ? 1 : 0);
})();
