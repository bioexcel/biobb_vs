import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="biobb_vs",
    version="5.3.0",
    author="Biobb developers",
    author_email="genis.bayarri@irbbarcelona.org",
    description="Biobb_vs is the Biobb module collection to perform virtual screening studies.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="Bioinformatics Workflows BioExcel Compatibility",
    url="https://github.com/bioexcel/biobb_vs",
    project_urls={
        "Documentation": "http://biobb-vs.readthedocs.io/en/latest/",
        "Bioexcel": "https://bioexcel.eu/",
    },
    packages=setuptools.find_packages(exclude=["docs", "test"]),
    package_data={"biobb_vs": ["py.typed"]},
    install_requires=["biobb_common==5.3.1"],
    python_requires=">=3.11",
    entry_points={
        "console_scripts": [
            "fpocket_filter = biobb_vs.fpocket.fpocket_filter:FPocketFilter.main",
            "fpocket_run = biobb_vs.fpocket.fpocket_run:FPocketRun.main",
            "fpocket_select = biobb_vs.fpocket.fpocket_select:FPocketSelect.main",
            "bindingsite = biobb_vs.utils.bindingsite:BindingSite.main",
            "box_residues = biobb_vs.utils.box_residues:BoxResidues.main",
            "box = biobb_vs.utils.box:Box.main",
            "extract_model_pdbqt = biobb_vs.utils.extract_model_pdbqt:ExtractModelPDBQT.main",
            "autodock_vina_run = biobb_vs.vina.autodock_vina_run:AutoDockVinaRun.main",
            "gnina_run = biobb_vs.gnina.gnina_run:GninaRun.main",
            "gnina_select_pose = biobb_vs.gnina.gnina_select_pose:GninaSelectPose.main",
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Operating System :: Unix",
    ],
)
