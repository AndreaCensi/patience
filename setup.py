from setuptools import setup, find_packages

install_requires = ["pyyaml", "SystemCmd-z7", "PyContracts3"]

setup(
    name="patience",
    author="Andrea Censi",
    author_email="github@censi.org",
    url="http://github.com/AndreaCensi/patience",
    version="1.5.0",
    description="A command line tool for managing multiple git repositories.",
    package_dir={"": "src"},
    packages=find_packages("src"),
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "patience = patience.main:main",
            "patience_search = patience.patience_search:main",
            "pat = patience.main:main",
            "patience2html = patience.patience2html:main",
        ]
    },
)
