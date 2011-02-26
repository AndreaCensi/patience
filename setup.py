from setuptools import setup

setup(name='patience',
	version="0.3",
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


