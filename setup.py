from setuptools import setup

setup(
    name='genshinstats',
    version='1.3.12',
    author='thesadru',
    packages=['genshinstats'],
    description="A python library that can get the stats of Genshin Impact players using Mihoyo's API.",
    keywords='api wrapper sign-in gacha mihoyo genshin genshin-impact hoyolab'.split(),
    python_requires='>=3.6',
    url='https://github.com/thesadru/genshinstats',
    install_requires=['requests'],
    author_email='thesadru@gmail.com',
    long_description=open('README.md', encoding="utf-8").read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'Typing :: Typed',
    ]
)
