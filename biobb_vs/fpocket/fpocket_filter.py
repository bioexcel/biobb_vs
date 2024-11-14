#!/usr/bin/env python3

"""Module containing the FPocketFilter class and the command line interface."""

import argparse
import json
from typing import Optional

from biobb_common.configuration import settings
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger

from biobb_vs.fpocket.common import (
    check_input_path,
    check_output_path,
    check_range,
    process_output_fpocket_filter,
)
from biobb_vs.utils.common import _from_string_to_list


class FPocketFilter(BiobbObject):
    """
    | biobb_vs FPocketFilter
    | Performs a search over the outputs of the fpocket building block.
    | Finds one or more binding sites in the outputs of the fpocket building block from given parameters.

    Args:
        input_pockets_zip (str): Path to all the pockets found by fpocket. File type: input. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/fpocket/input_pockets.zip>`_. Accepted formats: zip (edam:format_3987).
        input_summary (str): Path to the JSON summary file returned by fpocket. File type: input. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/fpocket/input_summary.json>`_. Accepted formats: json (edam:format_3464).
        output_filter_pockets_zip (str): Path to the selected pockets after filtering. File type: output. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/fpocket/ref_output_filter_pockets.zip>`_. Accepted formats: zip (edam:format_3987).
        properties (dic - Python dictionary object containing the tool parameters, not input/output files):
            * **score** (*list*) - (None) List of two float numbers between 0 and 1 indicating the score range. Indicates the fpocket score after the evaluation of pocket prediction accuracy as defined in the `fpocket paper <https://doi.org/10.1186/1471-2105-10-168>`_.
            * **druggability_score** (*list*) - (None) List of two float numbers between 0 and 1 indicating the druggability_score range. It's a value between 0 and 1, 0 signifying that the pocket is likely to not bind a drug like molecule and 1, that it is very likely to bind the latter.
            * **volume** (*list*) - (None) List of two float numbers indicating the volume range. Indicates the pocket volume.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.
            * **sandbox_path** (*str*) - ("./") [WF property] Parent path to the sandbox directory.

    Examples:
        This is a use example of how to use the building block from Python::

            from biobb_vs.fpocket.fpocket_filter import fpocket_filter
            prop = {
                'score': [0.2, 1],
                'druggability_score': [0.2, 0.8],
                'volume': [100, 600.2]
            }
            fpocket_filter(input_pockets_zip='/path/to/myPockets.zip',
                    input_summary='/path/to/mySummary.json',
                    output_filter_pockets_zip='/path/to/newPockets.json',
                    properties=prop)

    Info:
        * wrapped_software:
            * name: In house
            * license: Apache-2.0
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl

    """

    def __init__(
        self,
        input_pockets_zip,
        input_summary,
        output_filter_pockets_zip,
        properties=None,
        **kwargs,
    ) -> None:
        properties = properties or {}

        # Call parent class constructor
        super().__init__(properties)
        self.locals_var_dict = locals().copy()

        # Input/Output files
        self.io_dict = {
            "in": {
                "input_pockets_zip": input_pockets_zip,
                "input_summary": input_summary,
            },
            "out": {"output_filter_pockets_zip": output_filter_pockets_zip},
        }

        # Properties specific for BB
        self.score = [
            float(elem) for elem in _from_string_to_list(properties.get("score", None))
        ]
        self.druggability_score = [
            float(elem)
            for elem in _from_string_to_list(properties.get("druggability_score", None))
        ]

        self.volume = [
            float(elem) for elem in _from_string_to_list(properties.get("volume", None))
        ]
        self.properties = properties

        # Check the properties
        self.check_properties(properties)
        self.check_arguments()

    def check_data_params(self, out_log, err_log):
        """Checks all the input/output paths and parameters"""
        self.io_dict["in"]["input_pockets_zip"] = check_input_path(
            self.io_dict["in"]["input_pockets_zip"],
            "input_pockets_zip",
            out_log,
            self.__class__.__name__,
        )
        self.io_dict["in"]["input_summary"] = check_output_path(
            self.io_dict["in"]["input_summary"],
            "input_summary",
            False,
            out_log,
            self.__class__.__name__,
        )
        self.io_dict["out"]["output_filter_pockets_zip"] = check_output_path(
            self.io_dict["out"]["output_filter_pockets_zip"],
            "output_filter_pockets_zip",
            True,
            out_log,
            self.__class__.__name__,
        )

    def score_matcher(self, score):
        return lambda d: d["score"] > score[0] and d["score"] <= score[1]

    def druggability_score_matcher(self, druggability_score):
        return (
            lambda d: d["druggability_score"] > druggability_score[0]
            and d["druggability_score"] <= druggability_score[1]
        )

    def volume_matcher(self, volume):
        return lambda d: d["volume"] > volume[0] and d["volume"] <= volume[1]

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`FPocketFilter <fpocket.fpocket_filter.FPocketFilter>` fpocket.fpocket_filter.FPocketFilter object."""

        # check input/output paths and parameters
        self.check_data_params(self.out_log, self.err_log)

        # Setup Biobb
        if self.check_restart():
            return 0
        self.stage_files()

        # load input_summary into a dictionary
        with open(self.io_dict["in"]["input_summary"]) as json_file:
            data = json.load(json_file)

        # build search_list
        search_list = []
        ranges = {}
        if self.score:
            check_range(
                "score", self.score, [0, 1], self.out_log, self.__class__.__name__
            )
            search_list.append(self.score_matcher(self.score))
            ranges["score"] = self.score
        if self.druggability_score:
            check_range(
                "druggability_score",
                self.druggability_score,
                [0, 1],
                self.out_log,
                self.__class__.__name__,
            )
            search_list.append(self.druggability_score_matcher(self.druggability_score))
            ranges["druggability_score"] = self.druggability_score
        if self.volume:
            check_range(
                "volume", self.volume, [0, 10000], self.out_log, self.__class__.__name__
            )
            search_list.append(self.volume_matcher(self.volume))
            ranges["volume"] = self.volume

        fu.log(
            "Performing a search under the next parameters: %s"
            % (", ".join(["{0}: {1}".format(k, v) for k, v in ranges.items()])),
            self.out_log,
        )

        # perform search
        search = [x for x in data if all([f(data[x]) for f in search_list])]

        if len(search) == 0:
            fu.log("No matches found", self.out_log)
            return 0

        str_out = ""
        for s in search:
            str_out = str_out + (
                "\n**********\n%s\n**********\nscore: %s\ndruggability_score: %s\nvolume: %s\n"
                % (
                    s,
                    data[s]["score"],
                    data[s]["druggability_score"],
                    data[s]["volume"],
                )
            )

        fu.log("Found %d matches:%s" % (len(search), str_out), self.out_log)

        # create tmp_folder
        self.tmp_folder = fu.create_unique_dir()
        fu.log("Creating %s temporary folder" % self.tmp_folder, self.out_log)

        process_output_fpocket_filter(
            search,
            self.tmp_folder,
            self.io_dict["in"]["input_pockets_zip"],
            self.io_dict["out"]["output_filter_pockets_zip"],
            self.remove_tmp,
            self.out_log,
        )

        # Copy files to host
        self.copy_to_host()

        self.tmp_files.extend(
            [self.stage_io_dict.get("unique_dir", ""), self.tmp_folder]
        )
        self.remove_tmp_files()

        self.check_arguments(output_files_created=True, raise_exception=False)

        return 0


def fpocket_filter(
    input_pockets_zip: str,
    input_summary: str,
    output_filter_pockets_zip: str,
    properties: Optional[dict] = None,
    **kwargs,
) -> int:
    """Execute the :class:`FPocketFilter <fpocket.fpocket_filter.FPocketFilter>` class and
    execute the :meth:`launch() <fpocket.fpocket_filter.FPocketFilter.launch>` method."""

    return FPocketFilter(
        input_pockets_zip=input_pockets_zip,
        input_summary=input_summary,
        output_filter_pockets_zip=output_filter_pockets_zip,
        properties=properties,
        **kwargs,
    ).launch()


def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(
        description="Finds one or more binding sites in the outputs of the fpocket building block from given parameters.",
        formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999),
    )
    parser.add_argument("--config", required=False, help="Configuration file")

    # Specific args of each building block
    required_args = parser.add_argument_group("required arguments")
    required_args.add_argument(
        "--input_pockets_zip",
        required=True,
        help="Path to all the pockets found by fpocket. Accepted formats: zip.",
    )
    required_args.add_argument(
        "--input_summary",
        required=True,
        help="Path to the JSON summary file returned by fpocket. Accepted formats: json.",
    )
    required_args.add_argument(
        "--output_filter_pockets_zip",
        required=True,
        help="Path to the selected pockets after filtering. Accepted formats: zip.",
    )

    args = parser.parse_args()
    args.config = args.config or "{}"
    properties = settings.ConfReader(config=args.config).get_prop_dic()

    # Specific call of each building block
    fpocket_filter(
        input_pockets_zip=args.input_pockets_zip,
        input_summary=args.input_summary,
        output_filter_pockets_zip=args.output_filter_pockets_zip,
        properties=properties,
    )


if __name__ == "__main__":
    main()
