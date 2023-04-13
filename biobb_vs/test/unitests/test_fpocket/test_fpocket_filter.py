from biobb_common.tools import test_fixtures as fx
from biobb_vs.fpocket.fpocket_filter import fpocket_filter


class TestFPocketFilter():
    def setup_class(self):
        fx.test_setup(self, 'fpocket_filter')

    def teardown_class(self):
        fx.test_teardown(self)
        pass

    def test_fpocket_filter(self):
        fpocket_filter(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_filter_pockets_zip'])
        assert fx.equal(self.paths['output_filter_pockets_zip'], self.paths['ref_output_filter_pockets_zip'])
