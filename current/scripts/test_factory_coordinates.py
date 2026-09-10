"""Regression cases for shifted, mirrored and rotated factory placements."""
import copy
import unittest
from factory_coordinates import check_cpl


class FactoryCoordinates(unittest.TestCase):
    def setUp(self):
        self.rows=[{'Designator':'U1','Mid X':'12mm','Mid Y':'-11mm','Layer':'Bottom','Rotation':'90'}]
        self.components=[dict(reference='U1',x_mm=12,y_mm=-11,rotation_deg=90,side='bottom',pads=[
            dict(number='1',x_mm=11,y_mm=-12,copper_bottom=True),
            dict(number='2',x_mm=13,y_mm=-10,copper_bottom=True)])]
        self.pads=[('bottom','U1','1',11,-12),('bottom','U1','2',13,-10)]

    def test_matching_absolute_coordinates(self):
        self.assertEqual(check_cpl(self.rows,self.components,self.pads),2)

    def test_lower_left_cpl_against_upper_left_gerber_fails(self):
        self.rows[0]['Mid Y']='37mm'  # Historical +48 mm error.
        with self.assertRaises(AssertionError):check_cpl(self.rows,self.components,self.pads)

    def test_bottom_x_mirror_fails(self):
        self.rows[0]['Mid X']='-12mm'
        with self.assertRaises(AssertionError):check_cpl(self.rows,self.components,self.pads)

    def test_wrong_rotation_fails(self):
        self.rows[0]['Rotation']='0'
        with self.assertRaises(AssertionError):check_cpl(self.rows,self.components,self.pads)

    def test_gerber_shift_fails_even_if_native_and_cpl_agree(self):
        shifted=[(s,r,p,x,y+48) for s,r,p,x,y in self.pads]
        with self.assertRaises(AssertionError):check_cpl(self.rows,self.components,shifted)


if __name__=='__main__':unittest.main()
