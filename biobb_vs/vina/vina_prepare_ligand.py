#!/usr/bin/env python3

"""Module containing the VinaPrepareLigand class and the command line interface."""
import argparse
import os
import shutil
from biobb_common.configuration import  settings
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger
from biobb_common.command_wrapper import cmd_wrapper
from biobb_vs.vina.common import *

class VinaPrepareLigand():
    """Prepares input ligand for an Autodock Vina Virtual Screening.
    Wrapper of the prepare_ligand4.py module
    Visit the `AutoDock official website <http://autodock.scripps.edu/faqs-help/how-to/how-to-prepare-a-ligand-file-for-autodock4>`_. 

    Args:
        input_ligand_path (str): Path to the input PDB ligand. File type: input. `Sample file <>`_. Accepted formats: pdb.
        output_ligand_path (str): Path to the output PDBQT ligand. File type: output. `Sample file <>`_. Accepted formats: pdbqt.
        properties (dic):
            * **mgltools_path** (*string*) - ('mgltools') path to mgltools in your local computer (MGLTools are usually in the pkgs/ folder of the anaconda folder).
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.
    """

    def __init__(self, input_ligand_path,
                 output_ligand_path, properties=None, **kwargs) -> None:
        properties = properties or {}

        # Input/Output files
        self.io_dict = { 
            "in": { "input_ligand_path": input_ligand_path }, 
            "out": { "output_ligand_path": output_ligand_path } 
        }

        # Properties specific for BB
        self.mgltools_path = properties.get('mgltools_path', 'mgltools')
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
        self.io_dict["in"]["input_ligand_path"] = check_input_path(self.io_dict["in"]["input_ligand_path"], "input_ligand_path", out_log, self.__class__.__name__)
        self.io_dict["out"]["output_ligand_path"] = check_output_path(self.io_dict["out"]["output_ligand_path"],"output_ligand_path", False, out_log, self.__class__.__name__)

        self.mgltools_path = check_mgltools_path(self.mgltools_path, out_log, self.__class__.__name__)

    @launchlogger
    def launch(self) -> int:
        """Launches the execution of the VinaPrepareLigand module."""

        # Get local loggers from launchlogger decorator
        out_log = getattr(self, 'out_log', None)
        err_log = getattr(self, 'err_log', None)

        # check input/output paths and parameters
        self.check_data_params(out_log, err_log)

        # Check the properties
        fu.check_properties(self, self.properties)

        if self.restart:
            output_file_list = [self.io_dict["out"]["output_ligand_path"]]
            if fu.check_complete_files(output_file_list):
                fu.log('Restart is enabled, this step: %s will the skipped' % self.step, out_log, self.global_log)
                return 0

        # gets executor and script paths
        self.executor_path = str(PurePath(self.mgltools_path).joinpath('bin', 'pythonsh'))
        self.script_path = str(PurePath(self.mgltools_path).joinpath('MGLToolsPckgs', 'AutoDockTools', 'Utilities24', 'prepare_ligand4.py'))

        # move execution to temporary folder
        unique_dir = PurePath(fu.create_unique_dir())
        fu.log('Creating %s temporary folder' % unique_dir, out_log, self.global_log)
        shutil.copy2(self.io_dict["in"]["input_ligand_path"], unique_dir)
        cwd = Path.cwd()
        os.chdir(unique_dir)

        # create cmd
        self.input = PurePath(self.io_dict["in"]["input_ligand_path"]).name
        self.output = PurePath(self.io_dict["out"]["output_ligand_path"]).name

        cmd = [self.executor_path, self.script_path,
               '-l', self.input ,
               '-A bonds_hydrogens',
               '-o', self.output]

        fu.log('Executing in %s temporary folder' % unique_dir, out_log, self.global_log)
        cmd = fu.create_cmd_line(cmd, out_log=out_log, global_log=self.global_log)
        returncode = cmd_wrapper.CmdWrapper(cmd, out_log, err_log, self.global_log).launch()

        os.chdir(cwd)

        # copy output from temporary folder to output path
        shutil.copy2(PurePath(unique_dir).joinpath(self.output), PurePath(self.io_dict["out"]["output_ligand_path"]).parent)

        fu.log('Saving %s output file' % self.io_dict["out"]["output_ligand_path"], out_log, self.global_log)

        if self.remove_tmp:
            # remove temporary folder
            fu.rm(unique_dir)
            fu.log('Removed temporary folder: %s' % unique_dir, out_log)

        return returncode

def main():
    parser = argparse.ArgumentParser(description="Prepares input ligand for an Autodock Vina Virtual Screening.", formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('--config', required=False, help='Configuration file')

    # Specific args of each building block
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--input_ligand_path', required=True, help='Path to the input PDB ligand. Accepted formats: pdb.')
    required_args.add_argument('--output_ligand_path', required=True, help='Path to the output PDBQT ligand. Accepted formats: pdbqt.')

    args = parser.parse_args()
    args.config = args.config or "{}"
    properties = settings.ConfReader(config=args.config).get_prop_dic()

    # Specific call of each building block
    VinaPrepareLigand(input_ligand_path=args.input_ligand_path,
                   output_ligand_path=args.output_ligand_path, 
                   properties=properties).launch()

if __name__ == '__main__':
    main()

