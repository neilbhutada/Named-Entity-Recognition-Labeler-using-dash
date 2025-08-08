import io
from setuptools import setup, find_packages

with io.open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='dash-ner-labeler',
    version='0.1.0',
    description='A Plotly Dash component for Named Entity Recognition (NER) text labeling',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/dash-ner-labeler',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Framework :: Dash',
    ],
    install_requires=[
        'dash>=2.0.0',
        'dash-html-components',
        'dash-core-components'
    ],
    python_requires='>=3.6',
)