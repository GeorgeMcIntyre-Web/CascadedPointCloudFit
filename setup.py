"""Setup file for CascadedPointCloudFit package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements-minimal.txt"
requirements = []
if requirements_file.exists():
    requirements = requirements_file.read_text().splitlines()

setup(
    name="cascaded-point-cloud-fit",
    version="1.0.0",
    description="Cascaded point cloud registration using PCA, ICP, and FGR algorithms",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/CascadedPointCloudFit",
    packages=find_packages(exclude=["tests", "tests.*", "scripts", "docs"]),
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "flake8>=6.1.0",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cascaded-fit=cascaded_fit.cli.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    include_package_data=True,
    package_data={
        "cascaded_fit": ["py.typed"],
    },
)
