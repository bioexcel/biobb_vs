# type: ignore
from biobb_common.tools import test_fixtures as fx
from biobb_vs.utils.box import box


def assert_size_is_box_edge(box_pdb_path):
    """The SIZE written in the REMARK must be the full edge length of the box, which is
    what AutoDock Vina reads from --size_x/y/z, so it must match the span of the 8 box
    corner atoms."""
    lines = open(box_pdb_path).read().splitlines()
    size = [float(value) for value in lines[0].split()[-3:]]
    corners = [line for line in lines if line.startswith('HETATM')]
    assert len(corners) == 8
    for axis in range(3):
        coords = [float(line[30 + 8 * axis:38 + 8 * axis]) for line in corners]
        span = max(coords) - min(coords)
        assert abs(span - size[axis]) < 1e-3, (axis, span, size[axis])


class TestBox():
    def setup_class(self):
        fx.test_setup(self, 'box')

    def teardown_class(self):
        fx.test_teardown(self)
        pass

    def test_box(self):
        box(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_pdb_path'])
        assert fx.equal_txt(self.paths['output_pdb_path'], self.paths['ref_output_pdb_path'])
        assert_size_is_box_edge(self.paths['output_pdb_path'])
