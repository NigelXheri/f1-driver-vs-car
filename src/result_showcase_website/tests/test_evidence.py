#!/usr/bin/env python3
"""Read-only snapshot checks; no project pipelines, API calls or data writes.

Run from any directory: python3 -m unittest discover -s src/result_showcase_website/tests -v
Uses only Python 3.10+ standard library. Expected values describe this snapshot.
"""
import csv
import json
import math
import re
import statistics as st
import unittest
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SITE = ROOT / 'src/result_showcase_website'


def rows(path):
    with (ROOT / path).open(encoding='utf-8-sig', newline='') as stream:
        yield from csv.DictReader(stream)


def rank(values):
    return [1 + sum(w < v for w in values) + (values.count(v) - 1) / 2 for v in values]


class EvidenceTests(unittest.TestCase):
    def test_career_statistics_from_csv(self):
        ids = 'alonso vettel max_verstappen norris raikkonen button hakkinen rosberg hamilton michael_schumacher leclerc massa barrichello ricciardo montoya'.split()
        totals, ages = defaultdict(float), defaultdict(list)
        for row in rows('data/raw/results.csv'):
            if row['season'] == '2026':
                continue
            key = (int(row['season']), row['driver_id'])
            totals[key] += float(row['points'])
            if row['driver_id'] in ids:
                ages[key].append((date.fromisoformat(row['race_date']) - date.fromisoformat(row['driver_date_of_birth'])).days / 365.2425)
        seasons = defaultdict(list)
        for (season, driver), points in totals.items():
            seasons[season].append(points)
        ranks = {key: 1 + sum(p > points for p in seasons[key[0]]) for key, points in totals.items()}
        winner, other, early, later, best_later = [], [], [], [], []
        peaks = 0
        for driver in ids:
            keys = sorted(k for k in ages if k[1] == driver)
            best = min(ranks[k] for k in keys)
            peak_keys = [k for k in keys if ranks[k] == best]
            peaks += len(peak_keys)
            mean_age = round(st.mean(st.mean(ages[k]) for k in peak_keys), 2)
            (winner if best == 1 else other).append(mean_age)
            if driver not in ['michael_schumacher', 'hakkinen', 'barrichello']:
                early.append(st.mean(ranks[k] for k in keys[:3]))
                later.append(st.mean(ranks[k] for k in keys[3:]))
                best_later.append(min(ranks[k] for k in keys[3:]))
        self.assertEqual((len(winner), len(other), peaks), (10, 5, 36))
        self.assertAlmostEqual(st.mean(winner), 28.347, places=3)
        self.assertAlmostEqual(st.mean(other), 27.278, places=3)
        a, b = st.variance(winner)/len(winner), st.variance(other)/len(other)
        t = (st.mean(winner) - st.mean(other)) / math.sqrt(a+b)
        df = (a+b)**2/(a*a/(len(winner)-1)+b*b/(len(other)-1))
        self.assertAlmostEqual(t, .726, places=3)
        self.assertAlmostEqual(df, 10.806, places=3)
        # Integrate the t density using Simpson's rule; independently check saved p.
        n = 10000
        h = abs(t)/n
        norm = math.exp(math.lgamma((df+1)/2)-math.lgamma(df/2))/math.sqrt(df*math.pi)
        density = lambda z: norm*(1+z*z/df)**(-(df+1)/2)
        area = h/3*(density(0)+density(abs(t))+sum((4 if i%2 else 2)*density(i*h) for i in range(1,n)))
        self.assertAlmostEqual(1-2*area, .4832, places=4)
        self.assertAlmostEqual(st.correlation(rank(early),rank(later)), .5804, places=4)
        self.assertAlmostEqual(st.correlation(rank(early),rank(best_later)), .1418, places=4)

    def test_lap_findings_from_csv(self):
        by_race = defaultdict(list)
        teams = {(r['season'],r['round'],r['driver_id']):r['constructor_id'] for r in rows('data/raw/results.csv')}
        pits = {(r['season'],r['round'],r['driver_id'],int(r['lap'])) for r in rows('data/raw/pitstops.csv')}
        seen, circuits, drivers = set(),set(),set()
        for r in rows('data/processed/laps/lap_times_cleaned.csv'):
            key = (r['season'],r['round'],r['driver_id'],int(r['lap']))
            self.assertNotIn(key, seen)
            seen.add(key)
            seconds = 0
            for component in r['lap_time'].split(':'):
                seconds = seconds*60+float(component)
            self.assertAlmostEqual(seconds,float(r['lap_time_seconds']),places=6)
            by_race[key[:2]].append((key,seconds,r['circuit_id'],r['circuit_name']))
            circuits.add(r['circuit_id']); drivers.add(r['driver_id'])
        self.assertEqual((len(seen),len(by_race),len(circuits),len(drivers)),(639293,588,42,149))
        count,events = 0,0
        pairs, race_circuits, team_races, phase_rows = [],defaultdict(list),defaultdict(list),defaultdict(list)
        driver_gaps = defaultdict(list)
        aliases = {'Albert Park Circuit':'albert_park','Algarve International Circuit':'portimao','Autódromo Oscar y Juan Gálvez':'galvez','Autodromo Internazionale Enzo e Dino Ferrari':'imola','Autodromo José Carlos Pace':'interlagos','Circuito Permanente de Jerez':'jerez','Circuit Zandvoort':'zandvoort','Las Vegas Strip Circuit':'vegas','Suzuka International Racing Course':'suzuka','Korea International Circuit':'yeongam'}
        aliases.update({r[3]:r[2] for values in by_race.values() for r in values})
        wiki = {}
        for r in rows('data/processed/wikipedia_circuits_cleaned.csv'):
            name = re.sub(r'\s+', ' ', re.sub(r'\[[^\]]*\]|[*†‡]', '', r['Circuit'])).strip()
            if name in aliases:
                wiki[aliases[name]] = r
        for race, values in by_race.items():
            median = st.median(v[1] for v in values)
            race_laps, driver_max = defaultdict(list),defaultdict(int)
            for v in values:
                race_laps[v[0][3]].append(v[1])
                driver_max[v[0][2]] = max(driver_max[v[0][2]],v[0][3])
            delayed = {lap for lap,ts in race_laps.items() if sum(t>2*median for t in ts)>=max(5,len(ts)*.5)}
            events += len(delayed)
            pace = [v for v in values if v[0][3]>1 and v[0][3] not in delayed and (int(race[0])<2011 or v[0] not in pits) and -.2<=v[1]/median-1<=.2]
            count += len(pace)
            if not pace:
                continue
            race_circuits[pace[0][2]].append(st.median(v[1] for v in pace))
            matched, grid, per_driver = defaultdict(list),defaultdict(list),defaultdict(list)
            for key,t,c,name in pace:
                matched[(teams[key[:3]],key[3])].append((key[2],t))
                grid[key[3]].append(t)
                per_driver[key[2]].append((key[3],t))
            for (team,lap), pair in matched.items():
                if len(pair)==2:
                    gap=pair[0][1]-pair[1][1]
                    pairs.append(abs(gap))
                    if race[0]=='2024' and abs(gap)<=5:
                        driver_gaps[pair[0][0]].append(gap);driver_gaps[pair[1][0]].append(-gap)
            team_values = defaultdict(list)
            for driver, times in per_driver.items():
                relative = [(t/st.median(grid[lap])-1)*100 for lap,t in times if len(grid[lap])>=6]
                if len(relative)>=10:
                    team_values[teams[(*race,driver)]].append(st.median(relative))
                if driver_max[driver]>=.9*max(race_laps):
                    base=st.median(t for _,t in times)
                    phases=defaultdict(list)
                    for lap,t in times:
                        phase=max(0,math.ceil(lap/max(race_laps)*10)-1)
                        phases[phase].append((t/base-1)*100)
                    for phase, vals in phases.items():phase_rows[phase].append(st.median(vals))
            eligible={team:st.mean(ts) for team,ts in team_values.items() if len(ts)==2}
            if len(eligible)>=5 and race[0]=='2024':
                for team,value in eligible.items():team_races[team].append(value)
        self.assertEqual((count,events,len(pairs)),(577990,56,242133))
        self.assertAlmostEqual(st.median(pairs),.611,places=3)
        self.assertEqual(sum(g>5 for g in pairs),8913)
        self.assertAlmostEqual(st.median(driver_gaps['max_verstappen']),-.564,places=3)
        self.assertAlmostEqual(st.median(driver_gaps['norris']),-.2115,places=4)
        self.assertAlmostEqual(st.median(team_races['mclaren']),-.929581,places=6)
        self.assertEqual(len(team_races['red_bull']),21)
        lengths, times, turns, pace_per_km = [],[],[],[]
        types=defaultdict(list)
        for circuit, ts in race_circuits.items():
            w=wiki[circuit];length=float(w['Circuit_length_km']);time=st.median(ts)
            lengths.append(length);times.append(time);turns.append(float(w['Turns']));pace_per_km.append(time/length)
            types[w['Type']].append(time/length)
        self.assertAlmostEqual(st.correlation(lengths,times),.756,places=3)
        self.assertAlmostEqual(st.correlation(turns,pace_per_km),.087,places=3)
        self.assertAlmostEqual(st.median(types['Street circuit']),18.149,places=3)
        self.assertAlmostEqual(st.median(types['Race circuit']),17.945,places=3)
        self.assertAlmostEqual(st.median(phase_rows[0]),1.431974,places=6)
        self.assertAlmostEqual(st.median(phase_rows[9]),-.742481,places=6)

    def test_original_figure_bytes(self):
        manifest=json.loads((SITE/'evidence/figure-manifest.json').read_text(encoding='utf-8-sig'))
        import base64
        for entry in manifest:
            notebook=json.loads((ROOT/'notebooks'/entry['notebook']).read_text(encoding='utf-8'))
            images=[o['data']['image/png'] for o in notebook['cells'][entry['cell']]['outputs'] if 'image/png' in o.get('data',{})]
            index=int(Path(entry['asset']).stem.rsplit('-',1)[1])
            self.assertEqual((SITE/entry['asset']).read_bytes(),base64.b64decode(''.join(images[index])))


if __name__ == '__main__':
    unittest.main()
