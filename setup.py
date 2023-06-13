from setuptools import find_packages
from setuptools import setup

with open('requirements.txt') as f:
    content = f.readlines()
requirements = [x.strip() for x in content if 'git+' not in x]

setup(
    name='WalkieLookie',
    version="1.0",
    description="Personalized Walking Tour Recommender for Berlin based on your location and time availability",
    packages=find_packages(),
    install_requires=requirements,
    # include_package_data: to install data from MANIFEST.in
    include_package_data=True,
    scripts=['scripts/download_berlin_graph_data.py'],
    zip_safe=False)
