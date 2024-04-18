# LMT Statistics

## Overview
This is a simple python script that provides a summary of data from ILMT. It can be used as a web application, a standalone script or as a library.

## Usage
Install requirements:

```bash
python3 -m pip install -r requirements.txt
```
or
```bash
pip install -r requirements.txt
```

Then inside your python file:
```python
from main import LMT_Statistics

lmt = LMT_Statistics("path_to_your_file.csv")
# You can either catch the output from init() which is just dash.html.Div...
dashboard = lmt.init()

# Or launch a default dash web server
lmt.init(return_to_self=True)
lmt.run_server()
```

You can also just work in the main.py file.

## Generating data
You can generate more data to your csv file by using [ILMT Generator](https://github.com/SzymonSkrzypczyk/LMT_generator)

### How it works?
The answer to that question lies in the code. It is roughly documented inside the python script. For more information you can start a discussion on GitHub.

### Main contributors :)
- [Marek Chachlica](https://github.com/MarekChachlica)
- [Gabriel Pilch](https://github.com/GabrielPilch)
- [Szymon Skrzypczyk](https://github.com/SzymonSkrzypczyk)