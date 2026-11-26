#!/usr/bin/env python3

"""Module containing the FPocketRun class and the command line interface."""
from typing import Optional
import shutil
from pathlib import PurePath
from biobb_common.generic.biobb_object import BiobbObject, launcher
from biobb_common.tools import file_utils as fu
from biobb_vs.fpocket.common import process_output_fpocket


class FPocketRun(BiobbObject):
    """
    | biobb_vs FPocketRun
    | Wrapper of the fpocket software.
    | Finds the binding site of the input_pdb_path file via the `fpocket <https://github.com/Discngine/fpocket>`_ software.

    Args:
        input_pdb_path (str): Path to the PDB structure where the binding site is to be found. File type: input. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/fpocket/fpocket_input.pdb>`_. Accepted formats: pdb (edam:format_1476).
        output_pockets_zip (str): Path to all the pockets found by fpocket in the input_pdb_path structure. File type: output. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/fpocket/ref_output_pockets.zip>`_. Accepted formats: zip (edam:format_3987).
        output_summary (str): Path to the JSON summary file. File type: output. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/fpocket/ref_output_summary.json>`_. Accepted formats: json (edam:format_3464).
        properties (dic - Python dictionary object containing the tool parameters, not input/output files):
            * **min_radius** (*float*) - (None) [0.1~1000|0.1] The minimum radius in Ångstroms an alpha sphere might have in a binding pocket.
            * **max_radius** (*float*) - (None) [2~1000|0.1] The maximum radius in Ångstroms of alpha spheres in a pocket.
            * **num_spheres** (*int*) - (None) [1~1000|1] Indicates how many alpha spheres a pocket must contain at least in order to figure in the results.
            * **sort_by** (*str*) - ('druggability_score') From which property the output will be sorted. Values: druggability_score (this score intends to assess the likeliness of the pocket to bind a small drug like molecule), score (fpocket score as defined in the `fpocket paper <https://doi.org/10.1186/1471-2105-10-168>`_), volume (volume of the pocket).
            * **binary_path** (*string*) - ('fpocket') path to fpocket in your local computer.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.
            * **sandbox_path** (*str*) - ("./") [WF property] Parent path to the sandbox directory.
            * **container_path** (*str*) - (None) Container path definition.
            * **container_image** (*str*) - ('fpocket/fpocket:latest') Container image definition.
            * **container_volume_path** (*str*) - ('/tmp') Container volume path definition.
            * **container_user_id** (*str*) - (None) Container user_id definition.
            * **container_shell_path** (*str*) - ('/bin/bash') Path to default shell inside the container.

    Examples:
        This is a use example of how to use the building block from Python::

            from biobb_vs.fpocket.fpocket_run import fpocket_run
            prop = {
                'min_radius': 3,
                'max_radius': 6,
                'num_spheres': 35,
                'sort_by': 'druggability_score'
            }
            fpocket_run(input_pdb_path='/path/to/myStructure.pdb',
                    output_pockets_zip='/path/to/newPockets.zip',
                    output_summary='/path/to/newSummary.json',
                    properties=prop)

    Info:
        * wrapped_software:
            * name: fpocket
            * version: ==4.1
            * license: MIT
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl

    """

    def __init__(self, input_pdb_path: str, output_pockets_zip: str, output_summary: str,
                 properties: Optional[dict] = None, **kwargs) -> None:
        super().__init__(**locals())

    def run(self) -> None:
        """Execute the :class:`FPocketRun <fpocket.fpocket_run.FPocketRun>` fpocket.fpocket_run.FPocketRun object."""

        # fpocket writes its outputs in input_out, next to its input: a folder of the sandbox
        tmp_folder = self.create_tmp_dir(log=True)
        tmp_input = str(PurePath(tmp_folder).joinpath('input.pdb'))
        shutil.copy(self.sandbox_file("input_pdb_path"), tmp_input)

        # create cmd
        self.cmd = [self.binary_path,
                    '-f', self.staged_path(tmp_input)]

        # adding extra properties
        if self.min_radius:
            self.cmd.extend(['-m', str(self.min_radius)])

        if self.max_radius:
            self.cmd.extend(['-M', str(self.max_radius)])

        if self.num_spheres:
            self.cmd.extend(['-i', str(self.num_spheres)])

        fu.log('Executing fpocket', self.out_log, self.global_log)

        # Run Biobb block
        self.run_biobb()

        # Write the output pockets zip and the output summary from the folder written by fpocket.
        process_output_fpocket(tmp_folder,
                               self.sandbox_file("output_pockets_zip"),
                               self.sandbox_file("output_summary"),
                               self.sort_by,
                               self.remove_tmp,
                               self.out_log,
                               self.__class__.__name__)


fpocket_run = launcher(FPocketRun)


if __name__ == '__main__':
    FPocketRun.main()
