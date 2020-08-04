from biobb_common.tools import test_fixtures as fx
from biobb_vs.utils.extract_model_pdbqt import ExtractModelPDBQT


class TestExtractModelPDBQT():
    def setUp(self):
        fx.test_setup(self,'extract_model_pdbqt')

    def tearDown(self):
        fx.test_teardown(self)
        pass

    def test_extract_model_pdbqt(self):
        ExtractModelPDBQT(properties=self.properties, **self.paths).launch()
        assert fx.not_empty(self.paths['output_pdbqt_path'])
        assert fx.equal(self.paths['output_pdbqt_path'], self.paths['ref_output_pdbqt_path'])