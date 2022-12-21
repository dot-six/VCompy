import sys
from setuptools import find_packages, setup

with open('vcompy/version.py', 'r') as f:
	exec(f.read())

with open('README.md', 'r') as f:
	README = f.read()

requires=[
	'Pillow==9.3.0',
	'imageio==2.23.0',
	'imageio[pyav]',
	'numpy==1.24.0'
]

setup(
	name='vcompy',
	version=__version__,
	author='Hanz <hanz@godot.id>',
	description='Video compiler',
	long_description=README,
	long_description_content_type='text/markdown',
	url='https://github.com/dot-six/vcompy',
	license='MIT License',
	classifiers=[],
	keywords='video editing ffmpeg',
	packages=['vcompy'],
	install_requires=requires
)
