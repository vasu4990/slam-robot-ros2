#!/usr/bin/env python3
"""Apply explicit simulation-regression thresholds to benchmark JSON artifacts."""
import argparse,json
from pathlib import Path
import yaml

def readj(p): return json.loads(Path(p).read_text()) if p else None

def evaluate(t, trajectory=None, loop=None, map_metrics=None, resource=None):
    checks = {}
    if trajectory:
        q=t['trajectory']; checks['ate_rmse']=trajectory['ate_rmse_m']<=q['ate_rmse_m_max']; checks['rpe_translation']=trajectory['rpe_translation_rmse_m']<=q['rpe_translation_rmse_m_max']; checks['rpe_yaw']=trajectory['rpe_yaw_rmse_rad']<=q['rpe_yaw_rmse_rad_max']
    if loop:
        q=t['loop_closure']; checks['loop_event_present']=loop.get('loop_events',0)>0
        if loop.get('loop_events',0)>0:
            checks['loop_translation']=loop['mean_relative_translation_error_m']<=q['mean_relative_translation_error_m_max']; checks['loop_yaw']=loop['mean_relative_yaw_error_rad']<=q['mean_relative_yaw_error_rad_max']
    if map_metrics: checks['map_known_ratio']=map_metrics.get('known_ratio',0)>=t['map']['known_ratio_min']
    if resource: checks['resource_peak_rss']=resource.get('peak_rss_mb',float('inf'))<=t['resource']['slam_toolbox_peak_rss_mb_max']
    return all(checks.values()) if checks else False, checks

def main():
    p=argparse.ArgumentParser(); p.add_argument('--thresholds',default='benchmarks/thresholds.yaml'); p.add_argument('--trajectory'); p.add_argument('--loop'); p.add_argument('--map'); p.add_argument('--resource'); p.add_argument('--output'); a=p.parse_args()
    t=yaml.safe_load(Path(a.thresholds).read_text()); passed,checks=evaluate(t,readj(a.trajectory),readj(a.loop),readj(a.map),readj(a.resource)); payload={'passed':passed,'checks':checks,'simulation_reference_only':True}; print(json.dumps(payload,indent=2))
    if a.output: Path(a.output).write_text(json.dumps(payload,indent=2)+'\n')
    raise SystemExit(0 if passed else 1)

if __name__=='__main__': main()
