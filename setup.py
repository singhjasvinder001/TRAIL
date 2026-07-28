from setuptools import setup, find_packages

setup(
    name="trail",
    version="0.1.0",
    description="Your activity trail — never lose your context again.",
    packages=find_packages(),
    install_requires=["rich"],
    entry_points={
        "console_scripts": [
            "trail=trail.cli:main",
        ],
    },
    python_requires=">=3.10",
)
