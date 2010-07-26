from setuptools import setup

setup(name='patience',
	version="0.1",
      package_dir={'':'src'},
      py_modules=['patience'],
      install_requires=[],
      entry_points={
         'console_scripts': [
           'patience = patience.scripts.patience:main'
        ]
      }, 
)


