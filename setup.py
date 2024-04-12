from setuptools import setup, find_packages

setup(
    name='doorvestStatementExtractor',
    version='0.1.0',
    description='A Python package to extract statements from Doorvest PDFs',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/gramcraka/doorvestStatementExtractor',
    packages=find_packages(),
    install_requires=[
        'bitarray==2.9.2',
        'numpy==1.26.4',
        'pandas==2.2.2',
        'pdfreader==0.1.12',
        'pillow==10.3.0',
        'pycryptodome==3.20.0',
        'pypdf2==3.0.1',
        'python-dateutil==2.9.0.post0',
        'pytz==2024.1',
        'setuptools==68.2.0',
        'six==1.16.0',
        'typing-extensions==4.11.0',
        'tzdata==2024.1',
        'wheel==0.41.2'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
    ],
)
