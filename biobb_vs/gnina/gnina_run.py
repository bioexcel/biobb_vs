#!/usr/bin/env python3

"""Module containing the GninaRun class and the command line interface."""
from pathlib import PurePath
from typing import Optional

from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger

from biobb_vs.gnina.common import check_input_path, check_output_path, process_output_gnina


class GninaRun(BiobbObject):
    """
    | biobb_vs GninaRun
    | Wrapper of the gnina software.
    | This class performs docking of a ligand to a receptor, optionally rescoring the poses with a convolutional neural network, via the `gnina <https://github.com/gnina/gnina>`_ software.

    Args:
        input_ligand_path (str): Path to the input ligand. It may hold several ligands and it must hold genuine 3D coordinates, as gnina samples torsions but never bond lengths, bond angles or ring conformations. File type: input. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/gnina/gnina_ligand.sdf>`_. Accepted formats: sdf (edam:format_3814), mol2 (edam:format_3816), pdb (edam:format_1476), pdbqt (edam:format_1476).
        input_receptor_path (str): Path to the input receptor. Every atom of this file is treated as rigid receptor, so any crystal ligand must be removed beforehand. Provide a PDBQT file for full control over protonation, as PDBQT input is passed to gnina unmodified. Charges are not taken into account, just hydrogen donor/acceptor character which depends on the protonation state. File type: input. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/vina/vina_receptor.pdbqt>`_. Accepted formats: pdb (edam:format_1476), pdbqt (edam:format_1476).
        input_box_path (str) (Optional): Path to the PDB file with the box center and size annotated as a REMARK, as written by the box and box_residues building blocks. Mutually exclusive with input_autobox_path. File type: input. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/vina/vina_box.pdb>`_. Accepted formats: pdb (edam:format_1476).
        input_autobox_path (str) (Optional): Path to a reference structure whose bounding coordinates define the docking box, for example a crystal ligand, an fpocket pocket or the whole receptor. It only needs atoms with Cartesian coordinates, it does not need to be a real molecule. Mutually exclusive with input_box_path. File type: input. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/gnina/gnina_autobox.pdb>`_. Accepted formats: sdf (edam:format_3814), mol2 (edam:format_3816), pdb (edam:format_1476), pdbqt (edam:format_1476), pqr (edam:format_1476).
        output_sdf_path (str): Path to the output file with the docked poses and their scores as SD data fields. Use a .sdf.gz extension to obtain gzip compressed output. File type: output. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/gnina/ref_output_gnina.sdf>`_. Accepted formats: sdf (edam:format_3814), gz (edam:format_3989).
        output_summary_path (str) (Optional): Path to the JSON summary file, holding one entry per output pose with the ligand it belongs to and every score gnina assigned to it. File type: output. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/gnina/ref_output_summary.json>`_. Accepted formats: json (edam:format_3464).
        output_log_path (str) (Optional): Path to the log file written by gnina. File type: output. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/gnina/ref_output_gnina.log>`_. Accepted formats: log (edam:format_2330).
        properties (dic - Python dictionary object containing the tool parameters, not input/output files):
            * **cpu** (*int*) - (1) [1~1000|1] Number of CPU cores to use. Keep it lower than or equal to exhaustiveness, and always set it explicitly on a shared machine.
            * **exhaustiveness** (*int*) - (8) [1~10000|1] Number of independent Monte Carlo search chains. This is the main sampling knob, but it gives diminishing returns past the default for a targeted pocket.
            * **num_modes** (*int*) - (9) [1~1000|1] Maximum number of binding modes written out.
            * **min_rmsd_filter** (*float*) - (1.0) [0~100|0.1] RMSD in Angstroms below which a pose is dropped as redundant with a better ranked one.
            * **num_mc_saved** (*int*) - (None) [1~10000|1] Number of top poses retained in each Monte Carlo chain, gnina defaults to 50 when unset.
            * **seed** (*int*) - (None) Explicit random seed. Docking is stochastic, so set it for reproducible runs.
            * **scoring** (*str*) - (None) Built-in empirical scoring function, gnina uses its own default when unset. Values: default (the gnina default empirical scoring function), vina (the AutoDock Vina scoring function), vinardo (a reparameterization of the Vina terms that often does better for virtual screening), ad4_scoring (the AutoDock4 scoring function), dkoes_fast (a fast variant of the dkoes scoring function), dkoes_scoring (the dkoes scoring function), dkoes_scoring_old (the legacy dkoes scoring function).
            * **cnn_scoring** (*str*) - (None) Where the convolutional neural network is used in the pipeline, gnina defaults to rescore when unset. Values: none (empirical scoring only throughout, by far the fastest), rescore (the network only re-ranks the final pool of poses), refinement (the network also locally minimizes poses after the Monte Carlo search, around ten times slower), metrorescore (network rescoring combined with Metropolis sampling), metrorefine (network refinement combined with Metropolis sampling), all (the network scores the whole search, very slow).
            * **cnn** (*str*) - (None) Name of a built-in convolutional neural network model, or a name ending in _ensemble to evaluate every built-in model sharing that prefix. gnina defaults to an ensemble of three models when unset.
            * **pose_sort_order** (*str*) - (None) How the internal pose pool is sorted before the redundancy filter and the num_modes cutoff are applied, so it can surface a different set of poses and not merely reorder them. gnina defaults to CNNscore when unset. Values: CNNscore (sort by network pose score, which answers whether a pose is right), CNNaffinity (sort by predicted affinity, which is what ranks compounds in a screen), Energy (sort by empirical energy).
            * **autobox_add** (*float*) - (None) [0~100|0.1] Buffer in Angstroms added on every side of the box derived from input_autobox_path, gnina defaults to 4 when unset. A larger box does not slow gnina down, but it does loosen the constraint on sampling.
            * **autobox_extend** (*bool*) - (None) Enlarge the box derived from input_autobox_path when needed so the input ligand can rotate freely inside it, gnina enables this when unset.
            * **minimize** (*bool*) - (False) Energy minimize the poses given in input_ligand_path instead of searching for new ones.
            * **score_only** (*bool*) - (False) Score the poses given in input_ligand_path without searching or minimizing.
            * **local_only** (*bool*) - (False) Restrict the search to a local one inside the box.
            * **no_gpu** (*bool*) - (False) Disable GPU acceleration even when a GPU is available.
            * **device** (*int*) - (None) [0~16|1] Index of the GPU device to use.
            * **quiet** (*bool*) - (False) Suppress the gnina output messages.
            * **binary_path** (*str*) - ('gnina') Path to the gnina executable in your local computer. gnina is not distributed with this package, install it from its binary release or run it through a container.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.
            * **sandbox_path** (*str*) - ("./") [WF property] Parent path to the sandbox directory.
            * **container_path** (*str*) - (None) Container path definition.
            * **container_image** (*str*) - ('gnina/gnina:latest') Container image definition.
            * **container_volume_path** (*str*) - ('/data') Container volume path definition.
            * **container_working_dir** (*str*) - (None) Container working directory definition.
            * **container_user_id** (*str*) - (None) Container user_id definition.
            * **container_shell_path** (*str*) - ('/bin/bash -c') Path to default shell inside the container.

    Examples:
        This is a use example of how to use the building block from Python::

            from biobb_vs.gnina.gnina_run import gnina_run
            prop = {
                'cnn_scoring': 'rescore',
                'scoring': 'vinardo',
                'exhaustiveness': 8,
                'cpu': 4,
                'seed': 42
            }
            gnina_run(input_ligand_path='/path/to/myLigand.sdf',
                      input_receptor_path='/path/to/myReceptor.pdbqt',
                      input_box_path='/path/to/myBox.pdb',
                      output_sdf_path='/path/to/newPoses.sdf',
                      output_summary_path='/path/to/newSummary.json',
                      output_log_path='/path/to/newLog.log',
                      properties=prop)

        Instead of a box file, the docking box may be drawn around a reference structure,
        which is gnina's own idiom and needs no box file at all. An fpocket pocket works as
        a reference, and so does the receptor itself for whole protein docking::

            gnina_run(input_ligand_path='/path/to/myLigand.sdf',
                      input_receptor_path='/path/to/myReceptor.pdbqt',
                      input_autobox_path='/path/to/myPocket.pqr',
                      output_sdf_path='/path/to/newPoses.sdf',
                      properties={'autobox_add': 4})

        To reach a GPU from inside a container, ask the container runtime for it through the
        container_generic_command property, as in {'container_path': 'docker',
        'container_generic_command': 'run --gpus all'} for Docker or 'run --nv' for Singularity.

    Info:
        * wrapped_software:
            * name: gnina
            * version: >=1.3
            * license: Apache-2.0 and GPL-2.0
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl

    """

    # gnina flags taking a value, as (flag, property name) pairs
    VALUE_FLAGS = (
        ("--cpu", "cpu"),
        ("--exhaustiveness", "exhaustiveness"),
        ("--num_modes", "num_modes"),
        ("--min_rmsd_filter", "min_rmsd_filter"),
        ("--num_mc_saved", "num_mc_saved"),
        ("--seed", "seed"),
        ("--scoring", "scoring"),
        ("--cnn_scoring", "cnn_scoring"),
        ("--cnn", "cnn"),
        ("--pose_sort_order", "pose_sort_order"),
        ("--device", "device"),
    )

    # gnina flags that are bare switches
    SWITCH_FLAGS = (
        ("--minimize", "minimize"),
        ("--score_only", "score_only"),
        ("--local_only", "local_only"),
        ("--no_gpu", "no_gpu"),
        ("--quiet", "quiet"),
    )

    def __init__(self, input_ligand_path, input_receptor_path, output_sdf_path,
                 input_box_path=None, input_autobox_path=None,
                 output_summary_path=None, output_log_path=None,
                 properties=None, **kwargs) -> None:
        properties = properties or {}

        # Call parent class constructor
        super().__init__(properties)
        self.locals_var_dict = locals().copy()

        # Input/Output files
        self.io_dict = {
            "in": {
                "input_ligand_path": input_ligand_path,
                "input_receptor_path": input_receptor_path,
                "input_box_path": input_box_path,
                "input_autobox_path": input_autobox_path
            },
            "out": {
                "output_sdf_path": output_sdf_path,
                "output_summary_path": output_summary_path,
                "output_log_path": output_log_path
            }
        }

        # Properties specific for BB
        self.cpu = properties.get('cpu', 1)
        self.exhaustiveness = properties.get('exhaustiveness', 8)
        self.num_modes = properties.get('num_modes', 9)
        self.min_rmsd_filter = properties.get('min_rmsd_filter', 1.0)
        self.num_mc_saved = properties.get('num_mc_saved', None)
        self.seed = properties.get('seed', None)
        self.scoring = properties.get('scoring', None)
        self.cnn_scoring = properties.get('cnn_scoring', None)
        self.cnn = properties.get('cnn', None)
        self.pose_sort_order = properties.get('pose_sort_order', None)
        self.autobox_add = properties.get('autobox_add', None)
        self.autobox_extend = properties.get('autobox_extend', None)
        self.minimize = properties.get('minimize', False)
        self.score_only = properties.get('score_only', False)
        self.local_only = properties.get('local_only', False)
        self.no_gpu = properties.get('no_gpu', False)
        self.device = properties.get('device', None)
        self.quiet = properties.get('quiet', False)
        self.binary_path = properties.get('binary_path', 'gnina')
        self.properties = properties

        # Check the properties
        self.check_properties(properties)
        self.check_arguments()

    def check_data_params(self, out_log, err_log):
        """ Checks all the input/output paths and parameters """
        self.io_dict["in"]["input_ligand_path"] = check_input_path(self.io_dict["in"]["input_ligand_path"], "input_ligand_path", out_log, self.__class__.__name__)
        self.io_dict["in"]["input_receptor_path"] = check_input_path(self.io_dict["in"]["input_receptor_path"], "input_receptor_path", out_log, self.__class__.__name__)
        self.io_dict["out"]["output_sdf_path"] = check_output_path(self.io_dict["out"]["output_sdf_path"], "output_sdf_path", False, out_log, self.__class__.__name__)
        self.io_dict["out"]["output_summary_path"] = check_output_path(self.io_dict["out"]["output_summary_path"], "output_summary_path", True, out_log, self.__class__.__name__)
        self.io_dict["out"]["output_log_path"] = check_output_path(self.io_dict["out"]["output_log_path"], "output_log_path", True, out_log, self.__class__.__name__)

        # gnina needs a search space, given either as a box file or as a reference structure
        if bool(self.io_dict["in"]["input_box_path"]) == bool(self.io_dict["in"]["input_autobox_path"]):
            fu.log(self.__class__.__name__ + ': Provide exactly one of input_box_path or input_autobox_path to define the docking box, exiting', out_log)
            raise SystemExit(self.__class__.__name__ + ': Provide exactly one of input_box_path or input_autobox_path to define the docking box')

        if self.io_dict["in"]["input_box_path"]:
            self.io_dict["in"]["input_box_path"] = check_input_path(self.io_dict["in"]["input_box_path"], "input_box_path", out_log, self.__class__.__name__)
            # parse it now so an unusable box file is caught before any work is done
            self.calculate_box(self.io_dict["in"]["input_box_path"])
        else:
            self.io_dict["in"]["input_autobox_path"] = check_input_path(self.io_dict["in"]["input_autobox_path"], "input_autobox_path", out_log, self.__class__.__name__)

    def calculate_box(self, box_file_path):
        """ Reads the docking box out of the REMARK line written by the box building blocks

        Returns the box center and its edge lengths, as strings. SIZE is the
        full edge length of the box, which is what gnina expects in
        --size_x/y/z, so it is passed through unchanged.

        Does not log, as it is called both to validate the box file up front and
        to build the command line.
        """
        with open(box_file_path, "r") as box_file:
            for line in box_file:
                if line.startswith("REMARK BOX CENTER"):
                    fields = line.split()
                    center = [float(coord) for coord in fields[3:6]]
                    size = [float(side) for side in fields[-3:]]
                    return [str(coord) for coord in center], [str(side) for side in size]

        fu.log(self.__class__.__name__ + ': No REMARK BOX CENTER line found in %s, exiting' % box_file_path, self.out_log)
        raise SystemExit(self.__class__.__name__ + ': No REMARK BOX CENTER line found in %s' % box_file_path)

    def cmd_path(self, path):
        """ Renders a staged path the way gnina will see it

        Inside a container every staged file sits in the mounted volume, so a
        bare name is enough once the command has moved there. Locally the staged
        paths are already usable as they stand, which also keeps them correct
        when the sandbox is disabled or already the working directory.
        """
        if self.container_path:
            return str(PurePath(path).name)
        return str(path)

    def build_cmd(self) -> list:
        """ Builds the gnina command line out of the staged files and the properties

        Kept apart from :meth:`launch` so the command can be inspected without
        running gnina. Must be called after ``stage_files``.
        """
        if self.container_path:
            working_dir = self.container_volume_path if self.container_volume_path else "/data"
        else:
            working_dir = self.stage_io_dict.get("unique_dir", ".")

        cmd = ["cd", working_dir, ";",
               self.binary_path,
               "--receptor", self.cmd_path(self.stage_io_dict["in"]["input_receptor_path"]),
               "--ligand", self.cmd_path(self.stage_io_dict["in"]["input_ligand_path"]),
               "--out", self.cmd_path(self.stage_io_dict["out"]["output_sdf_path"])]

        # the box file is read here and never handed to gnina, so it is taken
        # from io_dict and not from the staged copy
        if self.io_dict["in"].get("input_box_path"):
            box_path = self.io_dict["in"]["input_box_path"]
            center, size = self.calculate_box(box_path)
            fu.log('Docking box center %s and edge lengths %s, read from %s' % (
                ' '.join('%.3f' % float(coord) for coord in center),
                ' '.join('%.3f' % float(side) for side in size),
                PurePath(box_path).name), self.out_log)
            cmd.extend(["--center_x", center[0], "--center_y", center[1], "--center_z", center[2],
                        "--size_x", size[0], "--size_y", size[1], "--size_z", size[2]])
        else:
            # gnina opens the reference structure, so this one must be the staged copy
            cmd.extend(["--autobox_ligand", self.cmd_path(self.stage_io_dict["in"]["input_autobox_path"])])
            if self.autobox_add is not None:
                cmd.extend(["--autobox_add", str(self.autobox_add)])
            if self.autobox_extend is not None:
                cmd.extend(["--autobox_extend", "1" if self.autobox_extend else "0"])

        # optional outputs are absent from stage_io_dict when they were not requested
        if self.stage_io_dict["out"].get("output_log_path"):
            cmd.extend(["--log", self.cmd_path(self.stage_io_dict["out"]["output_log_path"])])

        for flag, prop in self.VALUE_FLAGS:
            value = getattr(self, prop)
            if value is not None:
                cmd.extend([flag, str(value)])

        for flag, prop in self.SWITCH_FLAGS:
            if getattr(self, prop):
                cmd.append(flag)

        return cmd

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`GninaRun <gnina.gnina_run.GninaRun>` gnina.gnina_run.GninaRun object."""

        # check input/output paths and parameters
        self.check_data_params(self.out_log, self.err_log)

        # Setup Biobb
        if self.check_restart():
            return 0
        self.stage_files()

        # create cmd
        self.cmd = self.build_cmd()

        fu.log('Executing gnina', self.out_log, self.global_log)

        # Run Biobb block
        self.run_biobb()

        # Copy files to host
        self.copy_to_host()

        # remove temporary folder(s)
        self.remove_tmp_files()

        if self.return_code == 0:
            if self.io_dict["out"].get("output_summary_path"):
                process_output_gnina(self.io_dict["out"]["output_sdf_path"],
                                     self.io_dict["out"]["output_summary_path"],
                                     self.out_log,
                                     self.__class__.__name__)
        else:
            fu.log('gnina ended with return code %s, no summary was generated' % self.return_code, self.out_log, self.global_log)

        self.check_arguments(output_files_created=True, raise_exception=False)

        return self.return_code


def gnina_run(input_ligand_path: str, input_receptor_path: str, output_sdf_path: str,
              input_box_path: Optional[str] = None, input_autobox_path: Optional[str] = None,
              output_summary_path: Optional[str] = None, output_log_path: Optional[str] = None,
              properties: Optional[dict] = None, **kwargs) -> int:
    """Create the :class:`GninaRun <gnina.gnina_run.GninaRun>` class and
    execute the :meth:`launch() <gnina.gnina_run.GninaRun.launch>` method."""
    return GninaRun(**dict(locals())).launch()


gnina_run.__doc__ = GninaRun.__doc__
main = GninaRun.get_main(gnina_run, "Performs docking of a ligand to a receptor with CNN rescoring via the gnina software.")


if __name__ == '__main__':
    main()
