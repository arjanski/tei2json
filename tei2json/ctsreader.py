from dataclasses import dataclass
from pathlib import Path
from bs4 import BeautifulSoup
import re


# Create Soup for input file
def read_cts(cts_file):
    with open(cts_file, 'r') as cts:
        soup = BeautifulSoup(cts, 'lxml')
        return soup
    raise RuntimeError('Cannot generate a soup from the input')

# Return text element for given node
def elem_to_text(elem, default=''):
    if elem:
        return elem.getText()
    else:
        return default

class CTSFile(object):
    def __init__(self, filename):
        self.filename = filename
        self.soup = read_cts(filename)
        self._urn = ''
        self._textgroup = ''

    def basename(self):
        stem = Path(self.filename).stem
        if stem.endswith('.tei'):
            # Return base name without tei file
            return stem[0:-4]
        else:
            return stem

    def filepath(self):
        path = Path(self.filename).parent
        return str(path)

    @property
    def urn(self):
        if not self._urn and self.soup.find('ti:work'):
            urn = self.soup.find('ti:work')
            urn = urn['urn']
            if urn:
                self._urn = urn
        if not self._urn and self.soup.find('ti:textgroup'):
            urn = self.soup.find('ti:textgroup')
            urn = urn['urn']
            if urn:
                self._urn = urn
        return self._urn

    @property
    def textgroup(self):
        if not self._textgroup and self.soup.find('ti:work'):
            textgroup = self.soup.find('ti:work')
            if textgroup.has_attr('groupurn'):
                self._textgroup = textgroup['groupurn']
        return self._textgroup
