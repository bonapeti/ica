from setuptools import setup

setup(
    name='iac',
    version='0.2.0',
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
