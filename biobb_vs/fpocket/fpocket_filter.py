#!/usr/bin/env python3

"""Module containing the FPocketFilter class and the command line interface."""
import argparse
import os
from biobb_common.configuration import  settings
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger
from biobb_common.command_wrapper import cmd_wrapper
from biobb_vs.fpocket.common import *

class FPocketFilter():
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

    def __init__(self, input_pockets_zip, input_summary, output_filter_pockets_zip, 
                properties=None, **kwargs) -> None:
        properties = properties or {}

        # Input/Output files
        self.io_dict = { 
            "in": { "input_pockets_zip": input_pockets_zip, "input_summary": input_summary }, 
            "out": { "output_filter_pockets_zip": output_filter_pockets_zip } 
        }

        # Properties specific for BB
        self.score = properties.get('score', None)
        self.druggability_score = properties.get('druggability_score', None)
        self.volume = properties.get('volume', None)
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
        self.io_dict["in"]["input_summary"] = check_output_path(self.io_dict["in"]["input_summary"],"input_summary", False, out_log, self.__class__.__name__)
        self.io_dict["out"]["output_filter_pockets_zip"] = check_output_path(self.io_dict["out"]["output_filter_pockets_zip"],"output_filter_pockets_zip", True, out_log, self.__class__.__name__)

    def score_matcher(self, score):
        return lambda d: d['score'] > score[0] and d['score'] <= score[1]

    def druggability_score_matcher(self, druggability_score):
        return lambda d: d['druggability_score'] > druggability_score[0] and d['druggability_score'] <= druggability_score[1]

    def volume_matcher(self, volume):
        return lambda d: d['volume'] > volume[0] and d['volume'] <= volume[1]

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`FPocketFilter <fpocket.fpocket_filter.FPocketFilter>` fpocket.fpocket_filter.FPocketFilter object."""

        # Get local loggers from launchlogger decorator
        out_log = getattr(self, 'out_log', None)
        err_log = getattr(self, 'err_log', None)

        # check input/output paths and parameters
        self.check_data_params(out_log, err_log)

        # Check the properties
        fu.check_properties(self, self.properties)

        if self.restart:
            output_file_list = [self.io_dict["out"]["output_filter_pockets_zip"]]
            if fu.check_complete_files(output_file_list):
                fu.log('Restart is enabled, this step: %s will the skipped' % self.step, out_log, self.global_log)
                return 0

        # load input_summary into a dictionary
        with open(self.io_dict["in"]["input_summary"]) as json_file:
            data = json.load(json_file)

        # build search_list
        search_list = []
        ranges = {}
        if self.score: 
            check_range('score', self.score, [0,1], out_log, self.__class__.__name__)
            search_list.append(self.score_matcher(self.score))
            ranges['score'] = self.score
        if self.druggability_score: 
            check_range('druggability_score', self.druggability_score, [0,1], out_log, self.__class__.__name__)
            search_list.append(self.druggability_score_matcher(self.druggability_score))
            ranges['druggability_score'] = self.druggability_score
        if self.volume: 
            check_range('volume', self.volume, [0,10000], out_log, self.__class__.__name__)
            search_list.append(self.volume_matcher(self.volume))
            ranges['volume'] = self.volume

        fu.log('Performing a search under the next parameters: %s' % (', '.join(['{0}: {1}'.format(k, v) for k,v in ranges.items()])), out_log)

        # perform search
        search = [ x for x in data if all([f(data[x]) for f in search_list]) ]

        if len(search) == 0:
            fu.log('No matches found', out_log)
            return 0

        str_out = '';
        for s in search:
            str_out = str_out + ('\n**********\n%s\n**********\nscore: %s\ndruggability_score: %s\nvolume: %s\n' % (s, data[s]["score"], data[s]["druggability_score"], data[s]["volume"]))

        fu.log('Found %d matches:%s' % (len(search), str_out), out_log)

        # create tmp_folder
        self.tmp_folder = fu.create_unique_dir()
        fu.log('Creating %s temporary folder' % self.tmp_folder, out_log)

        process_output_fpocket_filter(search,
                                    self.tmp_folder,
                                    self.io_dict["in"]["input_pockets_zip"],
                                    self.io_dict["out"]["output_filter_pockets_zip"],
                                    self.remove_tmp, 
                                    out_log)

        return 0

def fpocket_filter(input_pockets_zip: str, input_summary: str, output_filter_pockets_zip:str, properties: dict = None, **kwargs) -> int:
    """Execute the :class:`FPocketFilter <fpocket.fpocket_filter.FPocketFilter>` class and
    execute the :meth:`launch() <fpocket.fpocket_filter.FPocketFilter.launch>` method."""

    return FPocketFilter(input_pockets_zip=input_pockets_zip,
                input_summary=input_summary,
                output_filter_pockets_zip=output_filter_pockets_zip,
                properties=properties, **kwargs).launch()

def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(description="Finds one or more binding sites in the outputs of the fpocket building block from given parameters.", formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('--config', required=False, help='Configuration file')

    # Specific args of each building block
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--input_pockets_zip', required=True, help='Path to all the pockets found by fpocket. Accepted formats: zip.')
    required_args.add_argument('--input_summary', required=True, help='Path to the JSON summary file returned by fpocket. Accepted formats: json.')
    required_args.add_argument('--output_filter_pockets_zip', required=True, help='Path to the selected pockets after filtering. Accepted formats: zip.')

    args = parser.parse_args()
    args.config = args.config or "{}"
    properties = settings.ConfReader(config=args.config).get_prop_dic()

    # Specific call of each building block
    fpocket_filter(input_pockets_zip=args.input_pockets_zip, 
            input_summary=args.input_summary, 
            output_filter_pockets_zip=args.output_filter_pockets_zip, 
            properties=properties)

if __name__ == '__main__':
    main()
