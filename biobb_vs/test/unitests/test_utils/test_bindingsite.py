from biobb_common.tools import test_fixtures as fx
from biobb_vs.utils.bindingsite import BindingSite


class TestBindingSite():
    def setUp(self):
        fx.test_setup(self,'bindingsite')

    def tearDown(self):
        fx.test_teardown(self)
        pass

    def test_bindingsite(self):
        BindingSite(properties=self.properties, **self.paths).launch()
        assert fx.not_empty(self.paths['output_pdb_path'])
        assert fx.equal(self.paths['output_pdb_path'], self.paths['ref_output_pdb_path'])
