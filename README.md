# WalkieLookie
An app to recommend walking tours in Berlin based on your location, time availability and personal preferences.

## Installation

### Clone repository
1. Open the Terminal.
2. Change the current working directory to the location where you want the cloned directory
3. Clone the repository using
```bash
git clone git@github.com:Heity94/WalkieLookie.git
```
4. Change into the cloned directory
```bash
cd WalkieLookie/
```
### Create and activate virtual environment
To avoid dependency issues we recommend to create a new virtual environment to install and run our code. Please note, that in order to follow the next steps [pyenv](https://github.com/pyenv/pyenv) and [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv) need to be installed.
1. Create a virtual environment using `pyenv virtualenv`. You can of course use another name as `aug_walkie_lookiehs_env` for the environment.
```bash
pyenv virtualenv walkie_lookie
```
2. Optionally: Use `pyenv local` within the AugmentedHierarchicalShrinkage source directory to select that environment automatically:
```bash
pyenv local walkie_lookie
```
From now on, all the commands that you run in this directory (or in any sub directory) will be using `walkie_lookie` virtual env.

### Install the package
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install WalkieLookie.
```bash
pip install --upgrade pip
pip install -e .
```

### Download graph data of Berlin
Execute the script to download the graph data of Berlin. You need to run this script only once. The download might take a while.
```bash
python scripts/download_berlin_graph_data.py
```

## Usage

After successful installation and download of the grtaph data you should be able to use our app by starting the streamlit application.
```bash
streamlit run app/app.py
```
From there on you can choose your starting address (must be within the boundaries of Berlin), your time availability for the walk, and if your route should bring you back to your starting place.
[Scrrenshot_Application](/app/Dashboard.png)



## Structure of the repository
The general structure of this repository is detailed below
```bash
.
├── TreeModelsFromScratch   # Python module for decision tree and random forest models
├── scripts                 # Script to run predictive performance experiment
├── raw_data                # Datasets used for training and evaluating the artifact
├── notebooks               # Notebooks to run experiments, recreate original results from HS paper and compare self-developed models with sklearn and imodels implementation
├── data                    # Experimental results, including trained models, simulation settings, and created plots
├── MANIFEST.in
├── README.md
├── .gitignore
├── requirements.txt
└── setup.py
```
