from setuptools import setup, find_packages

setup(
    name="minisc",
    version="0.1.0",
    description="A multi-cloud Kubernetes deployment module.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="minisc",
    author_email="ekremaksoy@gmail.com",
    url="https://github.com/eax/minisc",
    packages=find_packages(),
    include_package_data=True,
    install_requires=open("requirements.txt").read().splitlines(),
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "minisc-api=minisc.api_runner:main",
        ],
    },
)