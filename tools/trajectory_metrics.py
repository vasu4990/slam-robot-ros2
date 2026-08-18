#!/usr/bin/env python3
"""Compute SE(2)-aligned ATE and fixed-delta RPE from benchmark trajectory CSV."""
from __future__ import annotations
import argparse,csv,json,math
from dataclasses import dataclass
from pathlib import Path
@dataclass(frozen=True)
class Pose2:x:float;y:float;yaw:float
def wrap(a):return math.atan2(math.sin(a),math.cos(a))
def compose(a,b):
 c,s=math.cos(a.yaw),math.sin(a.yaw);return Pose2(a.x+c*b.x-s*b.y,a.y+s*b.x+c*b.y,wrap(a.yaw+b.yaw))
def inverse(a):
 c,s=math.cos(a.yaw),math.sin(a.yaw);return Pose2(-c*a.x-s*a.y,s*a.x-c*a.y,wrap(-a.yaw))
def relative(a,b):return compose(inverse(a),b)
def load(path):
 rows=[]
 with Path(path).open(newline='',encoding='utf-8') as f:
  for r in csv.DictReader(f):rows.append((float(r['stamp_s']),Pose2(float(r['gt_x']),float(r['gt_y']),float(r['gt_yaw'])),Pose2(float(r['est_x']),float(r['est_y']),float(r['est_yaw']))))
 if len(rows)<2:raise ValueError('at least two samples required')
 return rows
def align_se2(gt,est):
 gx=sum(p.x for p in gt)/len(gt);gy=sum(p.y for p in gt)/len(gt);ex=sum(p.x for p in est)/len(est);ey=sum(p.y for p in est)/len(est);cross=dot=0.0
 for g,e in zip(gt,est):
  gxc,gyc=g.x-gx,g.y-gy;exc,eyc=e.x-ex,e.y-ey;dot+=exc*gxc+eyc*gyc;cross+=exc*gyc-eyc*gxc
 th=math.atan2(cross,dot);c,s=math.cos(th),math.sin(th);tx=gx-(c*ex-s*ey);ty=gy-(s*ex+c*ey)
 return [Pose2(c*p.x-s*p.y+tx,s*p.x+c*p.y+ty,wrap(p.yaw+th)) for p in est],{'yaw_rad':th,'tx_m':tx,'ty_m':ty}
def rms(v):return math.sqrt(sum(x*x for x in v)/len(v)) if v else 0.0
def evaluate(rows,delta=10):
 gt=[r[1] for r in rows];est=[r[2] for r in rows];aligned,t=align_se2(gt,est);ate=[math.hypot(g.x-e.x,g.y-e.y) for g,e in zip(gt,aligned)];yaw=[abs(wrap(g.yaw-e.yaw)) for g,e in zip(gt,aligned)];rt=[];ry=[]
 for i in range(len(rows)-delta):
  err=relative(relative(gt[i],gt[i+delta]),relative(aligned[i],aligned[i+delta]));rt.append(math.hypot(err.x,err.y));ry.append(abs(err.yaw))
 return {'samples':len(rows),'duration_s':rows[-1][0]-rows[0][0],'alignment_se2':t,'ate_rmse_m':rms(ate),'ate_mean_m':sum(ate)/len(ate),'ate_max_m':max(ate),'yaw_rmse_rad':rms(yaw),'rpe_delta_samples':delta,'rpe_translation_rmse_m':rms(rt),'rpe_translation_max_m':max(rt) if rt else 0.0,'rpe_yaw_rmse_rad':rms(ry),'rpe_yaw_max_rad':max(ry) if ry else 0.0}
def main():
 p=argparse.ArgumentParser();p.add_argument('csv',type=Path);p.add_argument('--delta',type=int,default=10);p.add_argument('--output',type=Path);a=p.parse_args();m=evaluate(load(a.csv),a.delta);text=json.dumps(m,indent=2);print(text)
 if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(text+'\n')
if __name__=='__main__':main()
