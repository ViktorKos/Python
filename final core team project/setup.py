from setuptools import setup, find_packages

setup(
    name='project_13',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'mprogrammulinka=project_13.main:main',
        ],
    }
)