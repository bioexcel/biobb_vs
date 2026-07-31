# type: ignore
"""Checks the command line GninaRun builds, without running gnina.

gnina ships neither in the biobb_vs container nor in conda, and its official
image is tens of gigabytes, so a container test that actually executes gnina
cannot run anywhere. These tests instead drive ``build_cmd`` directly, which
needs no gnina and no container runtime, and pin down the parts of the command
that only the container code path exercises: the working directory, and the fact
that staged files are addressed by bare name inside the container volume.
"""
from biobb_common.tools import test_fixtures as fx

from biobb_vs.gnina.gnina_run import GninaRun


def build_cmd(properties, paths):
    """Stages the inputs and returns the command line, running nothing"""
    obj = GninaRun(properties=properties, **paths)
    obj.check_data_params(obj.out_log, obj.err_log)
    obj.stage_files()
    try:
        return obj.build_cmd()
    finally:
        obj.remove_tmp_files()


def flag_value(cmd, flag):
    """Returns the token following flag in cmd"""
    return cmd[cmd.index(flag) + 1]


class TestGninaRunDockerCmd():
    def setup_class(self):
        fx.test_setup(self, 'gnina_run_docker')

    def teardown_class(self):
        fx.test_teardown(self)
        pass

    def test_gnina_run_docker_cmd(self):
        cmd = build_cmd(self.properties, self.paths)

        # the command runs inside the mounted volume
        assert cmd[:3] == ['cd', '/data', ';']
        assert cmd[3] == 'gnina'

        # every staged file is addressed by bare name, never by a host path
        for flag in ('--receptor', '--ligand', '--out', '--autobox_ligand', '--log'):
            value = flag_value(cmd, flag)
            assert '/' not in value, '%s should be a bare name inside the container, got %s' % (flag, value)

        assert flag_value(cmd, '--receptor') == 'vina_receptor.pdbqt'
        assert flag_value(cmd, '--ligand') == 'gnina_ligand.sdf'
        assert flag_value(cmd, '--autobox_ligand') == 'gnina_autobox.pdb'
        assert flag_value(cmd, '--out') == 'output_gnina.sdf'
        assert flag_value(cmd, '--log') == 'output_gnina.log'

        # gnina writes its own log, it is not a shell redirection
        assert '>' not in cmd

        # properties reach gnina under the names gnina actually accepts
        assert flag_value(cmd, '--cnn_scoring') == 'none'
        assert flag_value(cmd, '--seed') == '42'
        assert flag_value(cmd, '--min_rmsd_filter') == '1.0'
        assert '--min_rmsd' not in cmd
        assert '--energy_range' not in cmd
        assert '--verbosity' not in cmd


class TestGninaRunLocalCmd():
    def setup_class(self):
        fx.test_setup(self, 'gnina_run')

    def teardown_class(self):
        fx.test_teardown(self)
        pass

    def test_gnina_run_local_cmd(self):
        cmd = build_cmd(self.properties, self.paths)

        # locally the staged files are addressed by their full path
        assert cmd[0] == 'cd'
        assert cmd[1].endswith(self.properties['path'].split('/')[-1]) or '/' in cmd[1]
        for flag in ('--receptor', '--ligand', '--out'):
            assert flag_value(cmd, flag).startswith('/'), '%s should be an absolute staged path' % flag

        # switches are emitted bare, never followed by a stringified boolean
        assert '--no_gpu' in cmd
        following = cmd[cmd.index('--no_gpu') + 1:]
        assert following == [] or following[0].startswith('--')

    def test_gnina_run_omitted_optional_outputs(self):
        # optional outputs are missing from stage_io_dict when unset, which must
        # not blow up while the command is being put together
        paths = {key: value for key, value in self.paths.items()
                 if key not in ('output_summary_path', 'output_log_path')}
        cmd = build_cmd(self.properties, paths)
        assert '--log' not in cmd
        assert '--out' in cmd


class TestGninaRunBoxCmd():
    def setup_class(self):
        fx.test_setup(self, 'gnina_run_box')

    def teardown_class(self):
        fx.test_teardown(self)
        pass

    def test_gnina_run_box_cmd(self):
        cmd = build_cmd(self.properties, self.paths)

        assert flag_value(cmd, '--center_x') == '7.293'
        assert flag_value(cmd, '--center_y') == '7.293'
        assert flag_value(cmd, '--center_z') == '-2.136'

        # SIZE is the full box edge length, which is what gnina reads from
        # --size_x/y/z, so it reaches gnina untouched just as it does in
        # autodock_vina_run. These are vina_box.pdb's REMARK values verbatim.
        assert float(flag_value(cmd, '--size_x')) == 16.319
        assert float(flag_value(cmd, '--size_y')) == 11.521
        assert float(flag_value(cmd, '--size_z')) == 13.047

        # the box file is read here, it is never handed to gnina
        assert '--autobox_ligand' not in cmd
