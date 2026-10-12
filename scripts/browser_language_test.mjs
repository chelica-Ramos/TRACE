// No test libraries required. Connect to a separate headless Edge/Chrome profile
// launched with --remote-debugging-port=9223, while Streamlit runs on port 8502.
import assert from 'node:assert/strict';
import fs from 'node:fs';

const pages = await (await fetch('http://127.0.0.1:9223/json/list')).json();
const page = pages.find(item => item.type === 'page');
const socket = new WebSocket(page.webSocketDebuggerUrl);
await new Promise(resolve => socket.addEventListener('open', resolve, {once:true}));
let id = 0;
const pending = new Map();
const exceptions = [];
socket.addEventListener('message', event => {
  const message = JSON.parse(event.data);
  if (message.id) {
    const request = pending.get(message.id);
    pending.delete(message.id);
    message.error ? request.reject(message.error) : request.resolve(message.result);
  }
  if (message.method === 'Runtime.exceptionThrown') exceptions.push(message.params.exceptionDetails);
});
function call(method, params={}) {
  return new Promise((resolve,reject) => {
    const n=++id; pending.set(n,{resolve,reject});
    socket.send(JSON.stringify({id:n,method,params}));
  });
}
async function evaluate(expression) {
  const result = await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});
  if (result.exceptionDetails) throw new Error(JSON.stringify(result.exceptionDetails));
  return result.result.value;
}
async function wait(expression, timeout=30000) {
  const started=Date.now();
  while (Date.now()-started < timeout) {
    if (await evaluate(`Boolean(${expression})`)) return;
    await new Promise(resolve=>setTimeout(resolve,150));
  }
  throw new Error('Timed out: '+expression);
}
async function click(expression) {
  const point = await evaluate(`(() => {const element=${expression};element.scrollIntoView({block:'center'});const rect=element.getBoundingClientRect();return {x:rect.x+rect.width/2,y:rect.y+rect.height/2};})()`);
  await call('Input.dispatchMouseEvent',{type:'mousePressed',button:'left',clickCount:1,...point});
  await call('Input.dispatchMouseEvent',{type:'mouseReleased',button:'left',clickCount:1,...point});
}
const switchRoot = `[...document.querySelectorAll('*')].map(e=>e.shadowRoot).find(root=>root?.querySelector('.trace-language-switch'))`;
const activeTab = `[...document.querySelectorAll('[role="tab"]')].findIndex(tab=>tab.getAttribute('aria-selected')==='true')`;
try {
  await call('Runtime.enable'); await call('Page.enable');
  await call('Emulation.setDeviceMetricsOverride',{width:1280,height:900,deviceScaleFactor:1,mobile:false});
  await call('Page.navigate',{url:'http://localhost:8502'});
  await wait(`document.querySelector('[data-testid="stChatInput"]') && (${switchRoot})`);
  await evaluate(`localStorage.setItem('trace.ui.language','en')`);
  await evaluate(`window.__beforeLanguageReload=true`);
  await call('Page.reload');
  await wait(`!window.__beforeLanguageReload && document.querySelector('input[aria-label="Region"]') && document.querySelector('[data-testid="stChatInput"]') && document.documentElement.lang==='en'`);
  await evaluate(`window.__traceLanguageTestToken='same-document'; if(document.querySelector('[data-testid="stSidebar"]').getAttribute('aria-expanded')==='false') [...document.querySelectorAll('button')].find(button=>button.innerText==='keyboard_double_arrow_right')?.click()`);
  await wait(`document.querySelector('input[aria-label="Region"]').getBoundingClientRect().x>=0`);
  await click(`document.querySelector('input[aria-label="Region"]')`);
  await wait(`document.querySelector('[role="option"]')`);
  const selectedRegion = await evaluate(`[...document.querySelectorAll('[role="option"]')].find(option=>option.textContent.trim()!=='Select all').textContent.trim()`);
  await evaluate(`[...document.querySelectorAll('[role="option"]')].find(option=>option.textContent.trim()!=='Select all').click()`);
  await wait(`document.querySelector('[data-testid="stMultiSelect"]').innerText.includes(${JSON.stringify(selectedRegion)})`);
  await evaluate(`document.querySelectorAll('[role="tab"]')[1].click()`);
  await wait(`(${activeTab})===1`);
  await evaluate(`(() => {const input=document.querySelector('input[aria-label="Search Contract ID or Description"]'); const setter=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set; setter.call(input,'NO_MATCH_LANGUAGE_TEST'); input.dispatchEvent(new Event('input',{bubbles:true})); input.focus();})()`);
  await call('Input.dispatchKeyEvent',{type:'keyDown',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});
  await call('Input.dispatchKeyEvent',{type:'keyUp',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});
  await wait(`document.body.innerText.includes('No matching projects in this scope.')`);
  await evaluate(`document.querySelectorAll('[role="tab"]')[3].click()`);
  await wait(`(${activeTab})===3`);
  await evaluate(`(${switchRoot}).querySelector('[data-language="tl"]').click()`);
  await wait(`document.documentElement.lang==='tl' && document.body.innerText.includes('Walang available na data ng aktuwal na bayad.')`);
  await wait(`(${activeTab})===3 && document.querySelector('input[aria-label="Maghanap gamit ang Contract ID o Description"]')?.value==='NO_MATCH_LANGUAGE_TEST'`);
  assert.equal(await evaluate(`window.__traceLanguageTestToken`),'same-document');
  assert.equal(await evaluate(`localStorage.getItem('trace.ui.language')`),'tl');
  assert.ok(await evaluate(`document.querySelector('[data-testid="stMultiSelect"]').innerText.includes(${JSON.stringify(selectedRegion)})`));
  assert.ok(await evaluate(`document.body.innerText.includes('Malaki ang mata, naka-hard hat, at uhaw sa sagot.')`));
  await evaluate(`document.querySelectorAll('[role="tab"]')[1].click()`);
  await wait(`(${activeTab})===1`);
  await evaluate(`(${switchRoot}).querySelector('[data-language="en"]').click()`);
  await wait(`document.documentElement.lang==='en' && document.body.innerText.includes('No matching projects in this scope.') && (${activeTab})===1`);
  await evaluate(`(${switchRoot}).querySelector('[data-language="tl"]').click()`);
  await wait(`document.documentElement.lang==='tl' && document.body.innerText.includes('Walang tugmang project sa saklaw na ito.')`);
  await evaluate(`window.__beforeLanguageReload=true`);
  await call('Page.reload');
  await wait(`!window.__beforeLanguageReload && document.documentElement.lang==='tl' && document.body.innerText.includes('Walang available na data ng aktuwal na bayad.') && document.querySelector('[data-testid="stChatInput"]')`);
  await call('Emulation.setDeviceMetricsOverride',{width:375,height:812,deviceScaleFactor:1,mobile:true});
  const rect = await evaluate(`(() => {const button=(${switchRoot}).querySelector('[data-language="en"]');const r=button.getBoundingClientRect();return {left:r.left,right:r.right,width:r.width,height:r.height};})()`);
  assert.ok(rect.left>=0 && rect.right<=375 && rect.width>=44 && rect.height>=36, JSON.stringify(rect));
  const screenshot=await call('Page.captureScreenshot',{format:'png'});
  fs.writeFileSync('.cache/language-mobile.png',Buffer.from(screenshot.data,'base64'));
  assert.deepEqual(exceptions,[]);
  console.log('PASS: browser EN/TL switching without document reload; tab, region and search preserved; localStorage restored on revisit; mobile toggle fits; no JavaScript exceptions.');
} finally {
  socket.close();
}
