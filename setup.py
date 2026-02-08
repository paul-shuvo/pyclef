from setuptools import setup, find_packages

setup(
    name="pyclef-lib",
    version="0.1.0",
    description="A Python library for working with CLEF log files",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Shuvo Paul",
    url="https://github.com/paul-shuvo/pyclef",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        # Add runtime dependencies here
    ],
    extras_require={
        "dev": [
            "black>=23.0",
        ],
        "test": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
        ],
        "docs": [
            "sphinx>=5.3.0",
            "shibuya>=2026.1.9",  # Ensure this is a valid dependency
            "sphinx-autodoc-typehints>=1.20.0",
            "sphinxcontrib-napoleon>=0.7",
            "sphinx-autobuild>=2021.3.14",
        ],
    },
    package_data={
        "": ["*.txt", "*.rst", "*.md"],
    },
)