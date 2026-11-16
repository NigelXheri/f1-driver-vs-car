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
  document.getElementById('pace-chart').innerHTML = data.map(([name,value,n,team])=> {
    const width = Math.abs(value)/limit*48;
    return `<div class="bar-row" title="${name}${team?' · '+team:''}: ${signed(value,4)}${unit}; ${n} ${isTeam?'races':'paired laps'}"><span>${name}</span><div class="bar-track" aria-hidden="true"><div class="bar-fill ${value>0?'positive':''}" style="left:${value<0?50-width:50}%;width:${width}%"></div></div><span class="bar-value">${signed(value)}${unit}</span></div>`;
  }).join('');
  document.getElementById('pace-axis').textContent = `← FASTER · ${isTeam?'RELATIVE TO GRID MEDIAN (%)':'RELATIVE TO TEAMMATE (SECONDS)'} · SLOWER →`;
  document.getElementById('pace-number').innerHTML = isTeam ? '−0.930<span>%</span>' : '−0.564<span>s</span>';
  document.getElementById('pace-callout').textContent = isTeam ? 'McLaren vs the grid reference' : 'Verstappen relative to Pérez';
  document.getElementById('pace-insight').textContent = isTeam ? 'Ferrari follows at −0.759%, Red Bull at −0.682%, and Mercedes at −0.522%. These summarize the driver–car–team package.' : 'Norris’s median advantage is 0.212 s. Russell and Hamilton are near parity (−0.013 s and +0.013 s respectively).';
  document.getElementById('pace-limit').textContent = isTeam ? 'Race eligibility differs by team. These medians are exploratory and do not isolate the car’s effect or establish significant differences.' : 'Tyres, traffic, setup, damage and strategy remain uncontrolled. Same lap number does not guarantee the same clock time. Replacement drivers change the teammate mix.';
  document.getElementById('pace-method').textContent = isTeam ? 'Notebook 03, cells 19–24. Use race-laps with ≥6 drivers; normalize to their median. Take a median per driver-race (≥10 laps), mean of two eligible drivers per constructor-race, then median across ≥8 races. Each race needs ≥5 eligible constructors.' : 'Notebook 03, cells 13–18. Match exactly two drivers by season, round, constructor and lap. Use driver time minus teammate time. Keep absolute gaps ≤5 seconds and driver-season-constructor groups with ≥100 paired laps. Figures come from saved output in cell 16.';
  document.getElementById('pace-table').innerHTML = table(isTeam?['Constructor','Relative pace (%)','Eligible races']:['Driver','Gap (s)','Paired laps','Constructor'],data.map(([name,value,n,team])=>isTeam?[name,signed(value,6),n]:[name,signed(value,4),n,team]),isTeam?'Notebook 03 · cell 20':'Notebook 03 · cell 16');
}
document.querySelectorAll('[data-view]').forEach(button=>button.addEventListener('click',()=>renderPace(button.dataset.view)));
renderPace('teams');
document.getElementById('career-chart').innerHTML = careers.map(([name,age,rank])=>`<div class="career-row"><span>${name}</span><div class="career-track" aria-hidden="true"><div class="career-fill ${rank===1?'winner':''}" style="width:${age/40*100}%"></div></div><span class="bar-value">${age.toFixed(2)}</span></div>`).join('');
const x = i=>75+i*91, y = value=>225-value*100;
const points = progress.map((v,i)=>`${x(i)},${y(v)}`).join(' ');
document.getElementById('progress-chart').innerHTML = `<svg viewBox="0 0 1000 360" role="img" aria-labelledby="progress-title progress-desc"><title id="progress-title">Relative lap pace by race phase</title><desc id="progress-desc">Median relative lap time decreases from plus 1.432 percent at 0–10 percent distance to minus 0.742 percent at 90–100 percent distance. Exact values and counts are in the following expandable table.</desc>${[-1,0,1,2].map(t=>`<line x1="60" x2="940" y1="${y(t)}" y2="${y(t)}" stroke="${t===0?'#899992':'#343c3f'}" stroke-dasharray="${t===0?'5 6':'0'}"/><text x="40" y="${y(t)+4}" fill="#a6afae" font-family="monospace" font-size="13" text-anchor="end">${t}%</text>`).join('')}<polyline points="${points}" fill="none" stroke="#ff4a3d" stroke-width="3"/>${progress.map((v,i)=>`<circle cx="${x(i)}" cy="${y(v)}" r="5" fill="#ff4a3d"><title>${i*10}–${i*10+10}%: ${signed(v)}%; ${progressCounts[i]} driver-race-phase observations</title></circle><text x="${x(i)}" y="350" text-anchor="middle" fill="#a6afae" font-family="monospace" font-size="12">${i*10}–${i*10+10}</text>`).join('')}<text x="90" y="${y(progress[0])-18}" fill="#f0f0e9" font-family="monospace" font-size="16">+1.432%</text><text x="${x(9)-10}" y="${y(progress[9])-18}" fill="#f0f0e9" font-family="monospace" font-size="16" text-anchor="end">−0.742%</text></svg>`;
document.getElementById('progress-table').innerHTML = table(['Race phase','Median relative lap time (%)','Driver-race-phase observations'],progress.map((v,i)=>[`${i*10}–${i*10+10}%`,signed(v,6),progressCounts[i]]),'Notebook 03 · cell 26');
const figures = [
  ['02_driver_career_eda',36,0,'Driver-level mean age at best recorded rank'],
  ['02_driver_career_eda',38,0,'Best-rank career-year heatmap'],
  ['02_driver_career_eda',40,0,'Age and elapsed career year (mathematically related)'],
  ['02_driver_career_eda',43,0,'Peak-age groups for Welch comparison'],
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
