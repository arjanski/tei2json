# TEI2JSON
📁 Batch transform/edit TEI XML files to JSON (and CSV) using [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/index.html) and [Pandas](https://pandas.pydata.org/) for further (data science) processing, then serve output via REST API using [FastAPI](https://fastapi.tiangolo.com/).

TEI2JSON is a fork of [teitocsv](https://github.com/komax/teitocsv), yet adding some additional functionality while stripping other features:

- Recursive scanning of TEI input directory (= nested folders)
- Additional routine to deal with [CTS XML metadata](http://cts.informatik.uni-leipzig.de/Canonical_Text_Service.html) files
- Separate Pandas dataframes for TEI and CTS data
- Jupyter Notebook as an interface for Pandas data manipulation
- Export to CSV as well as JSON
- Full-fledged REST API to serve JSON output (via [FastAPI](https://fastapi.tiangolo.com/))

## Install

**! Warning ! TEI2JSON is still experimental and very much WIP, so it is not suitable for production**

1. Create the virtual environment
```bash
$ python3 -m venv env
```

2. Activate the virtual environment
```bash
$ source env/bin/activate
```

3. Install packages
```bash
$ pip install --requirement=requirements.txt
```

## Usage

### Parse / serialize XML
Provide and input directory (e.g. 'data'). This directory name will also serve as the basename for CSV output files stored in `/output` (e.g. 'data.csv' and 'data.json'):

`python main.py data`

If successfull, you should find your CSV and JSON output files in the `/output` folder of your project.

### Using Pandas (via Jupyter Notebook)
tbd.

### Start FastAPI REST Server
To serve your resutlting JSON output locally, start FastAPI in the `/api` directory:

`uvicorn main:app --reload`

By default, your JSON output (stored in `/output`) will then be available on localhost at port 8000:

Localhost:
http://127.0.0.1:8000/

Automatic Swagger documentation for your data:
http://127.0.0.1:8000/docs

## How it works
Here's a quick summary of the different steps TEI2JSON takes to generate output from your TEI XML (or CTS) files.

### Scanning for input files
TEI2JSON recursively scans the given input directory for any .xml files:

`all_xmls = sorted([_ for _ in Path(input_dir).glob('**/*.xml')])`

Note: CTS metadata files (with filenames `__cts__.xml`) will be parsed and analyzed separately, see CTS chapter below.

### TEI Parsing
BeautifulSoup makes it very convenient to parse any TEI node, text or attribute with minimal syntax. By default, TEI2JSON only parses very few nodes, but tries to make adding new nodes as easy as possible.

All parsing-related logic can be found in `teireader.py`. Here, we have a `TEIFile` class that already has various attributes and methods to parse TEI nodes, such as e.g.:

```py
    # <title> text
    @property
    def title(self):
        if not self._title and self.soup.title:
            self._title = self.soup.title.getText()
        return self._title
```

Adding new nodes is simply a question of extending the `TEIFile` class and then returning the desired attributes:

```py
# Parse XML using TEIFile, return content
def tei_to_csv_entry(tei_file):
    tei = TEIFile(tei_file)
    print(Style.DIM + f"✓ Handled {tei_file}" + Style.RESET_ALL)
    return tei.basename(), tei.filepath(), tei.date, tei.title
```

Make sure to adjust the header columns of the respective Pandas dataframe to match your desired fields:

```py
    # Create Pandas dataframe with TEI list data
    df_tei = pd.DataFrame(csv_entries_tei, columns=['filename', 'filepath', 'date', 'title'])
```

### CTS Parsing
tbd.

### Generating CSV and JSON output files
tbd.

### REST API
tbd.