#!/usr/bin/env python3

"""Module containing the AutoDockVinaRun class and the command line interface."""
import os
from typing import Optional
from biobb_common.generic.biobb_object import BiobbObject, launcher


class AutoDockVinaRun(BiobbObject):
    """
    | biobb_vs AutoDockVinaRun
    | Wrapper of the AutoDock Vina software.
    | This class performs docking of the ligand to a set of grids describing the target protein via the `AutoDock Vina <http://vina.scripps.edu/index.html>`_ software.

    Args:
        input_ligand_pdbqt_path (str): Path to the input PDBQT ligand. File type: input. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/vina/vina_ligand.pdbqt>`_. Accepted formats: pdbqt (edam:format_1476).
        input_receptor_pdbqt_path (str): Path to the input PDBQT receptor. File type: input. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/vina/vina_receptor.pdbqt>`_. Accepted formats: pdbqt (edam:format_1476).
        input_box_path (str): Path to the PDB containig the residues belonging to the binding site. File type: input. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/vina/vina_box.pdb>`_. Accepted formats: pdb (edam:format_1476).
        output_pdbqt_path (str): Path to the output PDBQT file. File type: output. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/vina/ref_output_vina.pdbqt>`_. Accepted formats: pdbqt (edam:format_1476).
        output_log_path (str) (Optional): Path to the log file. File type: output. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/vina/ref_output_vina.log>`_. Accepted formats: log (edam:format_2330).
        properties (dic - Python dictionary object containing the tool parameters, not input/output files):
            * **cpu** (*int*) - (1) [1~1000|1] the number of CPUs to use.
            * **exhaustiveness** (*int*) - (8) [1~10000|1] exhaustiveness of the global search (roughly proportional to time).
            * **num_modes** (*int*) - (9) [1~1000|1] maximum number of binding modes to generate.
            * **min_rmsd** (*int*) - (1) [1~1000|1] minimum RMSD between output poses.
            * **energy_range** (*int*) - (3) [1~1000|1] maximum energy difference between the best binding mode and the worst one displayed (kcal/mol).
            * **binary_path** (*string*) - ('vina') path to vina in your local computer.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.
            * **sandbox_path** (*str*) - ("./") [WF property] Parent path to the sandbox directory.
            * **container_path** (*str*) - (None) Container path definition.
            * **container_image** (*str*) - ('biocontainers/autodock-vina:v1.1.2-5b1-deb_cv1') Container image definition.
            * **container_volume_path** (*str*) - ('/tmp') Container volume path definition.
            * **container_user_id** (*str*) - (None) Container user_id definition.
            * **container_shell_path** (*str*) - ('/bin/bash') Path to default shell inside the container.

    Examples:
        This is a use example of how to use the building block from Python::

            from biobb_vs.vina.autodock_vina_run import autodock_vina_run
            prop = {
                'binary_path': 'vina'
            }
            autodock_vina_run(input_ligand_pdbqt_path='/path/to/myLigand.pdbqt',
                            input_receptor_pdbqt_path='/path/to/myReceptor.pdbqt',
                            input_box_path='/path/to/myBox.pdb',
                            output_pdbqt_path='/path/to/newStructure.pdbqt',
                            output_log_path='/path/to/newLog.log',
                            properties=prop)

    Info:
        * wrapped_software:
            * name: Autodock Vina
            * version: >=1.2.3
            * license: Apache-2.0
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl

    """

    def __init__(
        self,
        input_ligand_pdbqt_path: str,
        input_receptor_pdbqt_path: str,
        input_box_path: str,
        output_pdbqt_path: str,
        output_log_path: Optional[str] = None,
        properties: Optional[dict] = None,
        **kwargs,
    ) -> None:
        super().__init__(**locals())

    def calculate_box(self, box_file_path):
        """Read the box center and the box edge lengths from the REMARK line of a box PDB file.

        The SIZE field is the full edge length of the box, matching what AutoDock Vina
        expects in --size_x/y/z.
        """
        with open(box_file_path, "r") as box_file:
            for line in box_file:
                line = line.rstrip(os.linesep)
                if line.startswith("REMARK BOX CENTER"):
                    fields = line.split()
                    center = fields[3:6]
                    size = fields[-3:]
                    return list(
                        map(
                            str,
                            [
                                center[0],
                                center[1],
                                center[2],
                                size[0],
                                size[1],
                                size[2],
                            ],
                        )
                    )
        raise SystemExit(
            "No 'REMARK BOX CENTER' line found in the input box file: %s"
            % (box_file_path)
        )

    def run(self) -> None:
        """Execute the :class:`AutoDockVinaRun_run <vina.autodock_vina_run.AutoDockVinaRun_run>` vina.autodock_vina_run.AutoDockVinaRun_run object."""

        # calculating box position and size
        x0, y0, z0, sidex, sidey, sidez = self.calculate_box(
            self.io_dict["in"]["input_box_path"]
        )

        # create cmd
        self.cmd = [
            self.binary_path,
            "--ligand",
            self.stage_io_dict["in"]["input_ligand_pdbqt_path"],
            "--receptor",
            self.stage_io_dict["in"]["input_receptor_pdbqt_path"],
            "--center_x=" + x0,
            "--center_y=" + y0,
            "--center_z=" + z0,
            "--size_x=" + sidex,
            "--size_y=" + sidey,
            "--size_z=" + sidez,
            "--cpu",
            str(self.cpu),
            "--exhaustiveness",
            str(self.exhaustiveness),
            "--num_modes",
            str(self.num_modes),
            "--min_rmsd",
            str(self.min_rmsd),
            "--energy_range",
            str(self.energy_range),
            "--out",
            self.stage_io_dict["out"]["output_pdbqt_path"],
            "--verbosity",
            "1",
        ]
        if self.stage_io_dict["out"].get("output_log_path"):
            self.cmd.extend([">", self.stage_io_dict["out"]["output_log_path"]])

        # Run Biobb block
        self.run_biobb()


autodock_vina_run = launcher(AutoDockVinaRun)


if __name__ == "__main__":
    AutoDockVinaRun.main()
