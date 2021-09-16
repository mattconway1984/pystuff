from setuptools import setup

setup(
    name="CTestPy",
    description="Test framework for writing PyTest test cases for C Code Under Test.",
    author="Robert Rescorla, Alex King, Matthew Conway",
    version="2.1.0",
    install_requires=[
        "pycparser",
        "cffi",
    ],
    python_requires=">=3.8",
    packages=["ctestpy"],
    entry_points={
        'console_scripts': [
            "ctestpy = ctestpy.__main__:main",
        ]
    }
)
