from setuptools import setup, find_packages

setup(
    name="pi_pvarr",
    version="0.1.0",
    description="Media server stack management system for Raspberry Pi and Linux",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/username/Pi-PVARR",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "flask>=2.2.3",
        "flask-cors>=3.0.10",
        "psutil>=5.9.5",
        "requests>=2.28.2",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0",
        "docker>=6.1.2",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "flake8",
            "black",
            "mypy",
            "isort",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)