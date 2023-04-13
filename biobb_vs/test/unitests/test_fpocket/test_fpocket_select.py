from biobb_common.tools import test_fixtures as fx
from biobb_vs.fpocket.fpocket_select import fpocket_select


class TestFPocketSelect():
    def setup_class(self):
        fx.test_setup(self, 'fpocket_select')

    def teardown_class(self):
        fx.test_teardown(self)
        pass

    def test_fpocket_select(self):
        fpocket_select(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_pocket_pdb'])
        assert fx.equal(self.paths['output_pocket_pdb'], self.paths['ref_output_pocket_pdb'])
        assert fx.not_empty(self.paths['output_pocket_pqr'])
        assert fx.equal(self.paths['output_pocket_pqr'], self.paths['ref_output_pocket_pqr'])
