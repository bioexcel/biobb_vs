from biobb_common.tools import test_fixtures as fx
from biobb_vs.utils.extract_model_pdbqt import extract_model_pdbqt


class TestExtractModelPDBQT():
    def setup_class(self):
        fx.test_setup(self,'extract_model_pdbqt')

    def teardown_class(self):
        fx.test_teardown(self)
        pass

    def test_extract_model_pdbqt(self):
        extract_model_pdbqt(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_pdbqt_path'])
        assert fx.equal(self.paths['output_pdbqt_path'], self.paths['ref_output_pdbqt_path'])