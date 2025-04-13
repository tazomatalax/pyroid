from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pyroid",
    version="1.0.0",
    author="PyRoid Team",
    description="A Radially Symmetrical Gyroid Generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.20.0",
        "pyvista>=0.43.0",
        "trimesh>=4.0.0",
        "PyQt5>=5.15.0",
        "pyvistaqt>=0.11.0",
        "QDarkStyle>=3.0.0"
    ],
    entry_points={
        "console_scripts": [
            "pyroid=main:main",
            "pyroid-cli=pyroid.cli:main",
        ],
    },
)