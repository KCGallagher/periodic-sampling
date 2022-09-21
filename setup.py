from setuptools import setup, find_packages

setup(
   name='periodic_sampling',
   version='1.0',
   license="MIT",
   description='Bayesian sampling methods to explore periodic data trends in epidemiological data',
   author='Kit Gallagher',
   install_requires=['numpy', 'pandas', 'scipy'],
   packages=find_packages(include=('periodic_sampling')),
)