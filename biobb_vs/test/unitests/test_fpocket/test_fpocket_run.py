from biobb_common.tools import test_fixtures as fx
from biobb_vs.fpocket.fpocket_run import fpocket_run


class TestFPocketRun():
    def setup_class(self):
        fx.test_setup(self, 'fpocket_run')

    def teardown_class(self):
        fx.test_teardown(self)
        pass

    def test_fpocket_run(self):
        fpocket_run(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_pockets_zip'])
        # assert fx.equal(self.paths['output_pockets_zip'], self.paths['ref_output_pockets_zip'])
        assert fx.not_empty(self.paths['output_summary'])
        # assert fx.equal(self.paths['output_summary'], self.paths['ref_output_summary'])
