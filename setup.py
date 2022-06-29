
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="minerinterface",
    version="0.5.3",
    author="Michael Schmid",
    author_email="michael@amazee.com",
    description="python library to talk to crypto miners",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/schnitzel/minerinterface",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    install_requires=["asyncssh>=2.7.2", "cryptography>=35.0.0", "passlib>=1.7.4", "PyYAML>=6.0", "toml>=0.10.2"],
    python_requires=">=3.9",
)