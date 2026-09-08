"""Exercise installed tools using fixtures, never the production PCB design."""
from pathlib import Path
import json
import os
import re
import subprocess
import sys

PROJECT = Path(__file__).resolve().parents[1]
ROOT = Path(os.environ.get("CANDI_TOOLS_ROOT", Path.home() / ".local/share/candi-tools"))
WORK = PROJECT / "reports/toolchain/work"
WORK.mkdir(parents=True, exist_ok=True)
os.environ["PATH"] = f"{PROJECT / '.venv/bin'}:{ROOT / 'bin'}:" + os.environ["PATH"]
results = []


def run(label, args):
    p = subprocess.run([str(a) for a in args], cwd=WORK, text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120)
    (WORK / f"{label}.log").write_text(p.stdout)
    results.append({"check": label, "returncode": p.returncode})
    if p.returncode:
        print(p.stdout)
        raise RuntimeError(f"{label} failed")
    print(f"PASS {label}")
    return p.stdout


versions = {
    "kicad": run("kicad_version", ["kicad-cli", "version"]).strip(),
    "ibom": run("ibom_version", ["ibom", "--version"]).strip(),
    "gcc": run("gcc_version", ["arm-none-eabi-gcc", "--version"]).splitlines()[0],
    "ngspice": run("ngspice_version", ["ngspice", "--version"]).splitlines()[1],
    "openocd": run("openocd_version", ["openocd", "--version"]).splitlines()[0],
    "cmake": run("cmake_version", ["cmake", "--version"]).splitlines()[0],
    "ninja": run("ninja_version", ["ninja", "--version"]).strip(),
}

(WORK / "divider.cir").write_text("""Toolchain fixture: 12 V divided by two
V1 vin 0 DC 12
R1 vin vout 10k
R2 vout 0 10k
.control
op
print v(vout)
quit
.endc
.end
""")
out = run("ngspice_divider", ["ngspice", "-b", "divider.cir"])
assert abs(float(re.search(r"v\(vout\)\s*=\s*(\S+)", out).group(1)) - 6) < 1e-6

for ext, compiler, code in [
    ("c", "arm-none-eabi-gcc", "#include <stdint.h>\n#include <string.h>\nint main(void){volatile uint32_t x=3;return (int)x;}\n"),
    ("cpp", "arm-none-eabi-g++", "#include <array>\nstd::array<int,2> a={1,2};\nint main(){return a[0];}\n"),
]:
    (WORK / f"firmware.{ext}").write_text(code)
    run(f"arm_{ext}_link", [compiler, "-mcpu=cortex-m0plus", "-mthumb", "--specs=nosys.specs",
                             f"firmware.{ext}", "-o", f"firmware-{ext}.elf"])

# A deliberately simple fixture checks the installed footprint library and PCB API.
(WORK / "make_fixture.py").write_text("""import os
from pathlib import Path
import pcbnew as p
root=Path(os.environ['CANDI_TOOLS_ROOT'])/'kicad/AppDir/share/kicad'
b=p.BOARD()
fp=p.FootprintLoad(str(root/'footprints/Resistor_SMD.pretty'),'R_0805_2012Metric')
assert fp is not None
fp.SetReference('R1'); fp.SetValue('10k'); fp.SetPosition(p.VECTOR2I(p.FromMM(10),p.FromMM(10))); b.Add(fp)
for a,z in [((0,0),(20,0)),((20,0),(20,20)),((20,20),(0,20)),((0,20),(0,0))]:
    s=p.PCB_SHAPE(); s.SetShape(p.SHAPE_T_SEGMENT); s.SetLayer(p.Edge_Cuts)
    s.SetStart(p.VECTOR2I(p.FromMM(a[0]),p.FromMM(a[1])))
    s.SetEnd(p.VECTOR2I(p.FromMM(z[0]),p.FromMM(z[1])))
    s.SetWidth(p.FromMM(0.05)); b.Add(s)
p.SaveBoard('fixture.kicad_pcb',b)
assert len(p.LoadBoard('fixture.kicad_pcb').GetFootprints()) == 1
""")
os.environ["CANDI_TOOLS_ROOT"] = str(ROOT)
run("pcb_api_roundtrip", ["kicad-python", "make_fixture.py"])
run("pcb_drc_engine", ["kicad-cli", "pcb", "drc", "--format", "json", "-o", "drc.json", "fixture.kicad_pcb"])
run("gerber_export", ["kicad-cli", "pcb", "export", "gerbers", "-o", "gerbers/", "fixture.kicad_pcb"])
run("drill_export", ["kicad-cli", "pcb", "export", "drill", "-o", "gerbers/", "fixture.kicad_pcb"])
run("ibom_export", ["ibom", "--no-browser", "--dest-dir", str(WORK / "ibom"), "fixture.kicad_pcb"])
assert list((WORK / "ibom").glob("*.html"))

# Exercise schematic parsing/ERC/PDF with a bundled upstream demo.
demo = ROOT / "kicad/AppDir/share/kicad/demos/interf_u/interf_u.kicad_sch"
run("schematic_erc_engine", ["kicad-cli", "sch", "erc", "--format", "json", "-o", "erc.json", demo])
run("schematic_pdf_export", ["kicad-cli", "sch", "export", "pdf", "-o", "schematic.pdf", demo])
run("pdf_render", ["pdftoppm", "-f", "1", "-singlefile", "-scale-to", "1000", "-png", "schematic.pdf", "schematic"])
assert (WORK / "schematic.png").stat().st_size > 1000

import can
import cantools
from pypdf import PdfReader
import numpy as np
import scipy
import matplotlib
import pandas
assert len(PdfReader(WORK / "schematic.pdf").pages) > 0
with can.Bus(interface="virtual", channel="candi-toolchain", receive_own_messages=True) as bus:
    bus.send(can.Message(arbitration_id=0x1ABCDE, is_extended_id=True, data=[1, 2, 3]))
    frame = bus.recv(timeout=1)
    assert frame is not None and bytes(frame.data) == b"\x01\x02\x03"
results.append({"check": "python_imports_pdf_and_virtual_can", "returncode": 0})
report = {"scope": "Tool installation checks only. ERC/DRC engine execution does not certify fixtures or a product design. No physical hardware tested.",
          "versions": versions, "checks": results}
(PROJECT / "reports/toolchain/verification.json").write_text(json.dumps(report, indent=2) + "\n")
print("Toolchain verification complete.")
