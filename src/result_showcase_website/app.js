#!/usr/bin/env node
/* Fixed, traceable notebook snapshot. No network calls or runtime dependencies. */
'use strict';
const teams = [
  ['McLaren', -.929581, 24], ['Ferrari', -.758811, 24], ['Red Bull', -.682148, 21],
  ['Mercedes', -.521756, 23], ['Aston Martin', .202931, 20], ['Haas', .273125, 23],
  ['Alpine', .372063, 20], ['Williams', .405951, 19], ['RB', .420290, 21], ['Sauber', .778982, 22]
];
const drivers = [
  ['Verstappen', -.564, 1016, 'Red Bull'], ['Albon', -.2125, 794, 'Williams'],
  ['Norris', -.2115, 1236, 'McLaren'], ['Hülkenberg', -.202, 1090, 'Haas'],
  ['Alonso', -.163, 1020, 'Aston Martin'], ['Gasly', -.1405, 956, 'Alpine'],
  ['Bottas', -.064, 1066, 'Sauber'], ['Leclerc', -.047, 1181, 'Ferrari'],
  ['Tsunoda', -.035, 1013, 'RB'], ['Lawson', -.025, 235, 'RB'],
  ['Colapinto', -.021, 189, 'Williams'], ['Russell', -.013, 1134, 'Mercedes'],
  ['Hamilton', .013, 1134, 'Mercedes'], ['Sainz', .031, 1135, 'Ferrari'],
  ['Zhou', .064, 1066, 'Sauber'], ['Ricciardo', .066, 778, 'RB'],
  ['Ocon', .110, 906, 'Alpine'], ['Stroll', .163, 1020, 'Aston Martin'],
  ['Magnussen', .203, 1022, 'Haas'], ['Piastri', .2115, 1236, 'McLaren'],
  ['Sargeant', .283, 605, 'Williams'], ['Pérez', .564, 1016, 'Red Bull']
];
const careers = [
  ['Alonso',24.42,1],['Vettel',24.56,1],['Verstappen',25.33,1],['Norris',25.70,1],
  ['Räikkönen',27.73,1],['Button',29.48,1],['Häkkinen',30.27,1],['Rosberg',31.08,1],
  ['Hamilton',31.42,1],['Schumacher',33.48,1],['Leclerc',24.76,2],['Massa',27.22,2],
  ['Barrichello',31.09,2],['Ricciardo',26.06,3],['Montoya',27.26,3]
];
const progress = [1.431974,.940114,.539176,.266058,.049163,-.167902,-.455665,-.650123,-.826681,-.742481];
const progressCounts = [8943,9355,9435,9432,9446,9477,9422,9451,9454,9450];
const fx = (name, ...args) => { try { if (typeof window !== 'undefined' && window.SOS && window.SOS[name]) window.SOS[name](...args); } catch (e) { /* presentation layer is optional */ } };
const signed = (value, digits=3) => `${value < 0 ? '−' : '+'}${Math.abs(value).toFixed(digits)}`;
function table(headers, rows, caption) {
  return `<table><caption>${caption}</caption><thead><tr>${headers.map(v=>`<th scope="col">${v}</th>`).join('')}</tr></thead><tbody>${rows.map(row=>`<tr>${row.map((v,i)=>i===0?`<th scope="row">${v}</th>`:`<td>${v}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
}
function renderPace(view) {
  const isTeam = view === 'teams', data = isTeam ? teams : drivers, unit = isTeam ? '%' : ' s';
  document.querySelectorAll('[data-view]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.view === view)));
  document.getElementById('pace-title').textContent = isTeam ? 'McLaren leads this pace metric.' : 'The teammate is the reference.';
  document.getElementById('pace-description').textContent = isTeam ? 'Median relative pace across eligible constructor-races. Each team has 19–24 observations.' : 'Median signed gap to each driver’s teammate(s). This is not a cross-team skill ranking.';
  const limit = isTeam ? 1 : .6;
  document.getElementById('pace-chart').innerHTML = data.map(([name,value,n,team],i)=> {
    const width = Math.abs(value)/limit*48;
    const tip = `${name}${team?' · '+team:''}: ${signed(value,4)}${unit}; ${n} ${isTeam?'races':'paired laps'}`;
    const pos = isTeam ? `<span class="pos" aria-hidden="true">${String(i+1).padStart(2,'0')}</span>` : '';
    const sub = team ? `<small>${team}</small>` : '';
    return `<div class="bar-row ${isTeam?'is-team':'is-driver'}" style="--i:${i}" title="${tip}" data-tip="${tip}" tabindex="0">${pos}<span>${name}${sub}</span><div class="bar-track" aria-hidden="true"><div class="bar-fill ${value>0?'positive':'neg'}" style="left:${value<0?50-width:50}%;width:${width}%"></div></div><span class="bar-value">${signed(value)}${unit}</span></div>`;
  }).join('');
  document.getElementById('pace-axis').textContent = `← FASTER · ${isTeam?'RELATIVE TO GRID MEDIAN (%)':'RELATIVE TO TEAMMATE (SECONDS)'} · SLOWER →`;
  document.getElementById('pace-number').innerHTML = isTeam ? '−0.930<span>%</span>' : '−0.564<span>s</span>';
  fx('countUp', document.getElementById('pace-number'));
  document.getElementById('pace-callout').textContent = isTeam ? 'McLaren vs the grid reference' : 'Verstappen relative to Pérez';
  document.getElementById('pace-insight').textContent = isTeam ? 'Ferrari follows at −0.759%, Red Bull at −0.682%, and Mercedes at −0.522%. These summarize the driver–car–team package.' : 'Norris’s median advantage is 0.212 s. Russell and Hamilton are near parity (−0.013 s and +0.013 s respectively).';
  document.getElementById('pace-limit').textContent = isTeam ? 'Race eligibility differs by team. These medians are exploratory and do not isolate the car’s effect or establish significant differences.' : 'Tyres, traffic, setup, damage and strategy remain uncontrolled. Same lap number does not guarantee the same clock time. Replacement drivers change the teammate mix.';
  document.getElementById('pace-method').textContent = isTeam ? 'Notebook 03, cells 19–24. Use race-laps with ≥6 drivers; normalize to their median. Take a median per driver-race (≥10 laps), mean of two eligible drivers per constructor-race, then median across ≥8 races. Each race needs ≥5 eligible constructors.' : 'Notebook 03, cells 13–18. Match exactly two drivers by season, round, constructor and lap. Use driver time minus teammate time. Keep absolute gaps ≤5 seconds and driver-season-constructor groups with ≥100 paired laps. Figures come from saved output in cell 16.';
  document.getElementById('pace-table').innerHTML = table(isTeam?['Constructor','Relative pace (%)','Eligible races']:['Driver','Gap (s)','Paired laps','Constructor'],data.map(([name,value,n,team])=>isTeam?[name,signed(value,6),n]:[name,signed(value,4),n,team]),isTeam?'Notebook 03 · cell 20':'Notebook 03 · cell 16');
  fx('replay', document.getElementById('pace-chart'));
}
document.querySelectorAll('[data-view]').forEach(button=>button.addEventListener('click',()=>renderPace(button.dataset.view)));
renderPace('teams');
const ageMin = 20, ageMax = 36, rank1Mean = 28.347;
const agePct = value => ((value-ageMin)/(ageMax-ageMin)*100).toFixed(2);
document.getElementById('career-chart').innerHTML = `<div class="career-rows" style="--m:${(rank1Mean-ageMin)/(ageMax-ageMin)}"><span class="career-mean" aria-hidden="true"><em>RANK-1 MEAN ${rank1Mean}</em></span>${careers.map(([name,age,rank],i)=>{
  const tip = `${name} · mean age across best-rank seasons: ${age.toFixed(2)} years · best recorded rank ${rank}`;
  return `<div class="career-row" style="--i:${i};--x:${agePct(age)}%" title="${tip}" data-tip="${tip}" tabindex="0"><span>${name}</span><div class="career-track" aria-hidden="true"><div class="career-fill ${rank===1?'winner':''}"></div><i class="career-dot ${rank===1?'winner':''}"></i></div><span class="bar-value">${age.toFixed(2)}</span></div>`;
}).join('')}<div class="career-axis" aria-hidden="true">${[20,24,28,32,36].map(t=>`<span style="left:${agePct(t)}%">${t}</span>`).join('')}</div></div>`;
const x = i=>75+i*91, y = value=>225-value*100;
const points = progress.map((v,i)=>`${x(i)},${y(v)}`).join(' ');
const lineLength = Math.ceil(progress.slice(1).reduce((sum,v,i)=>sum+Math.hypot(x(i+1)-x(i), y(v)-y(progress[i])), 0));
const baseY = y(0);
const areaPath = `M${x(0)},${baseY} ${progress.map((v,i)=>`L${x(i)},${y(v)}`).join(' ')} L${x(9)},${baseY} Z`;
const minIndex = progress.indexOf(Math.min(...progress));
const phaseLabel = i => `${i*10}–${i*10+10}%`;
const phaseTip = i => `${phaseLabel(i)}: ${signed(progress[i])}%; ${progressCounts[i]} driver-race-phase observations`;
document.getElementById('progress-chart').innerHTML = `<svg viewBox="0 0 1000 360" role="img" aria-labelledby="progress-title progress-desc"><title id="progress-title">Relative lap pace by race phase</title><desc id="progress-desc">Median relative lap time decreases from plus 1.432 percent at 0–10 percent distance to minus 0.742 percent at 90–100 percent distance. Exact values and counts are in the following expandable table.</desc><defs><clipPath id="clip-slow"><rect x="0" y="0" width="1000" height="${baseY}"/></clipPath><clipPath id="clip-fast"><rect x="0" y="${baseY}" width="1000" height="${360-baseY}"/></clipPath></defs>${[-1,0,1,2].map(t=>`<line x1="60" x2="940" y1="${y(t)}" y2="${y(t)}" stroke="${t===0?'#899992':'#343c3f'}" stroke-dasharray="${t===0?'5 6':'0'}"/><text x="40" y="${y(t)+4}" fill="#a6afae" font-family="monospace" font-size="13" text-anchor="end">${t}%</text>`).join('')}<path class="area area-slow" clip-path="url(#clip-slow)" d="${areaPath}"/><path class="area area-fast" clip-path="url(#clip-fast)" d="${areaPath}"/><text class="axis-note" x="948" y="${y(2)+4}">SLOWER</text><text class="axis-note" x="948" y="${y(-1)+4}">FASTER</text><polyline class="line-draw" style="--len:${lineLength}" points="${points}" fill="none" stroke="#ff4a3d" stroke-width="3"/>${progress.map((v,i)=>`<circle class="pt" data-i="${i}" tabindex="0" data-tip="${phaseTip(i)}" cx="${x(i)}" cy="${y(v)}" r="5" fill="#ff4a3d"><title>${phaseTip(i)}</title></circle><text x="${x(i)}" y="350" text-anchor="middle" fill="#a6afae" font-family="monospace" font-size="12">${phaseLabel(i).replace('%','')}</text>`).join('')}<text class="note" x="90" y="${y(progress[0])-18}" fill="#f0f0e9" font-family="monospace" font-size="16">+1.432%</text><text class="note" x="${x(9)-10}" y="${y(progress[9])-18}" fill="#f0f0e9" font-family="monospace" font-size="16" text-anchor="end">−0.742%</text><line class="leader" x1="${x(minIndex)}" x2="${x(minIndex)}" y1="${y(1.5)+10}" y2="${y(progress[minIndex])-12}" stroke="#ffffff" stroke-opacity=".3" stroke-dasharray="2 4"/><text class="note" x="${x(minIndex)}" y="${y(1.5)}" text-anchor="middle">FASTEST PHASE ${signed(progress[minIndex])}% · ${phaseLabel(minIndex)}</text><g id="progress-cursor" aria-hidden="true" transform="translate(${x(0)} 0)"><line x1="0" x2="0" y1="${y(2)}" y2="${y(-1)}" stroke="#ffffff" stroke-opacity=".35" stroke-dasharray="3 5"/><circle cx="0" cy="${y(progress[0])}" r="10" fill="none" stroke="#ffffff" stroke-width="2"/></g></svg>`;
document.getElementById('progress-table').innerHTML = table(['Race phase','Median relative lap time (%)','Driver-race-phase observations'],progress.map((v,i)=>[`${i*10}–${i*10+10}%`,signed(v,6),progressCounts[i]]),'Notebook 03 · cell 26');
(function buildRaceScrub() {
  const host = document.getElementById('race-scrub');
  if (!host) return;
  try {
    host.innerHTML = `<div class="scrub-rail"><span class="start-lights" aria-hidden="true">${[0,1,2,3,4].map(k=>`<i style="--k:${k}"></i>`).join('')}</span><label for="phase-slider">Race distance completed · drag or replay</label><span class="flag" aria-hidden="true"></span></div><input id="phase-slider" type="range" min="0" max="${progress.length-1}" step="1" value="0" aria-describedby="phase-readout"><div class="scrub-meta"><output id="phase-readout" aria-live="polite"></output><button type="button" class="play" id="phase-play">▶ REPLAY THE RACE</button></div>`;
    const slider = document.getElementById('phase-slider'), readout = document.getElementById('phase-readout');
    const cursor = document.getElementById('progress-cursor'), ring = cursor && cursor.querySelector('circle');
    const play = document.getElementById('phase-play');
    let timer = null;
    const show = i => {
      const v = progress[i];
      readout.innerHTML = `<b>${phaseLabel(i)}</b> of race distance · median relative lap time <b>${signed(v)}%</b> · ${progressCounts[i].toLocaleString('en-US')} driver-race-phase observations`;
      slider.style.setProperty('--fill', `${i/(progress.length-1)*100}%`);
      if (cursor) { cursor.setAttribute('transform', `translate(${x(i)} 0)`); ring.setAttribute('cy', y(v)); }
    };
    const stop = () => { clearInterval(timer); timer = null; play.textContent = '▶ REPLAY THE RACE'; };
    slider.addEventListener('input', () => { stop(); show(Number(slider.value)); });
    play.addEventListener('click', () => {
      if (timer) { stop(); return; }
      let i = 0; slider.value = 0; show(0); play.textContent = '■ STOP';
      timer = setInterval(() => { i += 1; if (i >= progress.length) { stop(); return; } slider.value = i; show(i); }, 560);
    });
    document.getElementById('progress-chart').addEventListener('click', event => {
      const pt = event.target.closest && event.target.closest('.pt');
      if (pt) { stop(); slider.value = pt.dataset.i; show(Number(pt.dataset.i)); }
    });
    show(0);
  } catch (error) { /* chart and exact-value table remain available */ }
})();
const figures = [
  ['02_driver_career_eda',36,0,'Driver-level mean age at best recorded rank'],
  ['02_driver_career_eda',38,0,'Mean career year across best-rank seasons'],
  ['02_driver_career_eda',40,0,'Age and elapsed career year (mathematically related)'],
  ['02_driver_career_eda',43,0,'Championship rank across career years'],
  ['02_driver_career_eda',58,0,'Early vs later average rank'],
  ['02_driver_career_eda',60,0,'Early vs later podium rates per entry'],
  ['02_driver_career_eda',62,0,'Early vs later win rates per entry'],
  ['03_lap_time_analysis',10,0,'Circuit length vs median lap time'],
  ['03_lap_time_analysis',10,1,'Turn count vs seconds per km'],
  ['03_lap_time_analysis',10,2,'Circuit-type pace distributions'],
  ['03_lap_time_analysis',16,0,'2024 signed teammate gaps'],
  ['03_lap_time_analysis',17,0,'Absolute gap histogram after the 5-second cutoff'],
  ['03_lap_time_analysis',21,0,'2024 constructor relative pace'],
  ['03_lap_time_analysis',23,0,'Constructor consistency across eligible races'],
  ['03_lap_time_analysis',27,0,'Race progression']
];
document.getElementById('figure-gallery').innerHTML = figures.map(([notebook,cell,index,label])=>`<a href="assets/${notebook}-cell-${cell}-${index}.png"><img loading="lazy" src="assets/${notebook}-cell-${cell}-${index}.png" alt="Original saved notebook chart: ${label}"><p>${label}<br>${notebook} · cell ${cell}</p></a>`).join('');
