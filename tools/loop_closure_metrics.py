#!/usr/bin/env python3
"""Detect ground-truth loop revisits and score long-horizon relative-pose error."""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
try:
 from tools.trajectory_metrics import load,relative,wrap
except ModuleNotFoundError:
 from trajectory_metrics import load,relative,wrap
def cumulative(gt):
 out=[0.0]
 for a,b in zip(gt,gt[1:]):out.append(out[-1]+math.hypot(b.x-a.x,b.y-a.y))
 return out
def detect(rows,radius=.30,min_path=3.0,min_gap_samples=50):
 gt=[r[1] for r in rows];est=[r[2] for r in rows];dist=cumulative(gt);events=[];last_j=-min_gap_samples
 for j in range(min_gap_samples,len(rows)):
  best=None
  for i in range(0,j-min_gap_samples):
   if dist[j]-dist[i]<min_path:continue
   d=math.hypot(gt[j].x-gt[i].x,gt[j].y-gt[i].y)
   if d<=radius and (best is None or d<best[0]):best=(d,i)
  if best and j-last_j>=min_gap_samples:
   _,i=best;err=relative(relative(gt[i],gt[j]),relative(est[i],est[j]));events.append({'start_index':i,'end_index':j,'path_length_m':dist[j]-dist[i],'gt_revisit_distance_m':best[0],'relative_translation_error_m':math.hypot(err.x,err.y),'relative_yaw_error_rad':abs(wrap(err.yaw))});last_j=j
 return events
def evaluate(rows,**kw):
 e=detect(rows,**kw)
 if not e:return {'loop_events':0,'mean_relative_translation_error_m':None,'mean_relative_yaw_error_rad':None,'events':[]}
 return {'loop_events':len(e),'mean_relative_translation_error_m':sum(x['relative_translation_error_m'] for x in e)/len(e),'max_relative_translation_error_m':max(x['relative_translation_error_m'] for x in e),'mean_relative_yaw_error_rad':sum(x['relative_yaw_error_rad'] for x in e)/len(e),'max_relative_yaw_error_rad':max(x['relative_yaw_error_rad'] for x in e),'events':e}
def main():
 p=argparse.ArgumentParser();p.add_argument('csv',type=Path);p.add_argument('--radius',type=float,default=.30);p.add_argument('--min-path',type=float,default=3.0);p.add_argument('--min-gap-samples',type=int,default=50);p.add_argument('--output',type=Path);a=p.parse_args();m=evaluate(load(a.csv),radius=a.radius,min_path=a.min_path,min_gap_samples=a.min_gap_samples);text=json.dumps(m,indent=2);print(text)
 if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(text+'\n')
if __name__=='__main__':main()
