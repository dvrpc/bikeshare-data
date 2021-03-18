from setuptools import find_packages, setup

setup(
    name="bikeshare_data",
    packages=find_packages(),
    version="0.1.0",
    description="Python module to facilitate the acquisition and analysis of Indego bikeshare data",
    author="Aaron Fraint, AICP",
    license="GPL-3.0",
    entry_points="""
        [console_scripts]
        indego=bikeshare_data.cli:main
    """,
)