import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pysirix",
    version="0.1.2",
    author="Moshe Uminer",
    author_email="mosheduminer@gmail.com",
    description="The SirixDB Python SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sirixdb/sirix-python-client",
    packages=setuptools.find_packages(exclude=("tests",)),
    install_requires=["httpx==0.13.3"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
