#!/usr/bin/env python
import argparse
import json
from pathlib import Path
from multiprocessing.pool import Pool
import pandas as pd
from pyfiglet import Figlet
from colorama import init, Fore, Style
init()

from teireader import TEIFile
from ctsreader import CTSFile

# Simple CLI for input directory and output filename 
def set_up_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('inputdir', help="Name of input directory containing TEI XML files. Directory name will also be used for output filenames in /output")
    return parser

# Scan directory for XML files (excluding CTS metadata), return paths
def all_teis(input_dir = ''):
    all_xmls = sorted([_ for _ in Path(input_dir).glob('**/*.xml')])
    all_teis = []
    for item in all_xmls:
        if "__cts__.xml" not in item.name:
            all_teis.append(item)
    return all_teis

# Scan directory for CTS metadata files, return paths
def all_cts(input_dir = ''):
    return sorted([_ for _ in Path(input_dir).glob('**/__cts__.xml')])

# Parse XML using TEIFile, return content
def tei_to_csv_entry(tei_file):
    tei = TEIFile(tei_file)
    print(Style.DIM + f"✓ Handled {tei_file}" + Style.RESET_ALL)
    return tei.basename(), tei.filepath(), tei.idno('PTA'), tei.idno('CPG'), tei.idno('BHGn'), tei.idno('Aldama'), tei.idno('Pinakes-Oeuvre'), tei.date, tei.title, tei.text, tei.licence, tei.revisiondate, tei.revisionauthor

# Parse CTS XML using TEIFile, return content
def cts_to_csv_entry(cts_file):
    cts = CTSFile(cts_file)
    print(Style.DIM + f"✓ Handled {cts_file}" + Style.RESET_ALL)
    return cts.filepath(), cts.urn, cts.textgroup

def main():
    parser = set_up_argparser()
    args = parser.parse_args()
    outputname = str(args.inputdir)
    
    # Generate list of TEI XML file paths in given input directory
    teis = all_teis(args.inputdir)

    # Generate list of CTS XML file paths in given input directory
    cts = all_cts(args.inputdir)

    f = Figlet(font='slant')
    print(f.renderText('TEI 2 JSON'))

    # Parse TEI XML into list using multi-threading
    pool = Pool()
    print(Fore.CYAN + "✓ Starting TEI parsing" + Style.RESET_ALL)
    csv_entries_tei = pool.map(tei_to_csv_entry, teis)
    print(Fore.GREEN + "✓ Completed TEI parsing" + Style.RESET_ALL)

    # Parse CTS XML into list using multi-threading
    pool_cts = Pool()
    print(Fore.GREEN + "✓ Starting CTS parsing" + Style.RESET_ALL)
    csv_entries_cts = pool_cts.map(cts_to_csv_entry, cts)
    print(Fore.GREEN + "✓ Completed CTS metadata parsing" + Style.RESET_ALL)

    # Create Pandas dataframe with TEI list data
    df_tei = pd.DataFrame(csv_entries_tei, columns=['filename', 'filepath', 'PTA', 'CPG', 'BHGn', 'aldama', 'pinakes', 'date', 'title', 'text', 'licence', 'revision_date', 'revision_author'])
    print(Fore.CYAN + "✓ Created Pandas dataframe for TEI data" + Style.RESET_ALL)

    # Create Pandas dataframe with CTS list data
    df_cts = pd.DataFrame(csv_entries_cts, columns=['filepath', 'urn', 'textgroup'])
    print(Fore.CYAN + "✓ Created Pandas dataframe for CTS metadata" + Style.RESET_ALL)

    # Merge TEI and CTS dataframes
    try:
        df_results = pd.merge(df_tei, df_cts)
    except:
        print(Fore.RED + "Error merging TEI and CTS dataframes" + Style.RESET_ALL)
    else:
        pass

    # Generate CSV from list data
    try:
        df_results.to_csv("output/%s.csv" %outputname, index=False)
    except:
        print(Fore.RED + "Error creating CSV output file" + Style.RESET_ALL)
    else:
        print(Fore.CYAN + "✓ Generated output CSV file: 'output/%s.csv'" %outputname, Style.RESET_ALL)

    # Generate JSON from list data
    try:
        json = df_results.to_json(orient='index')
        open("output/%s.json" %outputname,"w").write(json)
    except:
        print(Fore.RED + "Error creating JSON output file" + Style.RESET_ALL)
    else:
        print(Fore.CYAN + "✓ Generated output JSON file: 'output/%s.json'" %outputname + Style.RESET_ALL)

if __name__ == '__main__':
    main()
