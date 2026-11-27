#!/usr/bin/env python3

"""Module containing the GninaSelectPose class and the command line interface."""
from typing import Optional

from biobb_common.generic.biobb_object import BiobbObject, launcher
from biobb_common.tools import file_utils as fu

from biobb_vs.gnina.common import check_gzip_extension, open_sdf, read_sdf_records, to_number


class GninaSelectPose(BiobbObject):
    """
    | biobb_vs GninaSelectPose
    | Selects a single pose in the output of the gnina_run building block.
    | Extracts one pose out of the multi record SDF file written by the gnina_run building block, copying the record verbatim.

    Args:
        input_sdf_path (str): Path to the SDF file with the docked poses written by the gnina_run building block. File type: input. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/gnina/gnina_poses.sdf>`_. Accepted formats: sdf (edam:format_3814), gz (edam:format_3989).
        output_sdf_path (str): Path to the output SDF file with the selected pose. File type: output. `Sample file <https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/gnina/ref_output_pose.sdf>`_. Accepted formats: sdf (edam:format_3814), gz (edam:format_3989).
        properties (dic - Python dictionary object containing the tool parameters, not input/output files):
            * **pose** (*int*) - (1) [1~10000|1] Rank of the pose to extract, counted over the poses left after ligand has been applied and sort_by has been honoured.
            * **ligand** (*int*) - (None) [1~1000000|1] Index of the ligand whose poses are considered, following the order of the ligands in the file gnina docked. All poses in the file are considered when unset.
            * **sort_by** (*str*) - (None) Score to reorder the poses by before one is picked. The poses are taken in the order gnina wrote them when unset, which is already gnina's own ranking. Note that this reorders only the poses present in the file, so it is not equivalent to the pose_sort_order property of gnina_run, which reorders the whole internal pool before the redundancy filter and the num_modes cutoff discard poses. Values: CNNscore (network pose score, highest first), CNNaffinity (network predicted affinity, highest first), minimizedAffinity (empirical affinity in kcal/mol, lowest first).
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.
            * **sandbox_path** (*str*) - ("./") [WF property] Parent path to the sandbox directory.

    Examples:
        This is a use example of how to use the building block from Python::

            from biobb_vs.gnina.gnina_select_pose import gnina_select_pose
            prop = {
                'pose': 1,
                'sort_by': 'CNNaffinity'
            }
            gnina_select_pose(input_sdf_path='/path/to/myPoses.sdf',
                              output_sdf_path='/path/to/myBestPose.sdf',
                              properties=prop)

    Info:
        * wrapped_software:
            * name: In house
            * license: Apache-2.0
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl

    """

    # score to sort by, mapped to whether the highest value is the best one
    SORT_ORDERS = {
        'CNNscore': True,
        'CNNaffinity': True,
        'minimizedAffinity': False
    }

    def __init__(self, input_sdf_path: str, output_sdf_path: str,
                 properties: Optional[dict] = None, **kwargs) -> None:
        super().__init__(**locals())

    def prepare(self):
        """ Checks all the input/output paths and parameters """
        # a gzip compressed SDF file must be named .sdf.gz
        check_gzip_extension(self.io_dict["in"]["input_sdf_path"], "input_sdf_path", self.out_log, self.__class__.__name__)
        check_gzip_extension(self.io_dict["out"]["output_sdf_path"], "output_sdf_path", self.out_log, self.__class__.__name__)

        if self.sort_by is not None and self.sort_by not in self.SORT_ORDERS:
            fu.log(self.__class__.__name__ + ': Unknown sort_by %s, use one of %s, exiting' % (self.sort_by, ', '.join(self.SORT_ORDERS)), self.out_log)
            raise SystemExit(self.__class__.__name__ + ': Unknown sort_by %s' % self.sort_by)

    def select_record(self, records):
        """ Narrows the records down to the requested ligand, reorders them and picks one """

        if self.ligand is not None:
            records = [record for record in records if record['ligand_index'] == self.ligand]
            if not records:
                fu.log(self.__class__.__name__ + ': No poses found for ligand %s, exiting' % self.ligand, self.out_log)
                raise SystemExit(self.__class__.__name__ + ': No poses found for ligand %s' % self.ligand)
            fu.log('%d pose(s) found for ligand %s' % (len(records), self.ligand), self.out_log)

        if self.sort_by:
            missing = [record for record in records if self.sort_by not in record['data']]
            if missing:
                fu.log(self.__class__.__name__ + ': %s is missing from some poses, gnina only writes it for certain cnn_scoring values, exiting' % self.sort_by, self.out_log)
                raise SystemExit(self.__class__.__name__ + ': %s is missing from some poses' % self.sort_by)
            records = sorted(records,
                             key=lambda record: to_number(record['data'][self.sort_by]),
                             reverse=self.SORT_ORDERS[self.sort_by])
            fu.log('Poses reordered by %s' % self.sort_by, self.out_log)

        if self.pose < 1 or self.pose > len(records):
            fu.log(self.__class__.__name__ + ': pose %s is out of range, only %d pose(s) to choose from, exiting' % (self.pose, len(records)), self.out_log)
            raise SystemExit(self.__class__.__name__ + ': pose %s is out of range, only %d pose(s) to choose from' % (self.pose, len(records)))

        return records[self.pose - 1]

    def stage_files(self) -> None:
        """The block does not use the sandbox: there are no files to stage."""

    def run(self) -> None:
        """Execute the :class:`GninaSelectPose <gnina.gnina_select_pose.GninaSelectPose>` gnina.gnina_select_pose.GninaSelectPose object."""

        records = read_sdf_records(self.io_dict["in"]["input_sdf_path"])
        fu.log('%d pose(s) read from %s' % (len(records), self.io_dict["in"]["input_sdf_path"]), self.out_log)

        record = self.select_record(records)

        fu.log('Saving pose %s of ligand %s (%s) to %s file' % (
            record['pose'], record['ligand_index'], record['name'],
            self.io_dict["out"]["output_sdf_path"]), self.out_log)

        # the record is copied as it stands, scores included
        with open_sdf(self.io_dict["out"]["output_sdf_path"], 'wt') as output_file:
            output_file.write(record['text'])


gnina_select_pose = launcher(GninaSelectPose)


if __name__ == '__main__':
    GninaSelectPose.main()
