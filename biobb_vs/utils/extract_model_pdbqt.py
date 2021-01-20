#!/usr/bin/env python3

"""Module containing the ExtractModelPDBQT class and the command line interface."""
import argparse
from biobb_common.configuration import  settings
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger
from biobb_common.command_wrapper import cmd_wrapper
from biobb_vs.utils.common import *

class ExtractModelPDBQT():
    """
    | biobb_vs ExtractModelPDBQT
    | Extracts a model from a PDBQT file with several models.

    Args:
        input_pdbqt_path (str): Input PDBQT file. File type: input. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/utils/models.pdbqt>`_. Accepted formats: pdbqt (edam:format_1476).
        output_pdbqt_path (str): Output PDBQT file. File type: output. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/utils/ref_extract_model.pdbqt>`_. Accepted formats: pdbqt (edam:format_1476).
        properties (dic - Python dictionary object containing the tool parameters, not input/output files):
            * **model** (*int*) - (1) [0~1000|1] Model number to extract from input_pdbqt_path.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.

    Examples:
        This is a use example of how to use the building block from Python::

            from biobb_vs.utils.extract_model_pdbqt import extract_model_pdbqt
            prop = { 
                'model': 1
            }
            extract_model_pdbqt(input_pdbqt_path='/path/to/myStructure.pdbqt', 
                                output_pdbqt_path='/path/to/newStructure.pdbqt', 
                                properties=prop)

    Info:
        * wrapped_software:
            * name: In house using Biopython
            * version: >=1.76
            * license: Apache-2.0
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl

    """

    def __init__(self, input_pdbqt_path, output_pdbqt_path, 
                properties=None, **kwargs) -> None:
        properties = properties or {}

        # Input/Output files
        self.io_dict = { 
            "in": { "input_pdbqt_path": input_pdbqt_path },
            "out": { "output_pdbqt_path": output_pdbqt_path } 
        }

        # Properties specific for BB
        self.model = properties.get('model', 1)
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
        self.io_dict["in"]["input_pdbqt_path"] = check_input_path(self.io_dict["in"]["input_pdbqt_path"],"input_pdbqt_path", out_log, self.__class__.__name__)
        self.io_dict["out"]["output_pdbqt_path"] = check_output_path(self.io_dict["out"]["output_pdbqt_path"],"output_pdbqt_path", False, out_log, self.__class__.__name__)

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`ExtractModelPDBQT <utils.extract_model_pdbqt.ExtractModelPDBQT>` utils.extract_model_pdbqt.ExtractModelPDBQT object."""

        # Get local loggers from launchlogger decorator
        out_log = getattr(self, 'out_log', None)
        err_log = getattr(self, 'err_log', None)

        # check input/output paths and parameters
        self.check_data_params(out_log, err_log)

        # Check the properties
        fu.check_properties(self, self.properties)

        if self.restart:
            output_file_list = [self.io_dict["out"]["output_pdbqt_path"]]
            if fu.check_complete_files(output_file_list):
                fu.log('Restart is enabled, this step: %s will the skipped' % self.step, out_log, self.global_log)
                return 0

        structure_name = PurePath(self.io_dict["in"]["input_pdbqt_path"]).name
        parser      = Bio.PDB.PDBParser(QUIET = True)
        structPDB   = parser.get_structure(structure_name, self.io_dict["in"]["input_pdbqt_path"])

        models = []
        for model in structPDB.get_models():
            models.append(model.id + 1)

        if not self.model in models:
            fu.log(self.__class__.__name__ + ': Selected model %d not found in %s structure.' % (self.model, self.io_dict["in"]["input_pdbqt_path"]), out_log)
            raise SystemExit(self.__class__.__name__ + ': Selected model %d not found in %s structure.' % (self.model, self.io_dict["in"]["input_pdbqt_path"]))

        save = False
        lines = 0
        with open(self.io_dict["in"]["input_pdbqt_path"], "r") as input_pdb, open(self.io_dict["out"]["output_pdbqt_path"], "w") as output_pdb:
            for line in input_pdb:
                if line.startswith('MODEL') and line.split()[1] == str(self.model):
                    save = True
                if line.startswith('ENDMDL'):
                    save = False
                if save and not line.startswith('MODEL'):
                    lines = lines + 1
                    output_pdb.write(line)
                
        fu.log('Saving model %d to %s' % (self.model, self.io_dict["out"]["output_pdbqt_path"]), out_log)

        return 0

def extract_model_pdbqt(input_pdbqt_path: str, output_pdbqt_path: str, properties: dict = None, **kwargs) -> int:
    """Execute the :class:`ExtractModelPDBQT <utils.extract_model_pdbqt.ExtractModelPDBQT>` class and
    execute the :meth:`launch() <utils.extract_model_pdbqt.ExtractModelPDBQT.launch>` method."""

    return ExtractModelPDBQT(input_pdbqt_path=input_pdbqt_path,
                            output_pdbqt_path=output_pdbqt_path,
                            properties=properties, **kwargs).launch()

def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(description="Extracts a model from a PDBQT file with several models.", formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('--config', required=False, help='Configuration file')

    # Specific args of each building block
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--input_pdbqt_path', required=True, help='Input PDBQT file. Accepted formats: pdbqt.')
    required_args.add_argument('--output_pdbqt_path', required=True, help='Output PDBQT file. Accepted formats: pdbqt.')

    args = parser.parse_args()
    args.config = args.config or "{}"
    properties = settings.ConfReader(config=args.config).get_prop_dic()

    # Specific call of each building block
    extract_model_pdbqt(input_pdbqt_path=args.input_pdbqt_path, 
                        output_pdbqt_path=args.output_pdbqt_path, 
                        properties=properties)

if __name__ == '__main__':
    main()
