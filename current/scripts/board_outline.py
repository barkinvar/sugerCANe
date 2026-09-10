"""Reconstruct the exported contour and compare it with mechanical intent."""
import math
from gerbonara.graphic_objects import Arc, Line
from shapely.geometry import LineString
from shapely.ops import polygonize
from layout_contract import WIDTH, HEIGHT, RADIUS


def verified_outline(objects, tolerance=.001):
    w, h, r = WIDTH, HEIGHT, RADIUS
    expected_lines = {
        frozenset(((r, 0), (w-r, 0))),
        frozenset(((w, -r), (w, -(h-r)))),
        frozenset(((w-r, -h), (r, -h))),
        frozenset(((0, -(h-r)), (0, -r))),
    }
    expected_arcs = {
        frozenset(((w-r, 0), (w, -r))),
        frozenset(((w, -(h-r)), (w-r, -h))),
        frozenset(((r, -h), (0, -(h-r)))),
        frozenset(((0, -r), (r, 0))),
    }
    assert len(objects) == 8, 'Expected four straight edges and four corner arcs'
    lines, arcs, segments = set(), set(), []
    for obj in objects:
        ends = frozenset(((round(obj.x1, 5), round(obj.y1, 5)),
                          (round(obj.x2, 5), round(obj.y2, 5))))
        if isinstance(obj, Arc):
            assert abs(math.hypot(obj.cx, obj.cy) - r) < 1e-5
            arcs.add(ends)
            segments.extend(LineString(((s.x1, s.y1), (s.x2, s.y2)))
                            for s in obj.approximate(max_error=tolerance))
        else:
            assert isinstance(obj, Line), 'Unexpected board-outline primitive'
            lines.add(ends)
            segments.append(LineString(((obj.x1, obj.y1), (obj.x2, obj.y2))))
    assert lines == expected_lines and arcs == expected_arcs
    # Arc tessellation can end at 1.499999999999999 instead of the exact
    # adjoining 1.5 mm endpoint. Snap to the Gerber's micrometer precision.
    segments = [LineString([(round(x, 6), round(y, 6)) for x, y in s.coords])
                for s in segments]
    contours = list(polygonize(segments))
    assert len(contours) == 1 and contours[0].is_valid, 'Contour must close once'
    contour = contours[0]
    assert abs(contour.area - (w*h - (4 - math.pi)*r**2)) < .02
    return contour
