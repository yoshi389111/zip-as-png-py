from setuptools import setup, find_packages

setup(
    name="zipaspng",
    version="0.0.1",
    description="disguise zip to png",
    packages=find_packages(exclude=("tests", "docs")),
    test_suite="tests",
    entry_points = {
        "console_scripts": ["zipaspng=zipaspng.zipaspng:main"],
    },
)
