#!/usr/bin/env node
'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root,'index.html'),'utf8');

test('navigation, evidence and local asset references resolve', () => {
  const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);
  assert.equal(new Set(ids).size, ids.length, 'duplicate HTML IDs');
  for (const [,target] of html.matchAll(/(?:href|src)="([^"]+)"/g)) {
    if (target.startsWith('#')) {
      if (target.length>1) assert.ok(ids.includes(target.slice(1)),`missing anchor: ${target}`);
    } else if (!target.startsWith('https://')) {
      assert.ok(fs.existsSync(path.resolve(root,target)),`missing local asset: ${target}`);
    }
  }
  assert.ok(!/https?:\/\//.test(fs.readFileSync(path.join(root,'styles.css'),'utf8')), 'external CSS dependency');
});

test('pace toggle renders both datasets, updates accessibility state and restores constructor view', () => {
  const nodes = new Map([...html.matchAll(/\bid="([^"]+)"/g)].map(m=>[m[1],{innerHTML:'',textContent:''}]));
  const buttons = ['teams','drivers'].map(view=>({dataset:{view},attributes:{},setAttribute(k,v){this.attributes[k]=v;},addEventListener(event,callback){this[event]=callback;}}));
  const document = {getElementById:id=>{assert.ok(nodes.has(id),`unknown element ${id}`);return nodes.get(id);},querySelectorAll:selector=>{assert.equal(selector,'[data-view]');return buttons;}};
  // Include controls created by app.js so scrubber failures cannot hide in its fallback.
  for (const id of ['phase-slider','phase-readout','phase-play','progress-cursor']) nodes.set(id, {innerHTML:'',textContent:'',value:0});
  const ring = {attributes:{},setAttribute(k,v){this.attributes[k]=v;}};
  for (const node of nodes.values()) Object.assign(node, {
    attributes:{}, style:{setProperty(){}},
    setAttribute(k,v){this.attributes[k]=v;},
    addEventListener(event,callback){this[event]=callback;},
    querySelector(){return ring;}
  });
  let tick = null;
  const context=vm.createContext({document,
    setInterval(callback){tick=callback;return 1;},
    clearInterval(){tick=null;}
  });
  vm.runInContext(fs.readFileSync(path.join(root,'app.js'),'utf8'),context);
  assert.equal(buttons[0].attributes['aria-pressed'],'true');
  assert.equal((nodes.get('pace-chart').innerHTML.match(/class="bar-row(?: [^"]*)?"/g)||[]).length,10);
  assert.match(nodes.get('pace-table').innerHTML,/−0\.929581/);
  buttons[1].click();
  assert.equal(buttons[0].attributes['aria-pressed'],'false');
  assert.equal(buttons[1].attributes['aria-pressed'],'true');
  assert.equal((nodes.get('pace-chart').innerHTML.match(/class="bar-row(?: [^"]*)?"/g)||[]).length,22);
  assert.match(nodes.get('pace-table').innerHTML,/−0\.2115/);
  assert.match(nodes.get('pace-axis').textContent,/SECONDS/);
  assert.match(nodes.get('pace-method').textContent,/100 paired laps/);
  buttons[0].click();
  assert.match(nodes.get('pace-axis').textContent,/GRID MEDIAN/);
  assert.equal((nodes.get('career-chart').innerHTML.match(/class="career-row"/g)||[]).length,15);
  assert.equal((nodes.get('progress-table').innerHTML.match(/<tr>/g)||[]).length,11);
  for(const [,asset] of nodes.get('figure-gallery').innerHTML.matchAll(/(?:src|href)="([^"]+)"/g))assert.ok(fs.existsSync(path.join(root,asset)),asset);
  assert.equal((nodes.get('figure-gallery').innerHTML.match(/<img /g)||[]).length,15);
  const slider=nodes.get('phase-slider'), readout=nodes.get('phase-readout'), play=nodes.get('phase-play');
  assert.match(readout.innerHTML,/0–10%/);
  slider.value='9'; slider.input();
  assert.match(readout.innerHTML,/90–100%/);
  assert.match(readout.innerHTML,/−0\.742%/);
  assert.match(readout.innerHTML,/9,450/);
  assert.equal(nodes.get('progress-cursor').attributes.transform,'translate(894 0)');
  play.click();
  assert.match(play.textContent,/STOP/);
  tick(); assert.equal(slider.value,1);
  play.click(); assert.equal(tick,null);
  play.click();
  for(let i=0;i<10;i++) tick();
  assert.equal(tick,null);
  assert.equal(slider.value,9);
  assert.match(play.textContent,/REPLAY/);
  const point={dataset:{i:'8'}};
  nodes.get('progress-chart').click({target:{closest:()=>point}});
  assert.match(readout.innerHTML,/80–90%/);
  assert.match(readout.innerHTML,/−0\.827%/);
  // Published figures are traced to the saved notebook, not invented chart points.
  const source = JSON.parse(fs.readFileSync(path.resolve(root,'../../notebooks/03_lap_time_analysis.ipynb'),'utf8'));
  const output = source.cells[20].outputs.map(o=>(o.text||o.data?.['text/plain']||[]).join('')).join('\n');
  const chartTeams = vm.runInContext('teams',context);
  for (const [name,value,count] of chartTeams) {
    const sourceLine = output.split('\n').find(line=>line.trim().startsWith(name.toLowerCase().replaceAll(' ','_')));
    assert.ok(sourceLine, name);
    const parts=sourceLine.trim().split(/\s+/);
    assert.equal(Number(parts[1]),value);
    assert.equal(Number(parts[2]),count);
  }
});
