import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pysirix",
    version="0.1.0",
    author="Moshe Uminer",
    author_email="mosheduminer@gmail.com",
    description="The SirixDB Python SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sirixdb/sirix-python-client",
    packages=setuptools.find_packages(exclude=("tests",)),
    install_requires=["httpx"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)