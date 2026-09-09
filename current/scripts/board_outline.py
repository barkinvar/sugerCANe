"""Reconstruct and verify the 52 x 74 mm, R1.5 exported board contour."""
import math
from gerbonara.graphic_objects import Arc, Line
from shapely.geometry import LineString
from shapely.ops import polygonize


def verified_outline(objects, tolerance=.001):
    expected_lines = {
        frozenset(((1.5, 0), (50.5, 0))),
        frozenset(((52, -1.5), (52, -72.5))),
        frozenset(((50.5, -74), (1.5, -74))),
        frozenset(((0, -72.5), (0, -1.5))),
    }
    expected_arcs = {
        frozenset(((50.5, 0), (52, -1.5))),
        frozenset(((52, -72.5), (50.5, -74))),
        frozenset(((1.5, -74), (0, -72.5))),
        frozenset(((0, -1.5), (1.5, 0))),
    }
    assert len(objects) == 8, 'Expected four straight edges and four corner arcs'
    lines, arcs, segments = set(), set(), []
    for obj in objects:
        ends = frozenset(((round(obj.x1, 5), round(obj.y1, 5)),
                          (round(obj.x2, 5), round(obj.y2, 5))))
        if isinstance(obj, Arc):
            assert abs(math.hypot(obj.cx, obj.cy) - 1.5) < 1e-5
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
    assert abs(contour.area - (52 * 74 - (4 - math.pi) * 1.5 ** 2)) < .02
    return contour
