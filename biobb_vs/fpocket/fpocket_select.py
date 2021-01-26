#!/usr/bin/env python3

"""Module containing the FPocketSelect class and the command line interface."""
import argparse
import os
from biobb_common.configuration import  settings
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger
from biobb_common.command_wrapper import cmd_wrapper
from biobb_vs.fpocket.common import *

class FPocketSelect():
    """
    | biobb_vs FPocketSelect
    | Selects a single pocket in the outputs of the fpocket building block.
    | Selects a single pocket in the outputs of the fpocket building block from a given parameter.

    Args:
        input_pockets_zip (str): Path to the pockets found by fpocket. File type: input. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/fpocket/input_pockets.zip>`_. Accepted formats: zip (edam:format_3987).
        output_pocket_pdb (str): Path to the PDB file with the cavity found by fpocket. File type: output. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/fpocket/ref_output_pocket.pdb>`_. Accepted formats: pdb (edam:format_1476).
        output_pocket_pqr (str): Path to the PQR file with the pocket found by fpocket. File type: output. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/fpocket/ref_output_pocket.pqr>`_. Accepted formats: pqr (edam:format_1476).
        properties (dic - Python dictionary object containing the tool parameters, not input/output files):
            * **pocket** (*int*) - (1) [1~1000|1] Pocket id from the summary json given by the fpocket building block.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.

    Examples:
        This is a use example of how to use the building block from Python::

            from biobb_vs.fpocket.fpocket_select import fpocket_select
            prop = { 
                'pocket': 2
            }
            fpocket_select(input_pockets_zip='/path/to/myPockets.zip', 
                    output_pocket_pdb='/path/to/myCavity.pdb', 
                    output_pocket_pqr='/path/to/myPocket.pqr', 
                    properties=prop)

    Info:
        * wrapped_software:
            * name: In house
            * license: Apache-2.0
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl

    """

    def __init__(self, input_pockets_zip, output_pocket_pdb, output_pocket_pqr, 
                properties=None, **kwargs) -> None:
        properties = properties or {}

        # Input/Output files
        self.io_dict = { 
            "in": { "input_pockets_zip": input_pockets_zip }, 
            "out": { "output_pocket_pdb": output_pocket_pdb, "output_pocket_pqr": output_pocket_pqr } 
        }

        # Properties specific for BB
        self.pocket = properties.get('pocket', None)
        self.properties = properties

        # Properties common in all BB
        self.can_write_console_log = properties.get('can_write_console_log', True)
        self.global_log = properties.get('global_log', None)
        self.prefix = properties.get('prefix', None)
        self.step = properties.get('step', None)
        self.path = properties.get('path', '')
        self.remove_tmp = properties.get('remove_tmp', True)
        self.restart = properties.get('restart', False)

    def check_data_params(self, out_log, err_log):
        """ Checks all the input/output paths and parameters """
        self.io_dict["in"]["input_pockets_zip"] = check_input_path(self.io_dict["in"]["input_pockets_zip"], "input_pockets_zip", out_log, self.__class__.__name__)
        self.io_dict["out"]["output_pocket_pdb"] = check_output_path(self.io_dict["out"]["output_pocket_pdb"],"output_pocket_pdb", False, out_log, self.__class__.__name__)
        self.io_dict["out"]["output_pocket_pqr"] = check_output_path(self.io_dict["out"]["output_pocket_pqr"],"output_pocket_pqr", True, out_log, self.__class__.__name__)

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`FPocketSelect <fpocket.fpocket_select.FPocketSelect>` fpocket.fpocket_select.FPocketSelect object."""

        # Get local loggers from launchlogger decorator
        out_log = getattr(self, 'out_log', None)
        err_log = getattr(self, 'err_log', None)

        # check input/output paths and parameters
        self.check_data_params(out_log, err_log)

        # Check the properties
        fu.check_properties(self, self.properties)

        if self.restart:
            output_file_list = [self.io_dict["out"]["output_pocket_pdb"], self.io_dict["out"]["output_pocket_pqr"]]
            if fu.check_complete_files(output_file_list):
                fu.log('Restart is enabled, this step: %s will the skipped' % self.step, out_log, self.global_log)
                return 0

        # create tmp_folder
        self.tmp_folder = fu.create_unique_dir()
        fu.log('Creating %s temporary folder' % self.tmp_folder, out_log)

        # decompress the input_pockets_zip file to tmp_folder
        all_pockets = fu.unzip_list(zip_file = self.io_dict["in"]["input_pockets_zip"], dest_dir = self.tmp_folder, out_log = out_log)

        pockets_list = [i for i in all_pockets if ('pocket' + str(self.pocket)) in i]

        for p in pockets_list:
            if PurePath(p).suffix == '.pdb':
                fu.log('Saving %s file' % self.io_dict["out"]["output_pocket_pdb"], out_log)
                shutil.copy(p, self.io_dict["out"]["output_pocket_pdb"])
            else:
                fu.log('Saving %s file' % self.io_dict["out"]["output_pocket_pqr"], out_log)
                shutil.copy(p, self.io_dict["out"]["output_pocket_pqr"])

        if self.remove_tmp:
            # remove temporary folder
            fu.rm(self.tmp_folder)
            fu.log('Removed temporary folder: %s' % self.tmp_folder, out_log)

        return 0

def fpocket_select(input_pockets_zip: str, output_pocket_pdb: str, output_pocket_pqr:str, properties: dict = None, **kwargs) -> int:
    """Execute the :class:`FPocketSelect <fpocket.fpocket_select.FPocketSelect>` class and
    execute the :meth:`launch() <fpocket.fpocket_select.FPocketSelect.launch>` method."""

    return FPocketSelect(input_pockets_zip=input_pockets_zip,
                output_pocket_pdb=output_pocket_pdb,
                output_pocket_pqr=output_pocket_pqr,
                properties=properties, **kwargs).launch()

def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(description="Selects a single pocket in the outputs of the fpocket building block from a given parameter.", formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('--config', required=False, help='Configuration file')

    # Specific args of each building block
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--input_pockets_zip', required=True, help='Path to all the pockets found by fpocket. Accepted formats: zip.')
    required_args.add_argument('--output_pocket_pdb', required=True, help='Path to the PDB file with the cavity found by fpocket. Accepted formats: pdb.')
    required_args.add_argument('--output_pocket_pqr', required=True, help='Path to the PQR file with the pocket found by fpocket. Accepted formats: pqr.')

    args = parser.parse_args()
    args.config = args.config or "{}"
    properties = settings.ConfReader(config=args.config).get_prop_dic()

    # Specific call of each building block
    fpocket_select(input_pockets_zip=args.input_pockets_zip, 
                    output_pocket_pdb=args.output_pocket_pdb, 
                    output_pocket_pqr=args.output_pocket_pqr, 
                    properties=properties)

if __name__ == '__main__':
    main()
