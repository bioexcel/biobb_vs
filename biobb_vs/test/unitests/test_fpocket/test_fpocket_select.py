from biobb_common.tools import test_fixtures as fx
from biobb_vs.fpocket.fpocket_select import fpocket_select

class TestFPocket():
    def setUp(self):
        fx.test_setup(self,'fpocket_select')

    def tearDown(self):
        fx.test_teardown(self)
        pass

    def test_fpocket_select(self):
        fpocket_select(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_sel_pockets_zip'])
        assert fx.equal(self.paths['output_sel_pockets_zip'], self.paths['ref_output_sel_pockets_zip'])
