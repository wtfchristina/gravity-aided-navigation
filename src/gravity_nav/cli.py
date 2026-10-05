from __future__ import annotations
import argparse, json
from pathlib import Path
from .config import load_config
from .assured_pnt import run_assured_pnt
from .monte_carlo import run_campaign, summarize_campaign
from .trade_study import sensor_trade_study
from .reporting import write_report
from .requirements_config import load_mission_requirement
from .requirements import solve_sensor_requirements, evaluate_configuration
from .integrity import IntegrityConfig, single_run_integrity, campaign_integrity
from .mission import mission_envelope_study


def main(argv=None):
    p=argparse.ArgumentParser(prog='qpnt',description='Assured PNT mission-analysis and trade-study CLI')
    sp=p.add_subparsers(dest='cmd',required=True)
    r=sp.add_parser('run'); r.add_argument('config'); r.add_argument('--out',default='results/assured_pnt')
    mc=sp.add_parser('monte-carlo'); mc.add_argument('config'); mc.add_argument('--runs',type=int,default=25); mc.add_argument('--out',default='results/monte_carlo.csv')
    ts=sp.add_parser('trade-study'); ts.add_argument('config'); ts.add_argument('--out',default='results/trade_study.csv')
    req=sp.add_parser('requirements'); req.add_argument('config'); req.add_argument('--runs',type=int,default=25); req.add_argument('--out',default='results/requirements.csv')
    integ=sp.add_parser('integrity'); integ.add_argument('config'); integ.add_argument('--runs',type=int,default=25); integ.add_argument('--alert-limit-m',type=float,default=300.0); integ.add_argument('--out',default='results/integrity.csv')
    env=sp.add_parser('mission-envelope'); env.add_argument('config'); env.add_argument('--runs',type=int,default=10); env.add_argument('--out',default='results/mission_envelope.csv')
    args=p.parse_args(argv)

    if args.cmd in {'requirements','mission-envelope'}:
        cfg, requirement=load_mission_requirement(args.config)
    else:
        cfg=load_config(args.config)

    if args.cmd=='run':
        out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
        df,m,_,_=run_assured_pnt(cfg)
        df.to_csv(out.with_suffix('.csv'),index=False)
        out.with_suffix('.json').write_text(json.dumps(m,indent=2),encoding='utf-8')
        write_report(out.with_suffix('.md'),'Assured PNT Scenario Report',m,['Synthetic maps and planar kinematics.','Not operational performance.'])
        print(json.dumps({k:v for k,v in m.items() if k!='config'},indent=2))
    elif args.cmd=='monte-carlo':
        df=run_campaign(cfg,args.runs); Path(args.out).parent.mkdir(parents=True,exist_ok=True); df.to_csv(args.out,index=False)
        summary=summarize_campaign(df); summary.to_csv(Path(args.out).with_name(Path(args.out).stem+'_summary.csv'),index=False); print(summary.to_string(index=False))
    elif args.cmd=='trade-study':
        df=sensor_trade_study(cfg); Path(args.out).parent.mkdir(parents=True,exist_ok=True); df.to_csv(args.out,index=False); print(df.head(10).to_string(index=False))
    elif args.cmd=='requirements':
        df=solve_sensor_requirements(cfg,requirement,runs=args.runs); Path(args.out).parent.mkdir(parents=True,exist_ok=True); df.to_csv(args.out,index=False)
        baseline=evaluate_configuration(cfg,requirement,args.runs)
        Path(args.out).with_suffix('.json').write_text(json.dumps(baseline,indent=2),encoding='utf-8')
        print(df.head(15).to_string(index=False))
    elif args.cmd=='integrity':
        ic=IntegrityConfig(alert_limit_m=args.alert_limit_m)
        campaign=campaign_integrity(cfg,ic,args.runs); Path(args.out).parent.mkdir(parents=True,exist_ok=True); campaign.to_csv(args.out,index=False)
        df,_,_,_=run_assured_pnt(cfg); trace,metrics=single_run_integrity(df,ic)
        trace.to_csv(Path(args.out).with_name(Path(args.out).stem+'_trace.csv'),index=False)
        Path(args.out).with_suffix('.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
        print(campaign.describe().to_string()); print(json.dumps(metrics,indent=2))
    elif args.cmd=='mission-envelope':
        df=mission_envelope_study(cfg,requirement,runs=args.runs); Path(args.out).parent.mkdir(parents=True,exist_ok=True); df.to_csv(args.out,index=False); print(df.to_string(index=False))

if __name__=='__main__': main()
