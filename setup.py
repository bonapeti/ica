from setuptools import setup

setup(
    name='iac',
    version='0.0.3',
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
