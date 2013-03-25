from setuptools import setup

setup(name='patience',
      author="Andrea Censi",
      author_email="andrea@cds.caltech.edu",
      url='http://github.com/AndreaCensi/patience',
    	version="1.0",
      description="A command line tool for managing multiple git repositories.",
      package_dir={'':'src'},
      packages=['patience'],
      install_requires=['pyyaml'],
      entry_points={
         'console_scripts': [
           'patience = patience.main:main',
           'patience_search = patience.patience_search:main',
           'patience2html = patience.patience2html:main'
        ]  
      }, 
)


