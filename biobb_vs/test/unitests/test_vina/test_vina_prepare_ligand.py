from biobb_common.tools import test_fixtures as fx
from biobb_vs.vina.vina_prepare_ligand import VinaPrepareLigand


class TestVinaPrepareLigand():
    def setUp(self):
        fx.test_setup(self,'vina_prepare_ligand')

    def tearDown(self):
        fx.test_teardown(self)
        pass

    def test_vina_prepare_ligand(self):
        VinaPrepareLigand(properties=self.properties, **self.paths).launch()
        assert fx.not_empty(self.paths['output_ligand_path'])
        assert fx.equal(self.paths['output_ligand_path'], self.paths['ref_output_ligand_path'])
