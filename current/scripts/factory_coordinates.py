"""Check factory placement coordinates against independently parsed pad flashes."""
import math


def check_cpl(rows, components, gerber_pads):
    """All coordinates are absolute Gerber mm, X right and Y up on both sides.

    gerber_pads contains (side, ref, pin, x, y) records. Package-library rotation
    offsets at the assembler remain a separate pin-1 review.
    """
    physical = {c['reference']: c for c in components}
    pads = {(side, ref, pin, round(x, 5), round(y, 5))
            for side, ref, pin, x, y in gerber_pads}
    assert len(rows) == len({r['Designator'] for r in rows})
    checked = 0
    for row in rows:
        ref = row['Designator']; c = physical[ref]
        side = row['Layer'].lower()
        x = float(row['Mid X'].removesuffix('mm'))
        y = float(row['Mid Y'].removesuffix('mm'))
        angle = (float(row['Rotation'])-c['rotation_deg']+180) % 360-180
        assert side == c['side'], (ref, 'CPL side differs from native')
        assert abs(angle) < 1e-5, (ref, 'Unreviewed CPL rotation')
        assert math.hypot(x-c['x_mm'], y-c['y_mm']) < 1e-5, (ref, 'CPL/Gerber origin mismatch')
        for pad in c['pads']:
            if not pad['copper_'+side]: continue
            # Position each pad from the CPL centroid and the native relative
            # pad offset, then compare with the actual exported copper flash.
            px = x + pad['x_mm'] - c['x_mm']
            py = y + pad['y_mm'] - c['y_mm']
            assert (side, ref, pad['number'], round(px,5), round(py,5)) in pads, (ref, pad['number'], 'CPL does not land on Gerber pad')
            checked += 1
    return checked
