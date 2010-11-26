from setuptools import setup

setup(name='patience',
	version="0.2",
      package_dir={'':'src'},
      packages=['patience'],
      install_requires=['pyyaml'],
      entry_points={
         'console_scripts': [
           'patience = patience.scripts.main:main',
           'patience_search = patience.scripts.patience_search:main'
        ]
      }, 
)


