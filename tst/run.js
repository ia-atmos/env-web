// The tests of env-web, in Chromium (Playwright): tst/run.sh builds the
// pages into tst/out and serves them; this drives each one and checks
// the page.
const { chromium } = require('playwright');
const URL = process.env.URL || 'http://127.0.0.1:8771';
const SHOTS = process.env.SHOTS;    // a directory for screenshots
let fails = 0;
const check = (name, got, exp) => {
    const ok = JSON.stringify(got) === JSON.stringify(exp);
    if (!ok) fails++;
    console.log((ok ? 'ok  ' : 'FAIL') + ' ' + name + (ok ? '' : ' : got ' + JSON.stringify(got) + ', expected ' + JSON.stringify(exp)));
};

const tests = {
    counter: async (p) => {
        await p.waitForTimeout(300);
        check('counter: starts', await p.textContent('#msg'), 'running');
        for (let i=0; i<3; i++) await p.click('#inc');
        check('counter: 3 clicks', await p.textContent('#count'), '3');
        await p.waitForTimeout(2800);
        check('counter: 3 seconds', await p.textContent('#secs'), '3');
        await p.click('#stop');
        await p.click('#inc');
        await p.waitForTimeout(1300);
        check('counter: stopped', [await p.textContent('#msg'), await p.textContent('#count'), await p.textContent('#secs')], ['stopped', '3', '3']);
        check('counter: the program ended', await p.evaluate(() => Module.web.status), 1);
    },
    threads: async (p) => {
        await p.waitForTimeout(2500);
        check('threads: 3 threads', await p.locator('#tree > details').count(), 3);
        const r1 = await p.locator('#t1 > div').count();
        check('threads: replies of the first', r1 >= 10 && r1 <= 13, true);
        check('threads: a summary', await p.textContent('#t2 > summary'), 'chico: thread 2');
        check('threads: a fresh id', /^web\d+$/.test(await p.locator('#t1 > summary').getAttribute('id')), true);
        await p.click('#t2 > summary');
        await p.waitForTimeout(100);
        check('threads: one closed', await p.textContent('#open'), 'open: 2');
        await p.click('#t1-x');
        await p.waitForTimeout(100);
        check('threads: the first removed', [await p.locator('#t1').count(), await p.locator('#t2').count()], [0, 1]);
        await p.waitForTimeout(600);
        check('threads: the others go on', await p.locator('#t2 > div').count() >= 8, true);
    },
    form: async (p, logs) => {
        await p.waitForTimeout(300);
        check('form: number and boolean', await p.textContent('#num'), '10/false');
        await p.fill('#name', 'atmos');
        check('form: input', await p.textContent('#echo'), 'atmos');
        await p.click('#box');
        check('form: change', [await p.textContent('#state'), await p.getAttribute('#echo', 'class')], ['checked', 'on']);
        await p.click('#box');
        check('form: change back', [await p.textContent('#state'), await p.getAttribute('#echo', 'class')], ['unchecked', '']);
        await p.keyboard.press('a');
        check('form: key', await p.textContent('#key'), 'a/KeyA');
        await p.click('#color span');
        check('form: style, click inside', await p.textContent('#color2'), 'rgb(255, 0, 0)');
        await p.click('#hide');
        check('form: hidden', await p.isHidden('#echo'), true);
        await p.click('#bad');
        await p.waitForTimeout(100);
        check('form: the error ends the program', await p.evaluate(() => Module.web.status), 2);
        check('form: the message', logs.some(l => l.includes('web.set : no element : nope')), true);
    },
};

(async () => {
    const b = await chromium.launch();
    const only = process.argv.slice(2);
    for (const name of Object.keys(tests)) {
        if (only.length && !only.includes(name)) continue;
        const p = await b.newPage({ viewport: { width: 640, height: 480 } });
        const logs = [];
        p.on('console', m => logs.push(m.text()));
        p.on('pageerror', e => { logs.push('pageerror: ' + e.message); });
        await p.goto(URL + '/' + name + '.html');
        try {
            await tests[name](p, logs);
        } catch (e) {
            fails++;
            console.log('FAIL ' + name + ' : ' + e.message.split('\n')[0]);
        }
        check(name + ': no page error', logs.filter(l => l.startsWith('pageerror')), []);
        if (SHOTS) await p.screenshot({ path: SHOTS + '/' + name + '.png' });
        await p.close();
    }
    await b.close();
    console.log(fails ? fails + ' failed' : 'all passed');
    process.exit(fails ? 1 : 0);
})();
