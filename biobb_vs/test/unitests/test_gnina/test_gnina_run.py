# type: ignore
import shutil

import pytest
from biobb_common.tools import test_fixtures as fx

from biobb_vs.gnina.gnina_run import gnina_run

# gnina is not distributed with this package and is not installable from conda,
# so the docking tests only run where the binary is actually available
gnina_required = pytest.mark.skipif(shutil.which('gnina') is None,
                                    reason="gnina binary not found in PATH")


@gnina_required
class TestGninaRun():
    def setup_class(self):
        fx.test_setup(self, 'gnina_run')

    def teardown_class(self):
        fx.test_teardown(self)
        pass

    def test_gnina_run(self):
        # docking is stochastic, so the outputs are only checked for existence
        assert fx.exe_success(gnina_run(properties=self.properties, **self.paths))
        assert fx.not_empty(self.paths['output_sdf_path'])
        assert fx.not_empty(self.paths['output_summary_path'])
        assert fx.not_empty(self.paths['output_log_path'])


@gnina_required
class TestGninaRunBox():
    def setup_class(self):
        fx.test_setup(self, 'gnina_run_box')

    def teardown_class(self):
        fx.test_teardown(self)
        pass

    def test_gnina_run_box(self):
        # same block driven from a box file instead of an autobox reference,
        # and with the optional outputs left out
        assert fx.exe_success(gnina_run(properties=self.properties, **self.paths))
        assert fx.not_empty(self.paths['output_sdf_path'])
