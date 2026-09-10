"""Independent same-net ground-gap and narrow-neck screens on copper polygons."""
from shapely.ops import nearest_points


def polygons(geometry):
    if geometry.geom_type == 'Polygon':
        return [geometry]
    return [p for child in getattr(geometry, 'geoms', []) for p in polygons(child)]


def inspect_ground(ground, minimum_gap=.25, neck_screen=.24, minimum_core_area=.025):
    """Screen actual copper, including areas joined elsewhere through vias.

    Erosion must not split a ground island into multiple substantial cores.
    The 0.24 mm screen leaves geometric margin below the 0.25 mm native pour
    minimum; it is not a current-capacity or ground-return impedance model.
    Tiny residual tips below 0.025 mm² are excluded from the neck screen.
    """
    gaps = []
    nearest = None
    for i, a in enumerate(ground):
        for j in range(i+1, len(ground)):
            distance = a.distance(ground[j])
            if nearest is None or distance < nearest:
                nearest = distance
            if distance < minimum_gap-.002:  # Two 1 µm Gerber approximation errors.
                p, q = nearest_points(a, ground[j])
                gaps.append(dict(islands=[i, j], gap_mm=distance,
                                 a_mm=list(p.coords[0]), b_mm=list(q.coords[0])))
    necks = []
    for i, copper in enumerate(ground):
        cores = [p for p in polygons(copper.buffer(-neck_screen/2))
                 if p.area > minimum_core_area]
        if len(cores) > 1:
            necks.append(dict(island=i, surviving_core_areas_mm2=[p.area for p in cores]))
    return dict(result='FAIL' if gaps or necks else 'PASS', ground_islands=len(ground),
                minimum_separate_island_gap_mm=nearest, required_gap_mm=minimum_gap,
                neck_screen_width_mm=neck_screen, minimum_surviving_core_area_mm2=minimum_core_area,
                narrow_gaps=gaps, narrow_necks=necks)
