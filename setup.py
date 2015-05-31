#from distutils.core import setup

from setuptools import setup
try:
    from pypandoc import convert
    
    read_md = lambda f: convert(f, 'rst')
    
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()

read_rst = open('README.rst', 'w')
read_rst.write(read_md('README.md').encode('utf-8')) # convert returns unicode
read_rst.close()
'''
setup(
    # name, version, ...
    long_description=read_md('README.md'),
    install_requires=[]
)
'''

def run():
    setup(name="PestTools",
        version="0.0.1",
        description="Python package for processing and visualizing information associated with the parameter estimation software PEST",
        long_description=read_md('README.md'),
        url="",
        license="MIT",
        author="Evan Christianson, Andrew Leaf, Mike Fienen",
        maintainer_email="",
        packages=["pestools"],
    )

if __name__ == "__main__":
    run()


