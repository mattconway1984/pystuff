#pylint:skip-file

import setuptools

setuptools.setup(
    name="fun_async",
    version="0.0.0",
    description="Playing around with asyncio",
    packages=setuptools.find_namespace_packages(include=['fun_async', 'fun_async.*']),
    python_requires=">=3.6",
    install_requires=[],
)
