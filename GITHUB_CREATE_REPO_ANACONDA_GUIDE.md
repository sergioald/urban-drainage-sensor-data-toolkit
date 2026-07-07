# Create the GitHub repository from Anaconda

This guide assumes you are working on Windows with Anaconda Prompt or PowerShell
inside an Anaconda environment.

Recommended repository name:

```text
urban-drainage-sensor-data-toolkit
```

Recommended short GitHub description:

```text
Urban drainage sensor-data QA/QC toolkit for private telemetry auditing, automated reporting, and optional anomaly screening with synthetic examples.
```

Recommended topics:

```text
python
sensor-data
data-quality
qaqc
time-series
anomaly-detection
environmental-monitoring
urban-drainage
research-software
engineering-data
```

## 1. Unzip the repository package

Unzip `urban-drainage-sensor-data-toolkit-final.zip` somewhere local, for example:

```text
C:\Users\Sergio\GitHub\urban-drainage-sensor-data-toolkit
```

Do not unzip it inside your private PVS OneDrive folder.

## 2. Open Anaconda Prompt

Start Anaconda Prompt, then go to the repository folder:

```bat
cd /d C:\Users\Sergio\GitHub\urban-drainage-sensor-data-toolkit
```

## 3. Create a clean environment

Use a new environment rather than your `meander-morphology` environment:

```bat
conda create -n urban-drainage-qaqc python=3.11 -y
conda activate urban-drainage-qaqc
```

## 4. Install the package locally

```bat
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

If the optional dev extra does not install on your machine, use:

```bat
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
python -m pip install -e .
```

## 5. Run checks

```bat
python -m pytest -q
python examples/ml/run_anomaly_demo.py
```

Optional:

```bat
ruff check .
```

## 6. Initialise Git locally

```bat
git init
git status
git add .
git commit -m "Initial public release"
```

## 7. Create the empty GitHub repository

In GitHub:

1. Go to `https://github.com/new`
2. Repository owner: `sergioald`
3. Repository name: `urban-drainage-sensor-data-toolkit`
4. Description: use the text above
5. Visibility: Public
6. Do not add README, .gitignore, or license from GitHub, because they are already included in this package
7. Click **Create repository**

## 8. Link local repo to GitHub and push

Replace the URL below only if you choose a different repository name:

```bat
git branch -M main
git remote add origin https://github.com/sergioald/urban-drainage-sensor-data-toolkit.git
git push -u origin main
```

## 9. After upload

Check the GitHub page:

- README renders correctly
- no private PVS files appear
- no `INPUT/`, `DATA/`, `REPORT/`, `OUTPUT/`, private samples, tokens, pickles, or credentials were uploaded
- GitHub Actions runs successfully

## Do not upload

Never commit these private/local folders or files:

```text
INPUT/
DATA/
REPORT/
OUTPUT/
PRIVATE_SAMPLE*/
private_audit*/
private_report*/
credentials.json
*token*
*.pickle
*.pkl
TOPO/
TEMP/
```

## Optional private local use

After the public repo is created, you can use it locally with private data:

```bat
urban-drainage-qaqc audit --input "C:/Users/Sergio/OneDrive - University of Edinburgh/PVS/DATA" --output private_audit
```

Keep all private outputs outside Git or in ignored folders.
