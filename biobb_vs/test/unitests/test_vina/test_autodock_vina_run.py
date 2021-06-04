from biobb_common.tools import test_fixtures as fx
from biobb_vs.vina.autodock_vina_run import autodock_vina_run


class TestAutoDockVinaRun():
    def setUp(self):
        fx.test_setup(self,'autodock_vina_run')

    def tearDown(self):
        fx.test_teardown(self)
        pass

    def test_autodock_vina_run(self):
        autodock_vina_run(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_pdbqt_path'])
        assert fx.not_empty(self.paths['output_log_path'])
