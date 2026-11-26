#!/usr/bin/env python3

"""Module containing the FPocketSelect class and the command line interface."""
from typing import Optional
import shutil
from pathlib import PurePath
from biobb_common.generic.biobb_object import BiobbObject, launcher
from biobb_common.tools import file_utils as fu


class FPocketSelect(BiobbObject):
    """
    | biobb_vs FPocketSelect
    | Selects a single pocket in the outputs of the fpocket building block.
    | Selects a single pocket in the outputs of the fpocket building block from a given parameter.

    Args:
        input_pockets_zip (str): Path to the pockets found by fpocket. File type: input. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/fpocket/input_pockets.zip>`_. Accepted formats: zip (edam:format_3987).
        output_pocket_pdb (str): Path to the PDB file with the cavity found by fpocket. File type: output. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/fpocket/ref_output_pocket.pdb>`_. Accepted formats: pdb (edam:format_1476).
        output_pocket_pqr (str): Path to the PQR file with the pocket found by fpocket. File type: output. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/fpocket/ref_output_pocket.pqr>`_. Accepted formats: pqr (edam:format_1476).
        properties (dic - Python dictionary object containing the tool parameters, not input/output files):
            * **pocket** (*int*) - (None) [1~1000|1] Pocket id from the summary json given by the fpocket building block.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.
            * **sandbox_path** (*str*) - ("./") [WF property] Parent path to the sandbox directory.

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

    def __init__(self, input_pockets_zip: str, output_pocket_pdb: str, output_pocket_pqr: str,
                 properties: Optional[dict] = None, **kwargs) -> None:
        super().__init__(**locals())

    def stage_files(self) -> None:
        """The block does not use the sandbox: there are no files to stage."""

    def run(self) -> None:
        """Execute the :class:`FPocketSelect <fpocket.fpocket_select.FPocketSelect>` fpocket.fpocket_select.FPocketSelect object."""

        # create tmp_folder
        tmp_folder = self.create_tmp_dir(log=True)

        # decompress the input_pockets_zip file to tmp_folder
        all_pockets = fu.unzip_list(zip_file=self.io_dict["in"]["input_pockets_zip"], dest_dir=tmp_folder, out_log=self.out_log)

        pockets_list = [i for i in all_pockets if ('pocket' + str(self.pocket)) in i]

        for p in pockets_list:
            if PurePath(p).suffix == '.pdb':
                fu.log('Saving %s file' % self.io_dict["out"]["output_pocket_pdb"], self.out_log)
                shutil.copy(p, self.io_dict["out"]["output_pocket_pdb"])
            else:
                fu.log('Saving %s file' % self.io_dict["out"]["output_pocket_pqr"], self.out_log)
                shutil.copy(p, self.io_dict["out"]["output_pocket_pqr"])


fpocket_select = launcher(FPocketSelect)


if __name__ == '__main__':
    FPocketSelect.main()
