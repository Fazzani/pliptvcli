import setuptools

with open("readme.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as f:
    required = f.read().splitlines()

setuptools.setup(
    name="xplcli",
    version="0.1.7",
    author="Heni FAZZANI",
    author_email="heni.fazzani@gmail.com",
    description="Simple extensible m3u playlist manager cli",
    long_description=long_description,
    include_package_data=True,
    long_description_content_type="text/markdown",
    url="https://github.com/Fazzani/pliptvcli",
    packages=setuptools.find_packages(),
    install_requires=required,
    license="MIT",
    entry_points={"console_scripts": ["xpl=pliptv.main:main"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
