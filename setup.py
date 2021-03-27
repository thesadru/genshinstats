from setuptools import setup

setup(
    name='genshinstats',
    version='1.3.3',
    author='thesadru',
    packages=['genshinstats'],
    description="A python library that can get the stats of your or others' Genshin Impact account using Mihoyo's API.",
    keywords='wrapper-api genshin'.split(),
    python_requires='>=3.8',
    url='https://github.com/thesadru/genshinstats',
    install_requires=['requests'],
    author_email='dan0.suman@gmail.com',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)