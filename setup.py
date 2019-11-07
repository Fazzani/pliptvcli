import setuptools

with open("readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="xpl",
    version="0.0.5-dev0",
    author="Heni Fazzani",
    author_email="heni.fazzani@gmail.com",
    description="Simple extensible m3u playlist manager cli",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Fazzani/pliptvcli",
    packages=setuptools.find_packages(),
    entry_points={"console_scripts": ["xpl=main:main"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
