from biobb_common.tools import test_fixtures as fx
from biobb_vs.vina.vina_prepare_receptor import VinaPrepareReceptor


class TestVinaPrepareReceptor():
    def setUp(self):
        fx.test_setup(self,'vina_prepare_receptor')

    def tearDown(self):
        fx.test_teardown(self)
        pass

    def test_vina_prepare_receptor(self):
        VinaPrepareReceptor(properties=self.properties, **self.paths).launch()
        assert fx.not_empty(self.paths['output_receptor_path'])
        assert fx.equal(self.paths['output_receptor_path'], self.paths['ref_output_receptor_path'])
