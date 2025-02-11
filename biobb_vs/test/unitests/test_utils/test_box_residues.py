# type: ignore
from biobb_common.tools import test_fixtures as fx
from biobb_vs.utils.box_residues import box_residues


class TestBoxResidues():
    def setup_class(self):
        fx.test_setup(self, 'box_residues')

    def teardown_class(self):
        fx.test_teardown(self)
        pass

    def test_box_residues(self):
        box_residues(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_pdb_path'])
        assert fx.equal_txt(self.paths['output_pdb_path'], self.paths['ref_output_pdb_path'])
