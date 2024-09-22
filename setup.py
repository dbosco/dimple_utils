from setuptools import setup, find_packages

setup(
    name="dimple_utils",
    version="0.1.0",
    description="A collection of Python utility wrappers for common libraries.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Don Bosco Durai",
    url="https://github.com/dbosco/dimple_utils",
    packages=find_packages(),
    install_requires=[
        "requests>=2.26.0",
    ],
    extras_require={
        "dev": ["pytest", "flake8"],  # Development dependencies
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
    entry_points={
        'console_scripts': [
            # Add any command-line tools here, e.g.:
            # 'dimple-cli=dimple_utils.cli:main',
        ],
    },
)
