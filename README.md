[![build](https://github.com/JGCRI/bed/actions/workflows/build.yml/badge.svg)](https://github.com/JGCRI/bed/actions/workflows/build.yml)
[![docs](https://github.com/JGCRI/bed/actions/workflows/docs.yml/badge.svg)](https://github.com/JGCRI/bed/actions/workflows/docs.yml)
[![tests](https://github.com/JGCRI/bed/actions/workflows/test.yml/badge.svg)](https://github.com/JGCRI/bed/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/JGCRI/bed/branch/main/graph/badge.svg?token=2EWDAQI07B)](https://codecov.io/gh/JGCRI/bed)

## pytemplate

A template for a basic Python package with CI via GitHub actions and a JOSS paper template and action

### Using this template

Some version of the following, starting with the [Purpose](#purpose) section of this README, should be included in the README of your package.  The rest of this [Using this template](#using-this-template) section can be removed after you read it.

#### Building your Python package

The following are things to modify to make your Python package work for you:

- Change the version of your package in `pytemplate/__init__.py` which gets called in your `setup.py` file
- I like to start by installing my package in `develop` model in a clean virtual environment.  You can do this a bunch of ways depending on your preferences. After building my clean virutal environment, I navigate to the root of my cloned directory and run `python setup.py develop`.  Running in develop mode allows you to make changes to your package and execute them on the fly without having to reinstall it everytime.  
- You should now be able to open the Python prompt that you have your virtal environment built in and execute `import pytemplate` successfully.


#### Setting up your quickstarter Jupyter notebook

Assuming that you have your package and Jupyter installed, you can use the quickstarter notebook as a way to introduce folks to the key functionality of your package.  

You can do the following to link your virtual environment to your Jupyter notebook kernel:

- Install `ipykernel` in your virtual environment via:

    ```bash
    pip install ipykernel
    ```
    and run the following:
    ```bash
    ipython kernel install --name "<my-virtual-environment-name"
    ```

    At this point, you should be able to select your virtual environment within your Jupyter Lab environment.

    **NOTE**:  If you make changes to the source code of your package, you will need to restart the Jupyter kernel to have the change take effect in your Jupyter notebook.

#### Building your docs

To start install the following in your Python virutal environment:

```bash
pip install sphinx
pip install autodoc
```

There is no need to initialize Sphinx since I have included prebuilt directories.  However, if you want to know how to do this yourself, you can look up how to run `sphinx-quickstart` from within a prebuild `docs` directory.

All of the documentation is contained within the `docs` directory.  This directory contains the following:

- `Makefile`:  To generate the `build` directory and it's contents for the website for Unix
- `make.bat`:  To generate the `build` directory and it's contents for the website for Windows
- `.nojekyll`:  Used when we generate our documentation website via GitHub Pages to ensure Jekyll is not used.
- `source`:  Directory containing all information to build the website.  This is what is modified by you the user.  All documentation is built using ReStructuredText (.rst).
    - `conf.py`:  The Python file that controls how your documentation is built.
    - `index.rst`:  The blueprint of your website.
    - The following were generated by running the Sphinx autodoc tool to build an API documentation of the package from the docstrings for each class, method, and function:  `modules.rst`, `pytemplate.rst`, `pytemplate.tests.rst`.  These were generated by running:
    ```bash
    sphinx-apidoc -f -o source/ ../pytemplate/
    ```

To generate the documentation website files run the following from the `docs` directory if on a Mac or Linux maching (use the `make.bat` for Windows):

```bash
make html
```

This will build the website here:  `docs/build/html`  You can open this locally by double-clicking the `index.html` file.  Ultimately, the contents of the `docs/build/html` directory will be hosted on a separate `gh-pages` branch as we only want to keep the source docs in the code branches.  To setup a webpage after building your docs, do the following:

- Create a branch named `gh-pages` from what you have on `main`
- In your GitHub repo, navigate to `Settings` -> `Pages` and ensure that `Source` is set to `Deploy from branch` and that `gh-pages` is selected as the branch and that `/root` is the target directory.
- Copy the `docs/build/html` directory somewhere else on your machine (e.g., Desktop)
- Pull your new branch to your local repo via `git pull --all`, navigate to the root directory of your repository, and change branches to `gh-pages` (e.g., `git checkout gh-pages`)
- Remove everything from your repo when on the `gh-pages` branch.
- Copy the contents of the `html` directory you copied into the repo.
- Add an empty file named `.nojekyll` to the root directory with the HTML contents.
- Add, commit, and push this to `gh-pages`.
- Change directories back to `main` or your working branch.

If you navigate back to `Settings` -> `Pages` you will now see your web address that has been deployed.  This repos is:  https://jgcri.github.io/pytemplate/
Copy this address and navigate back the main GitHub repo page (e.g., https://github.com/JGCRI/pytemplate).  Click the gear in the `About` section in the top right of your page, paste in the link to your webpage, and click `Save changes`.

You now have a live documentation web page!  You can build custom sections that you can link to in the main README (these now only contain links to Goggle).

#### Your GitHub Actions

Your tests in the package will run via continuous integration from the `build.yml` action.  This is linked to the badge in your README.

#### Modifying your JOSS paper

I put a sample JOSS paper, bibliography, and figure in a directory named `paper` in the root.  This gets compiled to a PDF file so you can check formatting via this GitHub action:  `.github/workflows/draft-pdf.yml which creates a PDF as an artifact that you can download in the action.
This paper includes sample referencing as well.

### Purpose

`pytemplate` was created to make life easier when creating a new Python package.  It comes prebuilt with the following:
- A Python package
- A prebuilt example test suite
- A sample documentation directory and process using Sphinx
- A sample Journal of Open Source Software (JOSS) paper template directory
- A GitHub Action workflow for continous integration (CI)
- A GitHub Action workflow for building a PDF from the JOSS paper directory
- A quickstarter Jupyter notebook to introduce your package
- This README which contains specifics that are needed

### Installation

Since this package is a demo and contains no real code that produces something useful, you can simply use this repository to build your own by selecting it as a `Template` when building a new repository.  Then you can modify the contents to suit your needs.  You can also navigate directly to https://github.com/JGCRI/pytemplate, click the shiny green button that says `Use this template` and be on your way.

However, if you want to play around with this package to get used to how things are arranged, you can clone it locally via:

```bash
git clone https://github.com/JGCRI/pytemplate.git
```

### Check out a quickstart tutorial to run `pytemplate`

Run `pytemplate` using the quickstart tutorial:  [Quickstart Tutorial](www.google.com)

### Getting started

New to `pytemplate`?  Get familiar with what it is all about in our [Getting Started](www.google.com) docs!

### How to contribute

Whether you find a typo in the documentation, find a bug, or want to develop functionality that you think will make cerf more robust, you are welcome to contribute! See our [Contribution Guidelines](www.google.com)

### API reference

The reference guide contains a detailed description of the cerf API. The reference describes how the methods work and which parameters can be used. It assumes that you have an understanding of the key concepts. See [API Reference](www.google.com)