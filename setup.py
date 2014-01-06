from setuptools import setup, find_packages


setup(name='patience',
      author="Andrea Censi",
      author_email="censi@mit.edu",
      url='http://github.com/AndreaCensi/patience',
    	version="1.5.0",
      description="A command line tool for managing multiple git repositories.",
      package_dir={'':'src'},
      packages=find_packages('src'),
      install_requires=['pyyaml', 'SystemCmd', 'PyContracts'],
      entry_points={
         'console_scripts': [
           'patience = patience.main:main',
           'patience_search = patience.patience_search:main',
           'pat = patience.main:main',
           'patience2html = patience.patience2html:main'
        ]  
      },
)


