from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="rin",
    version="1.2.0",
    author="CTO (Acting)",
    description="Rhyzomic Intelligence Node - A sovereign AI agent system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/radkisson/Rhyzomic-Intelligence-Node-RIN-",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: AI",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.24.0",
        "requests>=2.31.0",
        "pyyaml>=6.0.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "full": [
            "playwright>=1.40.0",
            "beautifulsoup4>=4.12.0",
            "chromadb>=0.4.0",
            "sentence-transformers>=2.2.0",
            "openai>=1.0.0",
            "anthropic>=0.7.0",
        ],
        "dev": [
            "pytest>=7.4.0",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "pylint>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "rin=rin.main:main",
        ],
    },
)
