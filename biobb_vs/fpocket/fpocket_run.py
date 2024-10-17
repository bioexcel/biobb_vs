#!/usr/bin/env python3

"""Module containing the FPocketRun class and the command line interface."""
import argparse
from typing import Optional
import shutil
from pathlib import PurePath
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.configuration import settings
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger
from biobb_vs.fpocket.common import check_input_path, check_output_path, process_output_fpocket


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
            * **container_working_dir** (*str*) - (None) Container working directory definition.
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

    def __init__(self, input_pdb_path, output_pockets_zip, output_summary,
                 properties=None, **kwargs) -> None:
        properties = properties or {}

        # Call parent class constructor
        super().__init__(properties)
        self.locals_var_dict = locals().copy()

        # Input/Output files
        self.io_dict = {
            "in": {"input_pdb_path": input_pdb_path},
            "out": {"output_pockets_zip": output_pockets_zip, "output_summary": output_summary}
        }

        # Properties specific for BB
        self.binary_path = properties.get('binary_path', 'fpocket')
        self.min_radius = properties.get('min_radius', None)
        self.max_radius = properties.get('max_radius', None)
        self.num_spheres = properties.get('num_spheres', None)
        self.sort_by = properties.get('sort_by', 'druggability_score')
        self.properties = properties

        # Check the properties
        self.check_properties(properties)
        self.check_arguments()

    def check_data_params(self, out_log, err_log):
        """ Checks all the input/output paths and parameters """
        self.io_dict["in"]["input_pdb_path"] = check_input_path(self.io_dict["in"]["input_pdb_path"], "input_pdb_path", out_log, self.__class__.__name__)
        self.io_dict["out"]["output_pockets_zip"] = check_output_path(self.io_dict["out"]["output_pockets_zip"], "output_pockets_zip", False, out_log, self.__class__.__name__)
        self.io_dict["out"]["output_summary"] = check_output_path(self.io_dict["out"]["output_summary"], "output_summary", True, out_log, self.__class__.__name__)

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`FPocketRun <fpocket.fpocket_run.FPocketRun>` fpocket.fpocket_run.FPocketRun object."""

        # check input/output paths and parameters
        self.check_data_params(self.out_log, self.err_log)

        # Setup Biobb
        if self.check_restart():
            return 0
        self.stage_files()

        if self.container_path:
            tmp_input = str(PurePath(self.container_volume_path).joinpath(PurePath(self.io_dict["in"]["input_pdb_path"]).name))
            self.tmp_folder = self.stage_io_dict['unique_dir']
        else:
            # create tmp_folder
            self.tmp_folder = fu.create_unique_dir()
            fu.log('Creating %s temporary folder' % self.tmp_folder, self.out_log)
            tmp_input = str(PurePath(self.tmp_folder).joinpath('input.pdb'))
            # copy input_pdb_path to tmp_folder
            shutil.copy(self.io_dict["in"]["input_pdb_path"], tmp_input)

        # create cmd
        self.cmd = [self.binary_path,
                    '-f', tmp_input]

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

        # Copy files to host
        self.copy_to_host()

        process_output_fpocket(self.tmp_folder,
                               self.io_dict["out"]["output_pockets_zip"],
                               self.io_dict["out"]["output_summary"],
                               self.sort_by,
                               self.remove_tmp,
                               self.container_path,
                               self.out_log,
                               self.__class__.__name__)

        self.tmp_files.extend([
            self.stage_io_dict.get("unique_dir", ""),
            self.tmp_folder
        ])
        self.remove_tmp_files()

        return self.return_code


def fpocket_run(input_pdb_path: str, output_pockets_zip: str, output_summary: str, properties: Optional[dict] = None, **kwargs) -> int:
    """Execute the :class:`FPocketRun <fpocket.fpocket_run.FPocketRun>` class and
    execute the :meth:`launch() <fpocket.fpocket_run.FPocketRun.launch>` method."""

    return FPocketRun(input_pdb_path=input_pdb_path,
                      output_pockets_zip=output_pockets_zip,
                      output_summary=output_summary,
                      properties=properties, **kwargs).launch()


def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(description="Finds the binding site of the input_pdb_path file via the fpocket software", formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('--config', required=False, help='Configuration file')

    # Specific args of each building block
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--input_pdb_path', required=True, help='Path to the PDB structure where the binding site is to be found. Accepted formats: pdb.')
    required_args.add_argument('--output_pockets_zip', required=True, help='Path to all the pockets found by fpocket in the input_pdb_path structure. Accepted formats: zip.')
    required_args.add_argument('--output_summary', required=True, help='Path to the JSON summary file. Accepted formats: json.')

    args = parser.parse_args()
    args.config = args.config or "{}"
    properties = settings.ConfReader(config=args.config).get_prop_dic()

    # Specific call of each building block
    fpocket_run(input_pdb_path=args.input_pdb_path,
                output_pockets_zip=args.output_pockets_zip,
                output_summary=args.output_summary,
                properties=properties)


if __name__ == '__main__':
    main()
