from biobb_common.tools import test_fixtures as fx
from biobb_vs.fpocket.fpocket import fpocket

class TestFPocket():
    def setUp(self):
        fx.test_setup(self,'fpocket')

    def tearDown(self):
        fx.test_teardown(self)
        pass

    def test_fpocket(self):
        fpocket(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_pockets_zip'])
        #assert fx.equal(self.paths['output_pockets_zip'], self.paths['ref_output_pockets_zip'])
        assert fx.not_empty(self.paths['output_summary'])
        #assert fx.equal(self.paths['output_summary'], self.paths['ref_output_summary'])
