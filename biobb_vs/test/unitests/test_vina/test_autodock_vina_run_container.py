# type: ignore
import pytest
from biobb_common.tools import test_fixtures as fx
from biobb_vs.vina.autodock_vina_run import autodock_vina_run


class TestAutoDockVinaRunDocker():
    def setup_class(self):
        fx.test_setup(self, 'autodock_vina_run_docker')

    def teardown_class(self):
        fx.test_teardown(self)
        pass

    def test_autodock_vina_run_docker(self):
        autodock_vina_run(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_pdbqt_path'])
        assert fx.not_empty(self.paths['output_log_path'])


@pytest.mark.skip(reason="singularity currently not available")
class TestAutoDockVinaRunSingularity():
    def setup_class(self):
        fx.test_setup(self, 'autodock_vina_run_singularity')

    def teardown_class(self):
        fx.test_teardown(self)
        pass

    def test_autodock_vina_run_singularity(self):
        autodock_vina_run(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_pdbqt_path'])
        assert fx.not_empty(self.paths['output_log_path'])
