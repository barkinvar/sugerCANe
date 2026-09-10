"""Regression fixtures for routing rules and contact-aware copper DC analysis."""
import unittest
import math
import numpy as np
from check_routing import inspect
from check_order_readiness import dc_solver


def track(a, b, *, net='SIG', layer=0, width=.25, kind='line'):
    return dict(a=a, b=b, net=net, layer=layer, width=width, kind=kind)


def audit(*tracks, pads=(), vias=()):
    return inspect(dict(tracks=[dict(t, id=str(i)) for i,t in enumerate(tracks)],
                        pads=list(pads), vias=list(vias)))


class RoutingRules(unittest.TestCase):
    def test_straight_and_chamfer(self):
        self.assertEqual(audit(track((0,0),(1,0)), track((1,0),(2,1)),
                               track((2,1),(2,2)))['result'], 'PASS')

    def test_curve_and_non_octilinear(self):
        self.assertIn('curved_tracks', audit(track((0,0),(1,1), kind='arc'))['findings'])
        self.assertIn('non_45_direction', audit(track((0,0),(1,.8)))['findings'])

    def test_native_rounding_only(self):
        self.assertEqual(audit(track((0,0),(1,1.000001)))['result'], 'PASS')
        self.assertIn('non_45_direction', audit(track((0,0),(1,1.001)))['findings'])

    def test_duplicates_and_overlap(self):
        self.assertIn('duplicates', audit(track((0,0),(2,0)), track((2,0),(0,0)))['findings'])
        self.assertIn('collinear_overlap', audit(track((0,0),(2,0)),
                                               track((1,0),(3,0), width=.5))['findings'])

    def test_layers_and_nets_are_distinct(self):
        self.assertEqual(audit(track((0,0),(2,0)), track((0,0),(2,0),layer=2),
                               track((0,0),(2,0),net='OTHER'))['result'], 'PASS')

    def test_zero_length_and_tiny_free_jog(self):
        self.assertIn('zero_length', audit(track((0,0),(0,0)))['findings'])
        self.assertIn('short_free_segments', audit(track((0,0),(.025,.025)))['findings'])

    def test_local_contact_exception(self):
        pad=dict(net='SIG', layer=0, polygons=[[(-.2,-.2),(.2,-.2),(.2,.2),(-.2,.2)]])
        via=dict(net='SIG', at=(0,0), width=.6, layers=[0,2])
        self.assertEqual(audit(track((0,0),(.025,.025)), pads=[pad])['result'], 'PASS')
        self.assertEqual(audit(track((0,0),(.025,.025),layer=2), vias=[via])['result'], 'PASS')
        self.assertIn('short_free_segments', audit(track((1,1),(1.025,1.025)), pads=[pad])['findings'])
        self.assertIn('short_free_segments', audit(track((0,0),(.025,.025),layer=4), vias=[via])['findings'])

    def test_sharp_free_bend(self):
        for b in [(1,1), (0,1)]:
            self.assertIn('sharp_free_bends', audit(track((0,0),(1,0)),track((1,0),b))['findings'])

    def test_real_branch_junctions(self):
        self.assertEqual(audit(track((0,-1),(1,0)),track((0,1),(1,0)),
                               track((1,0),(2,0)))['result'], 'PASS')

    def test_perpendicular_tap_requires_chamfer(self):
        self.assertIn('unchamfered_free_branches',audit(track((0,0),(1,0)),track((1,0),(2,0)),
                               track((1,0),(1,1)))['findings'])

    def test_segment_interior_is_a_real_junction(self):
        result=audit(track((0,0),(2,0)),track((1,0),(1,1)))
        self.assertIn('implicit_free_junctions',result['findings'])
        self.assertIn('unchamfered_free_branches',result['findings'])

    def test_acute_side_tap_and_four_way_crossing(self):
        self.assertIn('unchamfered_free_branches',audit(track((0,0),(1,0)),track((1,0),(2,0)),
                               track((1,0),(2,1)))['findings'])
        self.assertEqual(audit(*(track((0,0),end) for end in [(1,0),(-1,0),(0,1),(0,-1)]))['result'],'PASS')

    def test_pad_contact_permits_perpendicular_branch(self):
        pad=dict(net='SIG',layer=0,polygons=[[(-.3,-.3),(.3,-.3),(.3,.3),(-.3,.3)]])
        self.assertEqual(audit(track((-1,0),(1,0)),track((0,0),(0,1)),pads=[pad])['result'],'PASS')

    def test_merge_only_equal_width_collinear_pieces(self):
        self.assertIn('redundant_collinear_joint', audit(track((0,0),(1,0)),track((1,0),(2,0)))['findings'])
        self.assertEqual(audit(track((0,0),(1,0)),track((1,0),(2,0),width=.5))['result'], 'PASS')


class CopperNetwork(unittest.TestCase):
    rho=1.724e-5*(1+.00393*65)
    depths={'F.Cu':.0175,'In2.Cu':1.3275,'B.Cu':1.5625}

    def drop(self, tracks, start, end, vias=(), reference=None):
        pads=[dict(ref=ref,number='1',contacts=[point])
              for ref,point in [('SRC',start),('LOAD',end)]]
        if reference is not None:pads.append(dict(ref='REF',number='1',contacts=[reference]))
        geo=dict(tracks=tracks,vias=list(vias),pads=pads,
                 layer_names={'0':'F.Cu','2':'B.Cu','6':'In2.Cu'})
        v=dc_solver(geo,self.depths)(('SRC','1'),{('LOAD','1'):1},
                                   ('REF','1') if reference is not None else None)
        return v[str(('SRC','1'))]-v[str(('LOAD','1'))]

    @staticmethod
    def line(a,b,layer=0):
        return dict(start=a,end=b,width=.25,layer=layer)

    def test_known_resistance_and_subdivision(self):
        expected=self.rho*10/(.25*.035)
        self.assertAlmostEqual(self.drop([self.line((0,0),(10,0))],(0,0,0),(10,0,0)),expected)
        self.assertAlmostEqual(self.drop([self.line((0,0),(4,0)),self.line((4,0),(10,0))],
                                         (0,0,0),(10,0,0)),expected)

    def test_overlapping_end_caps_conduct(self):
        self.assertAlmostEqual(self.drop([self.line((0,0),(4.95,0)),self.line((5.05,0),(10,0))],
                                         (0,0,0),(10,0,0)),self.rho*10/(.25*.035))

    def test_interior_pad_contact_and_voltage_reference(self):
        traces=[self.line((0,0),(10,0))]
        expected=self.rho*8/(.25*.035)
        self.assertAlmostEqual(self.drop(traces,(0,0,0),(8,0,0)),expected)
        self.assertAlmostEqual(self.drop(traces,(0,0,0),(8,0,0),reference=(5,0,0)),expected)

    def test_via_midsegment_and_three_layers(self):
        via=dict(at=(5,0),width=.6,drill=.3,layers=[0,2,6])
        traces=[self.line((0,0),(10,0)),self.line((5,0),(5,5),2)]
        expected=self.rho*10/(.25*.035)+self.rho*1.545/(math.pi*.3*.020)
        self.assertAlmostEqual(self.drop(traces,(0,0,0),(5,5,2),[via]),expected)
        traces.append(self.line((5,0),(8,0),6))
        self.assertAlmostEqual(self.drop(traces,(0,0,0),(5,5,2),[via]),expected)

    def test_real_gap_stays_open(self):
        with self.assertRaises(np.linalg.LinAlgError):
            self.drop([self.line((0,0),(4,0)),self.line((6,0),(10,0))],(0,0,0),(10,0,0))

    def test_crossing_layers_stay_isolated(self):
        with self.assertRaises(np.linalg.LinAlgError):
            self.drop([self.line((0,0),(10,0)),self.line((5,-5),(5,5),2)],(0,0,0),(5,5,2))


if __name__ == '__main__':
    unittest.main()
