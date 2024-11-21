#!/usr/bin/env python3

"""Module containing the ExtractModelPDBQT class and the command line interface."""

import argparse
import warnings
from pathlib import PurePath
from typing import Optional

from Bio import BiopythonDeprecationWarning
from biobb_common.configuration import settings
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger

from biobb_vs.utils.common import check_input_path, check_output_path

with warnings.catch_warnings():
    warnings.simplefilter("ignore", BiopythonDeprecationWarning)
    # try:
    #    import Bio.SubsMat.MatrixInfo
    # except ImportError:
    import Bio.Align.substitution_matrices
    import Bio.pairwise2
    import Bio.PDB


class ExtractModelPDBQT(BiobbObject):
    """
    | biobb_vs ExtractModelPDBQT
    | Extracts a model from a PDBQT file with several models.
    | Extracts a model from a PDBQT file with several models. The model number to extract is defined by the user.

    Args:
        input_pdbqt_path (str): Input PDBQT file. File type: input. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/utils/models.pdbqt>`_. Accepted formats: pdbqt (edam:format_1476).
        output_pdbqt_path (str): Output PDBQT file. File type: output. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/utils/ref_extract_model.pdbqt>`_. Accepted formats: pdbqt (edam:format_1476).
        properties (dic - Python dictionary object containing the tool parameters, not input/output files):
            * **model** (*int*) - (1) [0~1000|1] Model number to extract from input_pdbqt_path.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.
            * **sandbox_path** (*str*) - ("./") [WF property] Parent path to the sandbox directory.

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

    def __init__(
        self, input_pdbqt_path, output_pdbqt_path, properties=None, **kwargs
    ) -> None:
        properties = properties or {}

        # Call parent class constructor
        super().__init__(properties)
        self.locals_var_dict = locals().copy()

        # Input/Output files
        self.io_dict = {
            "in": {"input_pdbqt_path": input_pdbqt_path},
            "out": {"output_pdbqt_path": output_pdbqt_path},
        }

        # Properties specific for BB
        self.model = properties.get("model", 1)
        self.properties = properties

        # Check the properties
        self.check_properties(properties)
        self.check_arguments()

    def check_data_params(self, out_log, err_log):
        """Checks all the input/output paths and parameters"""
        self.io_dict["in"]["input_pdbqt_path"] = check_input_path(
            self.io_dict["in"]["input_pdbqt_path"],
            "input_pdbqt_path",
            out_log,
            self.__class__.__name__,
        )
        self.io_dict["out"]["output_pdbqt_path"] = check_output_path(
            self.io_dict["out"]["output_pdbqt_path"],
            "output_pdbqt_path",
            False,
            out_log,
            self.__class__.__name__,
        )

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`ExtractModelPDBQT <utils.extract_model_pdbqt.ExtractModelPDBQT>` utils.extract_model_pdbqt.ExtractModelPDBQT object."""

        # check input/output paths and parameters
        self.check_data_params(self.out_log, self.err_log)

        # Setup Biobb
        if self.check_restart():
            return 0
        self.stage_files()

        if self.restart:
            output_file_list = [self.io_dict["out"]["output_pdbqt_path"]]
            if fu.check_complete_files(output_file_list):
                fu.log(
                    "Restart is enabled, this step: %s will the skipped" % self.step,
                    self.out_log,
                    self.global_log,
                )
                return 0

        structure_name = PurePath(self.io_dict["in"]["input_pdbqt_path"]).name
        parser = Bio.PDB.PDBParser(QUIET=True)
        structPDB = parser.get_structure(
            structure_name, self.io_dict["in"]["input_pdbqt_path"]
        )

        models = []
        for model in structPDB.get_models():
            models.append(model.id + 1)

        if self.model not in models:
            fu.log(
                self.__class__.__name__
                + ": Selected model %d not found in %s structure."
                % (self.model, self.io_dict["in"]["input_pdbqt_path"]),
                self.out_log,
            )
            raise SystemExit(
                self.__class__.__name__
                + ": Selected model %d not found in %s structure."
                % (self.model, self.io_dict["in"]["input_pdbqt_path"])
            )

        save = False
        lines = 0
        with open(self.io_dict["in"]["input_pdbqt_path"], "r") as input_pdb, open(
            self.io_dict["out"]["output_pdbqt_path"], "w"
        ) as output_pdb:
            for line in input_pdb:
                if line.startswith("MODEL") and line.split()[1] == str(self.model):
                    save = True
                if line.startswith("ENDMDL"):
                    save = False
                if save and not line.startswith("MODEL"):
                    lines = lines + 1
                    output_pdb.write(line)

        fu.log(
            "Saving model %d to %s"
            % (self.model, self.io_dict["out"]["output_pdbqt_path"]),
            self.out_log,
        )

        # Copy files to host
        self.copy_to_host()

        self.tmp_files.extend([self.stage_io_dict.get("unique_dir", "")])
        self.remove_tmp_files()

        self.check_arguments(output_files_created=True, raise_exception=False)

        return 0


def extract_model_pdbqt(
    input_pdbqt_path: str,
    output_pdbqt_path: str,
    properties: Optional[dict] = None,
    **kwargs,
) -> int:
    """Execute the :class:`ExtractModelPDBQT <utils.extract_model_pdbqt.ExtractModelPDBQT>` class and
    execute the :meth:`launch() <utils.extract_model_pdbqt.ExtractModelPDBQT.launch>` method."""

    return ExtractModelPDBQT(
        input_pdbqt_path=input_pdbqt_path,
        output_pdbqt_path=output_pdbqt_path,
        properties=properties,
        **kwargs,
    ).launch()


def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(
        description="Extracts a model from a PDBQT file with several models.",
        formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999),
    )
    parser.add_argument("--config", required=False, help="Configuration file")

    # Specific args of each building block
    required_args = parser.add_argument_group("required arguments")
    required_args.add_argument(
        "--input_pdbqt_path",
        required=True,
        help="Input PDBQT file. Accepted formats: pdbqt.",
    )
    required_args.add_argument(
        "--output_pdbqt_path",
        required=True,
        help="Output PDBQT file. Accepted formats: pdbqt.",
    )

    args = parser.parse_args()
    args.config = args.config or "{}"
    properties = settings.ConfReader(config=args.config).get_prop_dic()

    # Specific call of each building block
    extract_model_pdbqt(
        input_pdbqt_path=args.input_pdbqt_path,
        output_pdbqt_path=args.output_pdbqt_path,
        properties=properties,
    )


if __name__ == "__main__":
    main()
