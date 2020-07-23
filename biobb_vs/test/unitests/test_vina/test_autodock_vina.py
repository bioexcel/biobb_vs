from biobb_common.tools import test_fixtures as fx
from biobb_vs.vina.autodock_vina import AutoDockVina


class TestAutoDockVina():
    def setUp(self):
        fx.test_setup(self,'autodock_vina')

    def tearDown(self):
        fx.test_teardown(self)
        pass

    def test_autodock_vina(self):
        AutoDockVina(properties=self.properties, **self.paths).launch()
        assert fx.not_empty(self.paths['output_pdbqt_path'])
        #assert fx.equal(self.paths['output_pdbqt_path'], self.paths['ref_output_pdbqt_path'])
        assert fx.not_empty(self.paths['output_log_path'])
        #assert fx.equal(self.paths['output_log_path'], self.paths['ref_output_log_path'])
