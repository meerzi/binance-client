# Pre-requisite Software packages and platform

`bina-data-fetcher-client.py` module is tested with py3 on linux-distros CentOs 7.9

- python3
- pip3

Run below command to install pip3

`sudo yum install python3-pip -y`

Install python packages required to run client module

`pip3 install -r requirements.txt`

# Run script to fetch the result

`python3 bina-data-fetcher-client.py`

# Improvement points
- Add flake8 to check python coding syntax
- Add unittets for each function preferred using pytest module
- Add functional test
- Live Dashboard to show all Q1-Q4 data constantly, refresh interval 1 sec or 1 minute
- Prepare CI/CD to automate the repository update to run  unit tests, functional tests, building container image and its deployment
- Prepare Grafana dashboard to show the output of Q5 accessibility using prometheus metrics format by adding query for panel
