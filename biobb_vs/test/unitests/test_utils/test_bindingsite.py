from biobb_common.tools import test_fixtures as fx
from biobb_vs.utils.bindingsite import bindingsite


class TestBindingSite():
    def setup_class(self):
        fx.test_setup(self, 'bindingsite')

    def teardown_class(self):
        fx.test_teardown(self)
        pass

    def test_bindingsite(self):
        bindingsite(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_pdb_path'])
        assert fx.equal(self.paths['output_pdb_path'], self.paths['ref_output_pdb_path'])
