from setuptools import setup

setup(
    name="paddle",
    packages=["paddle"],
    include_package_data=True,
    install_requires=[
        "flask",
    ],
)
