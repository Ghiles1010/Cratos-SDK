from setuptools import setup, find_packages

# Read the README file for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read the version from cratos/__init__.py
version = None
with open("cratos/__init__.py", "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip("'\"")
            break
if not version:
    raise RuntimeError("Cannot find version in cratos/__init__.py")

setup(
    name="cratos",
    version=version,
    description="Simple HTTP client for Cratos task scheduler",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "pydantic>=2.0.0",
        "websocket-client>=1.0.0"
    ],
    python_requires=">=3.7",
    author="Cratos Team",
    author_email="contact@cratos.dev",
    url="https://github.com/Ghiles1010/Cratos-SDK",
    project_urls={
        "Bug Tracker": "https://github.com/Ghiles1010/Cratos-SDK/issues",
        "Documentation": "https://github.com/Ghiles1010/Cratos-SDK",
        "Source Code": "https://github.com/Ghiles1010/Cratos-SDK",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
    ],
    keywords="cratos, task, scheduler, async, webhook",
    license="MIT",
) 