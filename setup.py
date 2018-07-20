from setuptools import setup

setup(
    name='concierge-python',
    version='0.0.1',
    description='concierge helper for Snips',
    author='Snips Labs',
    author_email='labs@snips.ai',
    url='https://github.com/akaisuisei/concierge-python',
    download_url='',
    license='MIT',
    install_requires=[
        'requests==2.6.0'
    ],
    keywords=['snips'],
    packages=['concierge-python'],
    include_package_data=True
)
