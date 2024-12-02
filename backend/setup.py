from setuptools import setup, find_packages

setup(
    name="natural-python",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flask==2.0.1",
        "flask-cors==3.0.10",
        "python-dotenv==0.19.0",
        "gunicorn==20.1.0",
        "pytest==7.0.1",
        "flask-talisman==0.8.1",
        "requests==2.31.0",
        "python-dateutil==2.8.2"
    ],
    python_requires=">=3.9",
    author="Anish Shinde",
    description="A natural language interface for Python programming",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
    ],
) 