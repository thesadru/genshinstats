from setuptools import setup

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='genshinstats-api',
    version='1.0.0',
    author='thesadru',
    py_modules=['genshinstats'],
    description='a wrapper for the official hoyolab.com Genshin impact gameRecord API.',
    keywords='wrapper-api genshin'.split(),
    python_requires='>=3.6',
    url='https://github.com/thesadru/genshinstats-api',
    package_data={'': ['config.ini']},
    include_package_data=True,
    install_requires=['requests'],
    author_email='dan0.suman@gmail.com',
    long_description=long_description,
    long_description_content_type='text/markdown',
)