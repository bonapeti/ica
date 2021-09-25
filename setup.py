from setuptools import setup

setup(
    name='ica',
    version='0.0.1',
    py_modules=['ica'],
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'ica = ica:main',
        ],
    },
)