from setuptools import setup

setup(
    name='iac',
    version='0.0.2',
    py_modules=['iac'],
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'ica = iac:main',
        ],
    },
)