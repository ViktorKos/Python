from setuptools import setup, find_namespace_packages

setup(
	name='simple_clean_folder',
	version='1.0',
	description='Cleans a given folder by sorting and moving files into set of typed folders.',
	url='https://github.com/ViktorKos/Python/tree/main/simple_clean_folder',
	author='Viktor Kos',
	author_email='viktor.v.kos@gmail.com',
	license='MIT',
	packages=find_namespace_packages(),
	entry_points={'console_scripts': ['cleanfolder = simple_clean_folder.clean:main']}
)