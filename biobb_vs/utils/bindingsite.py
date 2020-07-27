#!/usr/bin/env python3

"""Module containing the BindingSite class and the command line interface."""
import argparse
from biobb_common.configuration import  settings
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger
from biobb_common.command_wrapper import cmd_wrapper
from biobb_vs.utils.common import *

class BindingSite():
    """Finds the binding site of the input_pdb file based on the ligands' location of similar structures (members of the sequence identity cluster)

    Args:
        input_pdb_path (str): Path to the PDB structure where the binding site is to be found. File type: input. `Sample file <>`_. Accepted formats: pdb.
        input_clusters_zip (str): Path to the ZIP file with all the PDB members of the identity cluster. File type: input. `Sample file <>`_. Accepted formats: zip.
        output_pdb_path (str): Path to the PDB containig the residues belonging to the binding site. File type: output. `Sample file <>`_. Accepted formats: pdb.
        properties (dic):
            * **ligand** (*str*) - (None) Ligand to be found in the protein structure. If no ligand provided, no action will be executed.
            * **radius** (*float*) - (5.0) Cut-off distance(Amstrongs) around ligand atoms to consider a protein atom as a binding site atom.
            * **max_num_ligands** (*int*) - (15) Total number of superimposed ligands to be extracted from the identity cluster. For populated clusters, the restriction avoids to superimpose redundant structures. If 0, all ligands extracted will be considered.
            * **matrix_name** (*str*) - ('blosum62') Substitution matrices for use in alignments. Values: 'benner6', 'benner22', 'benner74', 'blosum100', 'blosum30', 'blosum35', 'blosum40', 'blosum45', 'blosum50', 'blosum55', 'blosum60', 'blosum62', 'blosum65', 'blosum70', 'blosum75', 'blosum80', 'blosum85', 'blosum90', 'blosum95', 'feng', 'fitch', 'genetic', 'gonnet', 'grant', 'ident', 'johnson', 'levin', 'mclach', 'miyata', 'nwsgappep', 'pam120', 'pam180', 'pam250', 'pam30', 'pam300', 'pam60', 'pam90', 'rao', 'risler', 'structure'.
            * **gap_open** (*float*) - (-10.0) Gap open penalty.
            * **gap_extend** (*float*) - (-0.5) Gap extend penalty.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.
    """

    def __init__(self, input_pdb_path, input_clusters_zip,
                output_pdb_path, properties=None, **kwargs) -> None:
        properties = properties or {}

        # Input/Output files
        self.io_dict = { 
            "in": { "input_pdb_path": input_pdb_path, "input_clusters_zip": input_clusters_zip },
            "out": { "output_pdb_path": output_pdb_path } 
        }

        # Properties specific for BB
        self.ligand = properties.get('ligand', None)
        self.radius = float(properties.get('radius', 5.0))
        self.max_num_ligands = properties.get('max_num_ligands', 15)
        self.matrix_name = properties.get('matrix_name', 'blosum62')
        self.gap_open = properties.get('gap_open', -10.0)
        self.gap_extend = properties.get('gap_extend', -0.5)
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
        self.io_dict["in"]["input_pdb_path"] = check_input_path(self.io_dict["in"]["input_pdb_path"],"input_pdb_path", out_log, self.__class__.__name__)
        self.io_dict["in"]["input_clusters_zip"] = check_input_path(self.io_dict["in"]["input_clusters_zip"],"input_clusters_zip", out_log, self.__class__.__name__)
        self.io_dict["out"]["output_pdb_path"] = check_output_path(self.io_dict["out"]["output_pdb_path"],"output_pdb_path", False, out_log, self.__class__.__name__)


    @launchlogger
    def launch(self) -> int:
        """Launches the execution of the BindingSite module."""

        # Get local loggers from launchlogger decorator
        out_log = getattr(self, 'out_log', None)
        err_log = getattr(self, 'err_log', None)

        # check input/output paths and parameters
        self.check_data_params(out_log, err_log)

        # Check the properties
        fu.check_properties(self, self.properties)

        if self.restart:
            output_file_list = [self.io_dict["out"]["output_pdb_path"]]
            if fu.check_complete_files(output_file_list):
                fu.log('Restart is enabled, this step: %s will the skipped' % self.step, out_log, self.global_log)
                return 0


        # Parse structure
        structure_name = PurePath(self.io_dict["in"]["input_pdb_path"]).name
        parser      = Bio.PDB.PDBParser(QUIET = True)
        structPDB   = parser.get_structure(structure_name, self.io_dict["in"]["input_pdb_path"])

        if len(structPDB):
            structPDB = structPDB[0]

        # Use only one chain
        n_chains = structPDB.get_list()
        if len(n_chains) != 1:
            fu.log('More than one chain found in the input PDB structure. Using only the first chain to find the binding site', out_log, self.global_log)
            # get first chain in case there is more than one chain
            for struct_chain in structPDB.get_chains():
                structPDB = struct_chain

        # Get AA sequence
        structPDB_seq   = get_pdb_sequence(structPDB)
        if len(structPDB_seq) == 0:
            fu.log(self.__class__.__name__ + ': Cannot extract AA sequence from the input PDB structure %s. Wrong format?' % self.io_dict["in"]["input_pdb_path"], out_log)
            raise SystemExit(self.__class__.__name__ + ': Cannot extract AA sequence from the input PDB structure %s. Wrong format?' % self.io_dict["in"]["input_pdb_path"])
        else:
            fu.log('Found %s residues in %s' % (len(structPDB_seq), self.io_dict["in"]["input_pdb_path"]), out_log)

        # create temporary folder for decompressing the input_clusters_zip file
        unique_dir = PurePath(fu.create_unique_dir())
        fu.log('Creating %s temporary folder' % unique_dir, out_log, self.global_log)

        # decompress the input_clusters_zip file
        cluster_list = fu.unzip_list(zip_file = self.io_dict["in"]["input_clusters_zip"], dest_dir = unique_dir, out_log = out_log)

        clusterPDB_ligands_aligned = []
        clusterPDB_ligands_num     = 0

        fu.log('Iterating on all clusters:', out_log)

        for idx, cluster_path in enumerate(cluster_list):

            cluster_name = PurePath(cluster_path).stem
            fu.log(' ', out_log)
            fu.log('------------ Iteration #%s --------------' % (idx + 1), out_log)
            fu.log('Cluster member: %s' % cluster_name, out_log)

             # Load and Parse PDB
            clusterPDB = {}
            clusterPDB = parser.get_structure(cluster_name, cluster_path)[0]

            # Use only the fist chain
            for cluster_chain in clusterPDB.get_chains():
                clusterPDB = cluster_chain

            # Looking for ligands
            clusterPDB_ligands = get_ligand_residues(clusterPDB)
            if (len(clusterPDB_ligands)) == 0:
                fu.log('No ligands found that could guide the binding site search. Ignoring this member: %s' % cluster_name, out_log)
                continue

            # Selecting the largest ligand, if more than one
            lig_atoms_num     = 0
            clusterPDB_ligand = {}
            if self.ligand:
                if self.ligand in [x.get_resname() for x in clusterPDB_ligands]:
                    for lig in clusterPDB_ligands:
                        if lig.get_resname() == self.ligand:
                            clusterPDB_ligand = lig
                            lig_atoms_num = len(lig.get_list())
                            fu.log('Ligand found: %s  (%s atoms)' % (lig.get_resname(), lig_atoms_num), out_log)
                else:
                    fu.log('Ligand %s not found in %s cluster member, skipping this cluster' % (self.ligand, cluster_name), out_log)
                    continue
            else:        
                if len(clusterPDB_ligands) > 1:
                    for lig_res in clusterPDB_ligands:
                        lig_res_atoms_num = len(lig_res.get_list())
                        fu.log('Ligand found: %s  (%s atoms)' % (lig_res.get_resname(), lig_res_atoms_num), out_log)
                        if lig_res_atoms_num > lig_atoms_num:
                            clusterPDB_ligand = lig_res
                            lig_atoms_num     = lig_res_atoms_num
                else:
                    clusterPDB_ligand = clusterPDB_ligands[0]
                    lig_atoms_num = len(clusterPDB_ligands[0].get_list())

            fu.log('Member accepted. Valid ligand found: %s (%s atoms)' % (clusterPDB_ligand.get_resname(), lig_atoms_num), out_log)

            ## Mapping residues by sequence alignment to match structPDB-clusterPDB paired residues

            # Get AA sequence
            clusterPDB_seq = get_pdb_sequence(clusterPDB)

            # Pairwise align
            aln, residue_map = align_sequences(structPDB_seq, clusterPDB_seq, self.matrix_name, self.gap_open, self.gap_extend)
            fu.log('Matching residues to input PDB structure. Alignment is:\n%s' % (aln[1]), out_log)

            # Calculate (gapless) sequence identity
            seq_identity, gap_seq_identity = calculate_alignment_identity(aln[0], aln[1])
            fu.log('Sequence identity (%%): %s' % (seq_identity), out_log)
            fu.log('Gap less identity (%%): %s' % (gap_seq_identity), out_log)

            ## Selecting aligned CA atoms from first model, first chain

            struct_atoms  = []
            cluster_atoms = []

            for struct_res in residue_map:
                try:
                    cluster_atoms.append(clusterPDB[residue_map[struct_res]]['CA'])
                    struct_atoms.append(get_residue_by_id(structPDB, struct_res)['CA'])
                except KeyError:
                    fu.log('Cannot find CA atom for residue %s  (input PDB  %s)' % (get_residue_by_id(structPDB, struct_res).get_resname(),struct_res), out_log)
                    pass

            if len(cluster_atoms)==0:
                fu.log(self.__class__.__name__ + ': Cannot find CA atoms (1st model, 1st chain) in cluster member %s when aligning against %s. Ignoring this member.' % (cluster_name, structure_name), out_log)
                raise SystemExit(self.__class__.__name__ + ': Cannot find CA atoms (1st model, 1st chain) in cluster member %s when aligning against %s. Ignoring this member.' % (cluster_name, structure_name))
            else:
                fu.log('Superimposing %s aligned protein residues' % (len(cluster_atoms)), out_log)

            ## Align against input structure

            si = Bio.PDB.Superimposer()
            si.set_atoms(struct_atoms, cluster_atoms)
            si.apply(clusterPDB.get_atoms())
            fu.log('RMSD: %s' % (si.rms), out_log)

            # Save transformed structure (and ligand)
            clusterPDB_ligand_aligned = clusterPDB[clusterPDB_ligand.get_id()]
            fu.log('Saving transformed ligand coordinates', out_log)

            clusterPDB_ligands_aligned.append(clusterPDB_ligand_aligned)

            ##  Stop after n accepted cluster members

            clusterPDB_ligands_num += 1

            if clusterPDB_ligands_num > self.max_num_ligands:
                break

        fu.log(' ', out_log)
        fu.log('----------------------------------------', out_log)
        fu.log('All transformed ligand coordinates saved, getting binding site residues', out_log)

        ## Select binding site atoms as those around cluster superimposed ligands

        fu.log('Defining binding site residues as those %sÅ around the %s cluster superimposed ligands' % (self.radius, clusterPDB_ligands_num), out_log)

        # select Atoms from aligned ligands
        clusterPDB_ligands_aligned2      = [res for res in clusterPDB_ligands_aligned]
        clusterPDB_ligands_aligned_atoms = Bio.PDB.Selection.unfold_entities(clusterPDB_ligands_aligned2, 'A')

        # select Atoms from input PDB structure
        structPDB_atoms = [ atom for atom in structPDB.get_atoms()]

        # compute neighbors for aligned ligands in the input PDB structure
        structPDB_bs_residues_raw = {}
        structPDB_neighbors = Bio.PDB.NeighborSearch(structPDB_atoms)
        for ligand_atom in clusterPDB_ligands_aligned_atoms:
                # look for PDB atoms 5A around each ligand atom
                k_l = structPDB_neighbors.search(ligand_atom.coord, self.radius, 'R')
                for k in k_l:
                    structPDB_bs_residues_raw[k.get_id()] = k.get_full_id()

        ## Save binding site to PDB

        io = Bio.PDB.PDBIO()
        fu.log('Writing binding site residues into %s' % (self.io_dict["out"]["output_pdb_path"]), out_log)

        # unselect input PDB atoms not in binding site
        structPDB_bs_atoms = 0
        p = re.compile('H_|W_|W')       
        residue_ids_to_remove = []
        for res in structPDB.get_residues():
            if res.id not in structPDB_bs_residues_raw.keys():
                # add residue to residue_ids_to_remove list
                residue_ids_to_remove.append(res.id)
            elif p.match(res.resname):
                # add residue to residue_ids_to_remove list
                residue_ids_to_remove.append(res.id)
            else:
                # this residue will be preserved
                structPDB_bs_atoms += len(res.get_list())

        # unselect input PDB atoms not in binding site
        for chain in structPDB:
            for idr in residue_ids_to_remove:
                chain.detach_child(idr)

        # write PDB file
        io.set_structure(structPDB)
        io.save(self.io_dict["out"]["output_pdb_path"])

        if self.remove_tmp:
            # remove temporary folder
            fu.rm(unique_dir)
            fu.log(' ', out_log)
            fu.log('----------------------------------------', out_log)
            fu.log('Removed temporary folder: %s' % unique_dir, out_log)


        #return returncode
        return 0

def main():
    parser = argparse.ArgumentParser(description="Finds the binding site of the input_pdb file based on the ligands' location of similar structures (members of the sequence identity cluster)", formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('--config', required=False, help='Configuration file')

    # Specific args of each building block
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--input_pdb_path', required=True, help='Path to the PDB structure where the binding site is to be found. Accepted formats: pdb.')
    required_args.add_argument('--input_clusters_zip', required=True, help='Path to the ZIP file with all the PDB members of the identity cluster. Accepted formats: zip.')
    required_args.add_argument('--output_pdb_path', required=True, help='Path to the PDB containig the residues belonging to the binding site. Accepted formats: pdb.')

    args = parser.parse_args()
    args.config = args.config or "{}"
    properties = settings.ConfReader(config=args.config).get_prop_dic()

    # Specific call of each building block
    BindingSite(input_pdb_path=args.input_pdb_path, input_clusters_zip=args.input_clusters_zip, 
                    output_pdb_path=args.output_pdb_path, 
                    properties=properties).launch()

if __name__ == '__main__':
    main()
