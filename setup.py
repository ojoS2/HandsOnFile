from setuptools import setup
def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='HandsOnFile',
    version='0.0.1',
    description='A package to organize and translate pdfs',
    classifiers=[
        'Development Status :: 1 - Gama',
        'License ::  MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Text Processing :: Linguistic',
        ],
    author='Ricardo',
    author_email='ojogodascontasdevidro@gmail.com',
    license='MIT',
    install_requires=[
        'unstructured',
        'language_tool_python',
        'deep_translator',
        're',
        'numpy',
        'os',
        'string',
        'PyPDF2',
        'distutils'
        'shutil',
        'textwrap',
        'awkward',
        ],
    py_modules=['HandsOnFile'],
    include_package_data=True,
    python_requires=">=3.6"
)
