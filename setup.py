from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='glorb',
    version='1.0.0',
    py_modules=['glorb'],
    install_requires=[
        'pywin32; sys_platform == "win32"',
        'WMI; sys_platform == "win32"'
    ],
    entry_points={
        'console_scripts': [
            'glorb=glorb:main',
        ],
    },
    author='Your Name',
    author_email='your.email@example.com',
    description='A fun CLI tool for monitor management',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/yourusername/glorb',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: System :: Hardware',
        'Topic :: Utilities',
    ],
    python_requires='>=3.7',
    keywords='monitor display rotation brightness cli windows',
)