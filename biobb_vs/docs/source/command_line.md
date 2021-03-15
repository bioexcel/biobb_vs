# BioBB VS Command Line Help
Generic usage:
```python
biobb_command [-h] --config CONFIG --input_file(s) <input_file(s)> --output_file <output_file>
```
-----------------


## Bindingsite
This class finds the binding site of the input_pdb.
### Get help
Command:
```python
bindingsite -h
```
    /bin/sh: bindingsite: command not found
### I / O Arguments
Syntax: input_argument (datatype) : Definition

Config input / output arguments for this building block:
* **input_pdb_path** (*string*): Path to the PDB structure where the binding site is to be found. File type: input. [Sample file](https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/utils/bindingsite.pdb). Accepted formats: PDB
* **input_clusters_zip** (*string*): Path to the ZIP file with all the PDB members of the identity cluster. File type: input. [Sample file](https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/utils/bindingsite.zip). Accepted formats: ZIP
* **output_pdb_path** (*string*): Path to the PDB containig the residues belonging to the binding site. File type: output. [Sample file](https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/utils/ref_output_bindingsite.pdb). Accepted formats: PDB
### Config
Syntax: input_parameter (datatype) - (default_value) Definition

Config parameters for this building block:
* **ligand** (*string*): (None) Ligand to be found in the protein structure. If no ligand provided, no action will be executed..
* **radius** (*number*): (5.0) Cut-off distance (Ångstroms) around ligand atoms to consider a protein atom as a binding site atom..
* **max_num_ligands** (*integer*): (15) Total number of superimposed ligands to be extracted from the identity cluster. For populated clusters, the restriction avoids to superimpose redundant structures. If 0, all ligands extracted will be considered..
* **matrix_name** (*string*): (blosum62) Substitution matrices for use in alignments. .
* **gap_open** (*number*): (-10.0) Gap open penalty..
* **gap_extend** (*number*): (-0.5) Gap extend penalty..
* **remove_tmp** (*boolean*): (True) Remove temporal files..
* **restart** (*boolean*): (False) Do not execute if output files exist..
### YAML
#### [Common config file](https://github.com/bioexcel/biobb_vs/blob/master/biobb_vs/test/data/config/config_bindingsite.yml)
```python
properties:
  gap_extend: -0.5
  gap_open: -10.0
  ligand: PGA
  matrix_name: blosum62
  max_num_ligands: 15
  radius: 5

```
#### Command line
```python
bindingsite --config config_bindingsite.yml --input_pdb_path bindingsite.pdb --input_clusters_zip bindingsite.zip --output_pdb_path ref_output_bindingsite.pdb
```
### JSON
#### [Common config file](https://github.com/bioexcel/biobb_vs/blob/master/biobb_vs/test/data/config/config_bindingsite.json)
```python
{
  "properties": {
    "ligand": "PGA",
    "matrix_name": "blosum62",
    "gap_open": -10.0,
    "gap_extend": -0.5,
    "max_num_ligands": 15,
    "radius": 5
  }
}
```
#### Command line
```python
bindingsite --config config_bindingsite.json --input_pdb_path bindingsite.pdb --input_clusters_zip bindingsite.zip --output_pdb_path ref_output_bindingsite.pdb
```

## Box
This class sets the center and the size of a rectangular parallelepiped box around a set of residues or a pocket.
### Get help
Command:
```python
box -h
```
    /bin/sh: box: command not found
### I / O Arguments
Syntax: input_argument (datatype) : Definition

Config input / output arguments for this building block:
* **input_pdb_path** (*string*): PDB file containing a selection of residue numbers or PQR file containing the pocket. File type: input. [Sample file](https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/utils/input_box.pqr). Accepted formats: PDB, PQR
* **output_pdb_path** (*string*): PDB including the annotation of the box center and size as REMARKs. File type: output. [Sample file](https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/utils/ref_output_box.pdb). Accepted formats: PDB
### Config
Syntax: input_parameter (datatype) - (default_value) Definition

Config parameters for this building block:
* **offset** (*number*): (2.0) Extra distance (Angstroms) between the last residue atom and the box boundary..
* **box_coordinates** (*boolean*): (False) Add box coordinates as 8 ATOM records..
* **remove_tmp** (*boolean*): (True) Remove temporal files..
* **restart** (*boolean*): (False) Do not execute if output files exist..
### YAML
#### [Common config file](https://github.com/bioexcel/biobb_vs/blob/master/biobb_vs/test/data/config/config_box.yml)
```python
properties:
  box_coordinates: true
  offset: 2

```
#### Command line
```python
box --config config_box.yml --input_pdb_path input_box.pqr --output_pdb_path ref_output_box.pdb
```
### JSON
#### [Common config file](https://github.com/bioexcel/biobb_vs/blob/master/biobb_vs/test/data/config/config_box.json)
```python
{
  "properties": {
    "offset": 2,
    "box_coordinates": true
  }
}
```
#### Command line
```python
box --config config_box.json --input_pdb_path input_box.pqr --output_pdb_path ref_output_box.pdb
```

## Fpocket_filter
Performs a search over the outputs of the fpocket building block.
### Get help
Command:
```python
fpocket_filter -h
```
    /bin/sh: fpocket_filter: command not found
### I / O Arguments
Syntax: input_argument (datatype) : Definition

Config input / output arguments for this building block:
* **input_pockets_zip** (*string*): Path to all the pockets found by fpocket. File type: input. [Sample file](https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/fpocket/input_pockets.zip). Accepted formats: ZIP
* **input_summary** (*string*): Path to the JSON summary file returned by fpocket. File type: input. [Sample file](https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/fpocket/input_summary.json). Accepted formats: JSON
* **output_filter_pockets_zip** (*string*): Path to the selected pockets after filtering. File type: output. [Sample file](https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/fpocket/ref_output_filter_pockets.zip). Accepted formats: ZIP
### Config
Syntax: input_parameter (datatype) - (default_value) Definition

Config parameters for this building block:
* **score** (*array*): (None) List of two float numbers between 0 and 1 indicating the score range. Indicates the fpocket score after the evaluation of pocket prediction accuracy as defined in the fpocket paper..
* **druggability_score** (*array*): (None) List of two float numbers between 0 and 1 indicating the druggability_score range. It's a value between 0 and 1, 0 signifying that the pocket is likely to not bind a drug like molecule and 1, that it is very likely to bind the latter..
* **volume** (*array*): (None) List of two float numbers indicating the volume range. Indicates the pocket volume..
* **remove_tmp** (*boolean*): (True) Remove temporal files..
* **restart** (*boolean*): (False) Do not execute if output files exist..
### YAML
#### [Common config file](https://github.com/bioexcel/biobb_vs/blob/master/biobb_vs/test/data/config/config_fpocket_filter.yml)
```python
properties:
  druggability_score:
  - 0.2
  - 0.9
  score:
  - 0.2
  - 1
  volume:
  - 100
  - 600

```
#### Command line
```python
fpocket_filter --config config_fpocket_filter.yml --input_pockets_zip input_pockets.zip --input_summary input_summary.json --output_filter_pockets_zip ref_output_filter_pockets.zip
```
### JSON
#### [Common config file](https://github.com/bioexcel/biobb_vs/blob/master/biobb_vs/test/data/config/config_fpocket_filter.json)
```python
{
  "properties": {
    "score": [
      0.2,
      1
    ],
    "druggability_score": [
      0.2,
      0.9
    ],
    "volume": [
      100,
      600
    ]
  }
}
```
#### Command line
```python
fpocket_filter --config config_fpocket_filter.json --input_pockets_zip input_pockets.zip --input_summary input_summary.json --output_filter_pockets_zip ref_output_filter_pockets.zip
```

## Box_residues
This class sets the center and the size of a rectangular parallelepiped box around a set of residues.
### Get help
Command:
```python
box_residues -h
```
    /bin/sh: box_residues: command not found
### I / O Arguments
Syntax: input_argument (datatype) : Definition

Config input / output arguments for this building block:
* **input_pdb_path** (*string*): PDB protein structure for which the box will be build. Its size and center will be set around the 'resid_list' property once mapped against this PDB. File type: input. [Sample file](https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/utils/input_box_residues.pdb). Accepted formats: PDB
* **output_pdb_path** (*string*): PDB including the annotation of the box center and size as REMARKs. File type: output. [Sample file](https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/utils/ref_output_box_residues.pdb). Accepted formats: PDB
### Config
Syntax: input_parameter (datatype) - (default_value) Definition

Config parameters for this building block:
* **resid_list** (*array*): (None) List with all the residue numbers to form a cavity or binding site. Mandatory property..
* **offset** (*number*): (2.0) Extra distance (Angstroms) between the last residue atom and the box boundary..
* **box_coordinates** (*boolean*): (False) Add box coordinates as 8 ATOM records..
* **residue_offset** (*integer*): (0) Residue id offset..
* **remove_tmp** (*boolean*): (True) Remove temporal files..
* **restart** (*boolean*): (False) Do not execute if output files exist..
### YAML
#### [Common config file](https://github.com/bioexcel/biobb_vs/blob/master/biobb_vs/test/data/config/config_box_residues.yml)
```python
properties:
  box_coordinates: true
  offset: 2
  resid_list:
  - 718
  - 743
  - 745
  - 762
  - 766
  - 796
  - 790
  - 791
  - 793
  - 794
  - 788

```
#### Command line
```python
box_residues --config config_box_residues.yml --input_pdb_path input_box_residues.pdb --output_pdb_path ref_output_box_residues.pdb
```
### JSON
#### [Common config file](https://github.com/bioexcel/biobb_vs/blob/master/biobb_vs/test/data/config/config_box_residues.json)
```python
{
  "properties": {
    "resid_list": [
      718,
      743,
      745,
      762,
      766,
      796,
      790,
      791,
      793,
      794,
      788
    ],
    "offset": 2,
    "box_coordinates": true
  }
}
```
#### Command line
```python
box_residues --config config_box_residues.json --input_pdb_path input_box_residues.pdb --output_pdb_path ref_output_box_residues.pdb
```

## Fpocket
Wrapper of the fpocket software.
### Get help
Command:
```python
fpocket -h
```
    /bin/sh: fpocket: command not found
### I / O Arguments
Syntax: input_argument (datatype) : Definition

Config input / output arguments for this building block:
* **input_pdb_path** (*string*): Path to the PDB structure where the binding site is to be found. File type: input. [Sample file](https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/fpocket/fpocket_input.pdb). Accepted formats: PDB
* **output_pockets_zip** (*string*): Path to all the pockets found by fpocket in the input_pdb_path structure. File type: output. [Sample file](https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/fpocket/ref_output_pockets.zip). Accepted formats: ZIP
* **output_summary** (*string*): Path to the JSON summary file. File type: output. [Sample file](https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/fpocket/ref_output_summary.json). Accepted formats: JSON
### Config
Syntax: input_parameter (datatype) - (default_value) Definition

Config parameters for this building block:
* **min_radius** (*number*): (None) The minimum radius in Ångstroms an alpha sphere might have in a binding pocket..
* **max_radius** (*number*): (None) The maximum radius in Ångstroms of alpha spheres in a pocket..
* **num_spheres** (*integer*): (None) Indicates how many alpha spheres a pocket must contain at least in order to figure in the results..
* **sort_by** (*string*): (druggability_score) From which property the output will be sorted. .
* **fpocket_path** (*string*): (fpocket) path to fpocket in your local computer..
* **remove_tmp** (*boolean*): (True) Remove temporal files..
* **restart** (*boolean*): (False) Do not execute if output files exist..
### YAML
#### [Common config file](https://github.com/bioexcel/biobb_vs/blob/master/biobb_vs/test/data/config/config_fpocket.yml)
```python
properties:
  max_radius: 6
  min_radius: 3
  num_spheres: 35
  sort_by: druggability_score

```
#### Command line
```python
fpocket --config config_fpocket.yml --input_pdb_path fpocket_input.pdb --output_pockets_zip ref_output_pockets.zip --output_summary ref_output_summary.json
```
### JSON
#### [Common config file](https://github.com/bioexcel/biobb_vs/blob/master/biobb_vs/test/data/config/config_fpocket.json)
```python
{
  "properties": {
    "min_radius": 3,
    "max_radius": 6,
    "num_spheres": 35,
    "sort_by": "druggability_score"
  }
}
```
#### Command line
```python
fpocket --config config_fpocket.json --input_pdb_path fpocket_input.pdb --output_pockets_zip ref_output_pockets.zip --output_summary ref_output_summary.json
```

## Autodock_vina
Wrapper of the AutoDock Vina software.
### Get help
Command:
```python
autodock_vina -h
```
    /bin/sh: autodock_vina: command not found
### I / O Arguments
Syntax: input_argument (datatype) : Definition

Config input / output arguments for this building block:
* **input_ligand_pdbqt_path** (*string*): Path to the input PDBQT ligand. File type: input. [Sample file](https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/vina/vina_ligand.pdbqt). Accepted formats: PDBQT
* **input_receptor_pdbqt_path** (*string*): Path to the input PDBQT receptor. File type: input. [Sample file](https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/vina/vina_receptor.pdbqt). Accepted formats: PDBQT
* **input_box_path** (*string*): Path to the PDB containig the residues belonging to the binding site. File type: input. [Sample file](https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/vina/vina_box.pdb). Accepted formats: PDB
* **output_pdbqt_path** (*string*): Path to the output PDBQT file. File type: output. [Sample file](https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/vina/ref_output_vina.pdbqt). Accepted formats: PDBQT
* **output_log_path** (*string*): Path to the log file. File type: output. [Sample file](https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/vina/ref_output_vina.log). Accepted formats: LOG
### Config
Syntax: input_parameter (datatype) - (default_value) Definition

Config parameters for this building block:
* **vina_path** (*string*): (vina) path to vina in your local computer..
* **remove_tmp** (*boolean*): (True) Remove temporal files..
* **restart** (*boolean*): (False) Do not execute if output files exist..
### YAML
#### [Common config file](https://github.com/bioexcel/biobb_vs/blob/master/biobb_vs/test/data/config/config_autodock_vina.yml)
```python
properties:
  remove_tmp: true

```
#### Command line
```python
autodock_vina --config config_autodock_vina.yml --input_ligand_pdbqt_path vina_ligand.pdbqt --input_receptor_pdbqt_path vina_receptor.pdbqt --input_box_path vina_box.pdb --output_pdbqt_path ref_output_vina.pdbqt --output_log_path ref_output_vina.log
```
### JSON
#### [Common config file](https://github.com/bioexcel/biobb_vs/blob/master/biobb_vs/test/data/config/config_autodock_vina.json)
```python
{
  "properties": {
    "remove_tmp": true
  }
}
```
#### Command line
```python
autodock_vina --config config_autodock_vina.json --input_ligand_pdbqt_path vina_ligand.pdbqt --input_receptor_pdbqt_path vina_receptor.pdbqt --input_box_path vina_box.pdb --output_pdbqt_path ref_output_vina.pdbqt --output_log_path ref_output_vina.log
```

## Fpocket_select
Selects a single pocket in the outputs of the fpocket building block.
### Get help
Command:
```python
fpocket_select -h
```
    /bin/sh: fpocket_select: command not found
### I / O Arguments
Syntax: input_argument (datatype) : Definition

Config input / output arguments for this building block:
* **input_pockets_zip** (*string*): Path to the pockets found by fpocket. File type: input. [Sample file](https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/fpocket/input_pockets.zip). Accepted formats: ZIP
* **output_pocket_pdb** (*string*): Path to the PDB file with the cavity found by fpocket. File type: output. [Sample file](https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/fpocket/ref_output_pocket.pdb). Accepted formats: PDB
* **output_pocket_pqr** (*string*): Path to the PQR file with the pocket found by fpocket. File type: output. [Sample file](https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/fpocket/ref_output_pocket.pqr). Accepted formats: PQR
### Config
Syntax: input_parameter (datatype) - (default_value) Definition

Config parameters for this building block:
* **pocket** (*integer*): (1) Pocket id from the summary json given by the fpocket building block..
* **remove_tmp** (*boolean*): (True) Remove temporal files..
* **restart** (*boolean*): (False) Do not execute if output files exist..
### YAML
#### [Common config file](https://github.com/bioexcel/biobb_vs/blob/master/biobb_vs/test/data/config/config_fpocket_select.yml)
```python
properties:
  pocket: 4

```
#### Command line
```python
fpocket_select --config config_fpocket_select.yml --input_pockets_zip input_pockets.zip --output_pocket_pdb ref_output_pocket.pdb --output_pocket_pqr ref_output_pocket.pqr
```
### JSON
#### [Common config file](https://github.com/bioexcel/biobb_vs/blob/master/biobb_vs/test/data/config/config_fpocket_select.json)
```python
{
  "properties": {
    "pocket": 4
  }
}
```
#### Command line
```python
fpocket_select --config config_fpocket_select.json --input_pockets_zip input_pockets.zip --output_pocket_pdb ref_output_pocket.pdb --output_pocket_pqr ref_output_pocket.pqr
```

## Extract_model_pdbqt
Extracts a model from a PDBQT file with several models.
### Get help
Command:
```python
extract_model_pdbqt -h
```
    /bin/sh: extract_model_pdbqt: command not found
### I / O Arguments
Syntax: input_argument (datatype) : Definition

Config input / output arguments for this building block:
* **input_pdbqt_path** (*string*): Input PDBQT file. File type: input. [Sample file](https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/utils/models.pdbqt). Accepted formats: PDBQT
* **output_pdbqt_path** (*string*): Output PDBQT file. File type: output. [Sample file](https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/utils/ref_extract_model.pdbqt). Accepted formats: PDBQT
### Config
Syntax: input_parameter (datatype) - (default_value) Definition

Config parameters for this building block:
* **model** (*integer*): (1) Model number to extract from input_pdbqt_path..
* **remove_tmp** (*boolean*): (True) Remove temporal files..
* **restart** (*boolean*): (False) Do not execute if output files exist..
### YAML
#### [Common config file](https://github.com/bioexcel/biobb_vs/blob/master/biobb_vs/test/data/config/config_extract_model_pdbqt.yml)
```python
properties:
  model: 1

```
#### Command line
```python
extract_model_pdbqt --config config_extract_model_pdbqt.yml --input_pdbqt_path models.pdbqt --output_pdbqt_path ref_extract_model.pdbqt
```
### JSON
#### [Common config file](https://github.com/bioexcel/biobb_vs/blob/master/biobb_vs/test/data/config/config_extract_model_pdbqt.json)
```python
{
  "properties": {
    "model": 1
  }
}
```
#### Command line
```python
extract_model_pdbqt --config config_extract_model_pdbqt.json --input_pdbqt_path models.pdbqt --output_pdbqt_path ref_extract_model.pdbqt
```
