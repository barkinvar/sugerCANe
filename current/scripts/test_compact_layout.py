"""Regression checks for compact critical routing and local boost ground."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import pcbnew as p

ROOT = Path(__file__).resolve().parents[1]
BOARD = ROOT / 'hardware/FRC_Sensor_CAN.kicad_pcb'


def check(board, output):
    return subprocess.run([sys.executable, str(ROOT / 'scripts/check_compact_layout.py'),
                           '--board', str(board), '--output', str(output)],
                          text=True, capture_output=True)


with tempfile.TemporaryDirectory(prefix='candi-compact-regression-') as directory:
    trial = Path(directory) / BOARD.name
    output = Path(directory) / 'verification.json'
    shutil.copyfile(BOARD.with_suffix('.kicad_pro'), trial.with_suffix('.kicad_pro'))
    shutil.copyfile(BOARD, trial)
    result = check(trial, output)
    assert result.returncode == 0, result.stderr
    report = json.loads(output.read_text())
    assert report['preserved_critical_tracks_and_vias'] == 51
    assert report['verified_critical_tracks_and_vias'] == 55
    for case in ('corner_contact', 'narrow_diode_leg', 'missing_pad_entry', 'unlisted_clock_change',
                 'missing_local_ground_via', 'ground_via_wrong_span'):
        board = p.LoadBoard(str(BOARD))
        tracks = {t.m_Uuid.AsString(): t for t in board.GetTracks()}
        if case == 'corner_contact':
            track = tracks['c58c6da1-66e1-4fb1-b3ff-9aa2b8d80d4c']
            track.SetStart(p.VECTOR2I(p.FromMM(29.5), p.FromMM(22.625)))
            track.SetEnd(p.VECTOR2I(p.FromMM(32.175), p.FromMM(19.95)))
            track.SetWidth(p.FromMM(.5))
        elif case == 'narrow_diode_leg':
            tracks['61517e2f-1387-4752-a3e7-2a117a3ea970'].SetWidth(p.FromMM(.3))
        elif case == 'missing_pad_entry':
            removed = tracks['5e4f71f9-120b-4208-aa9b-4f51ac11a37b']
            board.RemoveNative(removed)
        elif case == 'unlisted_clock_change':
            track = next(t for t in board.GetTracks() if t.GetNetname() == 'HSE_IN')
            track.SetWidth(track.GetWidth() + p.FromMM(.01))
        elif case == 'missing_local_ground_via':
            ground = next(d for f in board.GetFootprints() if f.GetReference() == 'U8'
                          for d in f.Pads() if d.GetNumber() == '4')
            removed_vias = []
            for via in list(board.GetTracks()):
                if (isinstance(via, p.PCB_VIA) and via.GetNetname() == 'GND' and
                        (via.GetPosition() - ground.GetPosition()).EuclideanNorm() <= p.FromMM(3.2)):
                    board.RemoveNative(via)
                    removed_vias.append(via)
        else:
            via = tracks['ebde20cb-ab86-430d-91c4-3e24b3b6bb4e']
            via.SetViaType(p.VIATYPE_BLIND)
            via.SetLayerPair(p.F_Cu, p.In1_Cu)
        p.SaveBoard(str(trial), board)
        result = check(trial, output)
        assert result.returncode != 0 and ('Critical repair differs' in result.stderr or
               'Clock/converter copper differs' in result.stderr or
               'Boost ground return lacks' in result.stderr), (case, result.stdout, result.stderr)
        print('PASS rejects', case)
print('PASS compact repair: valid board accepted; six unsafe/unreviewed mutations rejected')
