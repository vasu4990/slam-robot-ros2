#!/usr/bin/env python3
"""Sample CPU and RSS for matching processes and emit machine-readable profiling results."""
import argparse,json,time
from pathlib import Path
try:import psutil
except ImportError as exc:raise SystemExit('Install psutil (requirements-dev.txt)') from exc
def main():
 p=argparse.ArgumentParser();p.add_argument('--match',action='append',required=True);p.add_argument('--duration',type=float,default=30);p.add_argument('--interval',type=float,default=1);p.add_argument('--output',type=Path,default=Path('artifacts/resource-profile.json'));a=p.parse_args();samples=[];end=time.monotonic()+a.duration
 while time.monotonic()<end:
  row={'t_s':round(a.duration-(end-time.monotonic()),3),'processes':[]}
  for proc in psutil.process_iter(['pid','name','cmdline','memory_info']):
   try:
    label=' '.join([proc.info['name'] or '']+(proc.info['cmdline'] or []))
    if any(m.lower() in label.lower() for m in a.match):row['processes'].append({'pid':proc.pid,'name':proc.info['name'],'cpu_percent':proc.cpu_percent(None),'rss_mb':proc.info['memory_info'].rss/1048576})
   except (psutil.NoSuchProcess,psutil.AccessDenied):pass
  samples.append(row);time.sleep(a.interval)
 flat=[x for s in samples for x in s['processes']];summary={'samples':len(samples),'matches':a.match,'peak_rss_mb':max((x['rss_mb'] for x in flat),default=0.0),'peak_cpu_percent':max((x['cpu_percent'] for x in flat),default=0.0),'raw':samples};a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='raw'},indent=2))
if __name__=='__main__':main()
