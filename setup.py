from setuptools import setup

setup(
    name='concierge_python',
    version='0.0.1.4',
    description='concierge helper for Snips',
    author='Snips Labs',
    author_email='labs@snips.ai',
    url='https://github.com/akaisuisei/concierge-python',
    download_url='',
    license='MIT',
    install_requires=[
        'requests',
        'paho-mqtt',
        'events'
    ],
    keywords=['snips'],
    packages=['concierge_python'],
    include_package_data=True
)
