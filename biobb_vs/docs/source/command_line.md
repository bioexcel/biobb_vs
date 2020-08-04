# BioBB Virtual Screening Command Line Help

Generic usage:


```python
biobb_command [-h] --config CONFIG --input_file(s) <input_file(s)> --output_file <output_file>
```

-----------------

## AutoDockVina

Docking of the ligand to a set of grids describing the target protein.

### Get help

Command:


```python
autodock_vina -h
```


```python
usage: autodock_vina [-h] [--config CONFIG] --input_ligand_pdbqt_path INPUT_LIGAND_PDBQT_PATH --input_receptor_pdbqt_path INPUT_RECEPTOR_PDBQT_PATH --input_box_path INPUT_BOX_PATH --output_pdbqt_path OUTPUT_PDBQT_PATH [--output_log_path OUTPUT_LOG_PATH]

Prepares input ligand for an Autodock Vina Virtual Screening.

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG       Configuration file
  --output_log_path OUTPUT_LOG_PATH
                        Path to the log file. Accepted formats: log.

required arguments:
  --input_ligand_pdbqt_path INPUT_LIGAND_PDBQT_PATH
                        Path to the input PDBQT ligand. Accepted formats: pdbqt.
  --input_receptor_pdbqt_path INPUT_RECEPTOR_PDBQT_PATH
                        Path to the input PDBQT receptor. Accepted formats: pdbqt.
  --input_box_path INPUT_BOX_PATH
                        Path to the PDB containig the residues belonging to the binding site. Accepted formats: pdb.
  --output_pdbqt_path OUTPUT_PDBQT_PATH
                        Path to the output PDBQT file. Accepted formats: pdbqt.
```

### I / O Arguments

Syntax: input_argument (datatype) : Definition

Config input / output arguments for this building block:

* **input_ligand_pdbqt_path** (*str*): Path to the input PDBQT ligand. File type: input. [Sample file](https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/vina/vina_ligand.pdbqt). Accepted formats: pdbqt.
* **input_receptor_pdbqt_path** (*str*): Path to the input PDBQT receptor. File type: input. [Sample file](https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/vina/vina_receptor.pdbqt). Accepted formats: pdbqt.
* **input_box_path** (*str*): Path to the PDB containig the residues belonging to the binding site. [Sample file](https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/vina/vina_box.pdb). Accepted formats: pdb.
* **output_pdbqt_path** (*str*): Path to the output PDBQT file. File type: output. [Sample file](https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/vina/ref_output_vina.pdbqt). Accepted formats: pdbqt.
* **output_log_path** (*str*) (Optional): Path to the log file. File type: output. [Sample file](https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/vina/ref_output_vina.log). Accepted formats: log.

### Config

Syntax: input_parameter (datatype) - (default_value) Definition

Config parameters for this building block:

* **vina_path** (*string*) - ('vina') path to vina in your local computer.
* **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
* **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.

### YAML

#### Common file config


```python
properties:
  vina_path: vina
```

#### Command line


```python
autodock_vina --config data/conf/vina.yml --input_ligand_pdbqt_path data/input/vina_ligand.pdbqt --input_receptor_pdbqt_path data/input/vina_receptor.pdbqt --input_box_path data/input/vina_box.pdb --output_pdbqt_path data/output/output_vina.pdbqt --output_log_path data/output/output_vina.log
```

### JSON

#### Common file config


```python
{
  "properties": {
    "vina_path": "vina"
  }
}
```

#### Command line


```python
autodock_vina --config data/conf/vina.json --input_ligand_pdbqt_path data/input/vina_ligand.pdbqt --input_receptor_pdbqt_path data/input/vina_receptor.pdbqt --input_box_path data/input/vina_box.pdb --output_pdbqt_path data/output/output_vina.pdbqt --output_log_path data/output/output_vina.log
```

## Bindingsite

Finds the binding site of the input_pdb file based on the ligands' location of similar structures (members of the sequence identity cluster).

### Get help

Command:


```python
bindingsite -h
```


```python
usage: bindingsite [-h] [--config CONFIG] --input_pdb_path INPUT_PDB_PATH --input_clusters_zip INPUT_CLUSTERS_ZIP --output_pdb_path OUTPUT_PDB_PATH

Finds the binding site of the input_pdb file based on the ligands' location of similar structures (members of the sequence identity cluster)

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG       Configuration file

required arguments:
  --input_pdb_path INPUT_PDB_PATH
                        Path to the PDB structure where the binding site is to be found. Accepted formats: pdb.
  --input_clusters_zip INPUT_CLUSTERS_ZIP
                        Path to the ZIP file with all the PDB members of the identity cluster. Accepted formats: zip.
  --output_pdb_path OUTPUT_PDB_PATH
                        Path to the PDB containig the residues belonging to the binding site. Accepted formats: pdb.
```

### I / O Arguments

Syntax: input_argument (datatype) : Definition

Config input / output arguments for this building block:

* **input_pdb_path** (*str*): Path to the PDB structure where the binding site is to be found. File type: input. [Sample file](https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/utils/bindingsite.pdb). Accepted formats: pdb.
* **input_clusters_zip** (*str*): Path to the ZIP file with all the PDB members of the identity cluster. File type: input. [Sample file](https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/utils/bindingsite.zip). Accepted formats: zip.
* **output_pdb_path** (*str*): Path to the PDB containig the residues belonging to the binding site. File type: output. [Sample file](https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/utils/ref_output_bindingsite.pdb). Accepted formats: pdb.

### Config

Syntax: input_parameter (datatype) - (default_value) Definition

Config parameters for this building block:

* **ligand** (*str*) - (None) Ligand to be found in the protein structure. If no ligand provided, no action will be executed.
* **radius** (*float*) - (5.0) Cut-off distance(Angstroms) around ligand atoms to consider a protein atom as a binding site atom.
* **max_num_ligands** (*int*) - (15) Total number of superimposed ligands to be extracted from the identity cluster. For populated clusters, the restriction avoids to superimpose redundant structures. If 0, all ligands extracted will be considered.
* **matrix_name** (*str*) - ('blosum62') Substitution matrices for use in alignments. Values: 'benner6', 'benner22', 'benner74', 'blosum100', 'blosum30', 'blosum35', 'blosum40', 'blosum45', 'blosum50', 'blosum55', 'blosum60', 'blosum62', 'blosum65', 'blosum70', 'blosum75', 'blosum80', 'blosum85', 'blosum90', 'blosum95', 'feng', 'fitch', 'genetic', 'gonnet', 'grant', 'ident', 'johnson', 'levin', 'mclach', 'miyata', 'nwsgappep', 'pam120', 'pam180', 'pam250', 'pam30', 'pam300', 'pam60', 'pam90', 'rao', 'risler', 'structure'.
* **gap_open** (*float*) - (-10.0) Gap open penalty.
* **gap_extend** (*float*) - (-0.5) Gap extend penalty.
* **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
* **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.

### YAML

#### Common file config


```python
properties:
  ligand: PGA
  matrix_name: blosum62
  gap_open: -10.0
  gap_extend: -0.5
  max_num_ligands: 15
  radius: 5
```

#### Command line


```python
bindingsite --conf data/conf/bindingsite.yml --input_pdb_path data/input/input_bindingsite.pdb --input_clusters_zip data/input/input_bindingsite.zip --output_pdb_path data/output/output_bindingsite.pdb
```

### JSON

#### Common file config


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
bindingsite --conf data/conf/bindingsite.json --input_pdb_path data/input/input_bindingsite.pdb --input_clusters_zip data/input/input_bindingsite.zip --output_pdb_path data/output/output_bindingsite.pdb
```

## Box

Sets the center and the size of a rectangular parallelepiped box around a selection of residues found in a given PDB. The residue identifiers that compose the selection (i.e. binding site) are extracted from a second PDB.

### Get help

Command:


```python
box -h
```


```python
usage: box [-h] [--config CONFIG] --input_pdb_path INPUT_PDB_PATH --resid_pdb_path RESID_PDB_PATH --output_pdb_path OUTPUT_PDB_PATH

Sets the center and the size of a rectangular parallelepiped box around a selection of residues found in a given PDB. The residue identifiers that compose the selection (i.e. binding site) are extracted from a second PDB.

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG       Configuration file

required arguments:
  --input_pdb_path INPUT_PDB_PATH
                        Path to the PDB structure where the binding site is to be found. Accepted formats: pdb.
  --resid_pdb_path RESID_PDB_PATH
                        PDB file containing a selection of residue numbers mappable to 'input_pdb_path'. Accepted formats: pdb.
  --output_pdb_path OUTPUT_PDB_PATH
                        Path to the PDB containig the residues belonging to the binding site. Accepted formats: pdb.
```

### I / O Arguments

Syntax: input_argument (datatype) : Definition

Config input / output arguments for this building block:

* **input_pdb_path** (*str*): PDB protein structure for which the box will be build. Its size and center will be set around the 'resid_pdb_path' residues once mapped against this PDB. File type: input. [Sample file](https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/utils/box.pdb). Accepted formats: pdb.
* **resid_pdb_path** (*str*): PDB file containing a selection of residue numbers mappable to 'input_pdb_path'. File type: input.  [Sample file](https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/utils/resid_box.pdb). Accepted formats: pdb.
* **output_pdb_path** (*str*): PDB protein structure coordinates including the annotation of the box center and size as REMARKs. File type: output. [Sample file](https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/utils/ref_output_box.pdb). Accepted formats: pdb.

### Config

Syntax: input_parameter (datatype) - (default_value) Definition

Config parameters for this building block:

* **offset** (*float*) - (2.0) Extra distance (Angstroms) between the last residue atom and the box boundary.
* **residue_offset** (*int*) - (0) Residue id offset.
* **box_coordinates** (*bool*) - (False) Add box coordinates as 8 ATOM records.
* **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
* **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.

### YAML

#### Common file config


```python
properties:
  offset: 2
  box_coordinates: true
```

#### Command line


```python
box --conf data/conf/box.yml --input_pdb_path data/input/input_box.pdb --resid_pdb_path data/input/input_resid.pdb --output_pdb_path data/output/output_box.pdb
```

### JSON

#### Common file config


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
box --conf data/conf/box.json --input_pdb_path data/input/input_box.pdb --resid_pdb_path data/input/input_resid.pdb --output_pdb_path data/output/output_box.pdb
```

## ExtractModelPDBQT

Extracts a model from a PDBQT file with several models

### Get help

Command:


```python
extract_model_pdbqt -h
```


```python
usage: extract_model_pdbqt [-h] [--config CONFIG] --input_pdbqt_path INPUT_PDBQT_PATH --output_pdbqt_path OUTPUT_PDBQT_PATH

Extracts a model from a PDBQT file with several models.

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG       Configuration file

required arguments:
  --input_pdbqt_path INPUT_PDBQT_PATH
                        Input PDBQT file. Accepted formats: pdbqt.
  --output_pdbqt_path OUTPUT_PDBQT_PATH
                        Output PDBQT file. Accepted formats: pdbqt.
```

### I / O Arguments

Syntax: input_argument (datatype) : Definition

Config input / output arguments for this building block:

* **input_pdbqt_path** (*str*): Input PDBQT file. File type: input. [Sample file](https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/data/utils/models.pdbqt). Accepted formats: pdbqt.
* **output_pdbqt_path** (*str*): Output PDBQT file. File type: output. [Sample file](https://github.com/bioexcel/biobb_vs/raw/master/biobb_vs/test/reference/utils/ref_extract_model.pdbqt). Accepted formats: pdbqt.

### Config

Syntax: input_parameter (datatype) - (default_value) Definition

Config parameters for this building block:

* **model** (*int*) - (1) Model number to extract from input_pdbqt_path.
* **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
* **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.

### YAML

#### Common file config


```python
properties:
  model: 1
```

#### Command line


```python
extract_model_pdbqt --config data/conf/extract_model.yml --input_pdbqt_path data/input/extract_models.pdbqt --output_pdbqt_path data/output/output_extract_models.pdbqt
```

### JSON

#### Common file config


```python
{
  "properties": {
    "model": 1
  }
}
```

#### Command line


```python
extract_model_pdbqt --config data/conf/extract_model.json --input_pdbqt_path data/input/extract_models.pdbqt --output_pdbqt_path data/output/output_extract_models.pdbqt
```
