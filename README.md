# Default Automation Coding Assessment

## How to run the script
With Virtual environment:
```bash
# Create new virtual environment
virtualenv -p /usr/bin/python3 default

# Activate the virtual environment
. ./default/bin/activate
```

```bash
# Install required python modules
pip install -r requirements.txt

# Run scraping script
python main.py
```

_* At the end of execution, a file named Clutch.csv will be created in the same folder with all final data_