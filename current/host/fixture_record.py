"""Record post-programming CAN identity and operator/fixture measurements per UID.
No measurement is synthesized. This acceptance record is not design qualification.
"""
import argparse
from datetime import datetime, timezone
import hashlib,json
from pathlib import Path
from can_service import Client,TcpBridge,SocketCan

LIMITS={'internal_5v':(4.8,5.3),'logic_3v3':(3.15,3.45),'regulated_12v':(11.4,12.6),'sensor_5v':(4.65,5.45)}
CHECKS=('smt_inspected','terminal_polarity','input1_low_high','input2_low_high',
        'input3_low_high','telemetry_after_service','power_cycle_config_retained',
        'efuse_exposed_pad_inspected','rails_off_in_bootloader','rails_off_during_reset',
        'rail_adc_matches_meter','sensor_rail_short_and_can_reset')
def assess(info, measurements):
    errors=[]
    if info['mode']!='application' or not info['configured'] or not info['boot_protected']:
        errors.append('Application, configuration and boot protection must all be verified')
    for name,(lo,hi) in LIMITS.items():
        value=measurements.get(name)
        if not isinstance(value,(int,float)) or isinstance(value,bool) or not lo<=value<=hi:
            errors.append(f'{name}: measured value must be {lo}..{hi} V')
    for name in CHECKS:
        if measurements.get(name) is not True:errors.append(name+': explicit passed measurement/check required')
    return errors

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--uid',required=True)
    p.add_argument('--bridge');p.add_argument('--channel',default='can0')
    p.add_argument('--measurements',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--operator',required=True);p.add_argument('--lot',required=True)
    args=p.parse_args();measured=json.loads(args.measurements.read_text());c=Client(TcpBridge(args.bridge) if args.bridge else SocketCan('socketcan',args.channel))
    try:c.open();c.select(args.uid);info=c.info()
    finally:c.close()
    errors=assess(info,measured)
    report=dict(timestamp=datetime.now(timezone.utc).isoformat(),operator=args.operator,lot=args.lot,device=info,measurements=measured,measurement_file_sha256=hashlib.sha256(args.measurements.read_bytes()).hexdigest(),result='FAIL' if errors else 'PASS unit acceptance',errors=errors,scope='Operator/fixture supplied measurements plus live CAN identity. Not design qualification.')
    # Never overwrite another unit's evidence silently.
    with args.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    if errors:p.exit(1,'Unit acceptance failed; see report\n')
    print(args.output)
if __name__=='__main__':main()
