// Drives the prototype in Chromium: serve the output of build.sh on
// port 8766 (python3 -m http.server 8766), then: node test.js [shot.png]
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  const logs = [];
  p.on('console', m => logs.push(m.type()+': '+m.text()));
  p.on('pageerror', e => logs.push('pageerror: '+e.message));
  await p.goto(process.env.URL || 'http://127.0.0.1:8766/counter.html');
  await p.waitForTimeout(500);
  const q = async () => ({msg: await p.textContent('#msg'), count: await p.textContent('#count'), secs: await p.textContent('#secs')});
  console.log('t0.5', JSON.stringify(await q()));
  for (let i=0;i<3;i++) await p.click('#inc');
  console.log('3 clicks', JSON.stringify(await q()));
  await p.waitForTimeout(2600);
  console.log('t3.1', JSON.stringify(await q()));
  await p.click('#stop');
  await p.waitForTimeout(300);
  await p.click('#inc');
  await p.waitForTimeout(1200);
  console.log('after stop', JSON.stringify(await q()), 'status', await p.evaluate(()=>Module.status));
  console.log('out:', JSON.stringify(await p.textContent('#out')));
  await p.screenshot({path: process.argv[2] || 'dom.png'});
  console.log(logs.join('\n'));
  await b.close();
})();
