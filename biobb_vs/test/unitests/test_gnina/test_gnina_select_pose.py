# type: ignore
import pytest
from biobb_common.tools import test_fixtures as fx

from biobb_vs.gnina.gnina_select_pose import gnina_select_pose


class TestGninaSelectPose():
    def setup_class(self):
        fx.test_setup(self, 'gnina_select_pose')

    def teardown_class(self):
        fx.test_teardown(self)
        pass

    def test_gnina_select_pose(self):
        gnina_select_pose(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_sdf_path'])
        # the record is copied verbatim, so it must match byte for byte
        assert fx.equal(self.paths['output_sdf_path'], self.paths['ref_output_sdf_path'])

    def test_gnina_select_pose_out_of_range(self):
        # the poses file holds 6 records, so asking for the 99th must fail cleanly
        with pytest.raises(SystemExit):
            gnina_select_pose(input_sdf_path=self.paths['input_sdf_path'],
                              output_sdf_path=self.paths['output_sdf_path'],
                              properties={'pose': 99})

    def test_gnina_select_pose_unknown_sort_by(self):
        with pytest.raises(SystemExit):
            gnina_select_pose(input_sdf_path=self.paths['input_sdf_path'],
                              output_sdf_path=self.paths['output_sdf_path'],
                              properties={'sort_by': 'nonsense'})

    def test_gnina_select_pose_unknown_ligand(self):
        with pytest.raises(SystemExit):
            gnina_select_pose(input_sdf_path=self.paths['input_sdf_path'],
                              output_sdf_path=self.paths['output_sdf_path'],
                              properties={'ligand': 99})


class TestGninaSelectPoseSorted():
    def setup_class(self):
        fx.test_setup(self, 'gnina_select_pose_sorted')

    def teardown_class(self):
        fx.test_teardown(self)
        pass

    def test_gnina_select_pose_sorted(self):
        # reordering by empirical affinity surfaces a different pose than the
        # order gnina wrote, which ranks by CNN score
        gnina_select_pose(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_sdf_path'])
        assert fx.equal(self.paths['output_sdf_path'], self.paths['ref_output_sdf_path'])
