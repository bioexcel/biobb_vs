from biobb_common.tools import test_fixtures as fx
from biobb_vs.utils.box import Box


class TestBox():
    def setUp(self):
        fx.test_setup(self,'box')

    def tearDown(self):
        fx.test_teardown(self)
        pass

    def test_box(self):
        Box(properties=self.properties, **self.paths).launch()
        assert fx.not_empty(self.paths['output_pdb_path'])
        assert fx.equal(self.paths['output_pdb_path'], self.paths['ref_output_pdb_path'])