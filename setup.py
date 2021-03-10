from setuptools import setup

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='genshinstats',
    version='1.2.7',
    author='thesadru',
    packages=['genshinstats'],
    description='A wrapper for the official hoyolab.com Genshin impact gameRecord API.',
    keywords='wrapper-api genshin'.split(),
    python_requires='>=3.6',
    url='https://github.com/thesadru/genshinstats',
    install_requires=['requests'],
    author_email='dan0.suman@gmail.com',
    long_description=long_description,
    long_description_content_type='text/markdown',
)