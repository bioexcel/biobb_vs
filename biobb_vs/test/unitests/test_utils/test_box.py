from biobb_common.tools import test_fixtures as fx
from biobb_vs.utils.box import box


class TestBox():
    def setUp(self):
        fx.test_setup(self,'box')

    def tearDown(self):
        fx.test_teardown(self)
        pass

    def test_box(self):
        box(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_pdb_path'])
        assert fx.equal(self.paths['output_pdb_path'], self.paths['ref_output_pdb_path'])