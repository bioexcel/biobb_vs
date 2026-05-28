# type: ignore
from biobb_common.tools import test_fixtures as fx
from biobb_vs.fpocket.fpocket_run import fpocket_run
import pytest
import sys


class TestFPocketRunDocker():
    def setup_class(self):
        fx.test_setup(self, 'fpocket_run_docker')

    def teardown_class(self):
        fx.test_teardown(self)
        pass

    def test_fpocket_run_docker(self):
        fpocket_run(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_pockets_zip'])
        # assert fx.equal(self.paths['output_pockets_zip'], self.paths['ref_output_pockets_zip'])
        assert fx.not_empty(self.paths['output_summary'])
        # assert fx.equal(self.paths['output_summary'], self.paths['ref_output_summary'])


@pytest.mark.skipif(sys.platform == 'darwin', reason="singularity not available on macOS")
class TestFPocketRunSingularity():
    def setup_class(self):
        fx.test_setup(self, 'fpocket_run_singularity')

    def teardown_class(self):
        fx.test_teardown(self)
        pass

    def test_fpocket_run_singularity(self):
        fpocket_run(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_pockets_zip'])
        # assert fx.equal(self.paths['output_pockets_zip'], self.paths['ref_output_pockets_zip'])
        assert fx.not_empty(self.paths['output_summary'])
        # assert fx.equal(self.paths['output_summary'], self.paths['ref_output_summary'])
