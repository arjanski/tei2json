from dataclasses import dataclass
from pathlib import Path
from bs4 import BeautifulSoup
import re


# Create Soup for input file
def read_tei(tei_file):
    with open(tei_file, 'r') as tei:
        soup = BeautifulSoup(tei, 'lxml')
        return soup
    raise RuntimeError(Fore.RED + 'Error: Cannot generate a soup from file:',tei_file + Style.RESET_ALL)

# Return text element for given node
def elem_to_text(elem, default=''):
    if elem:
        return elem.getText()
    else:
        return default


@dataclass
class Person:
    firstname: str
    middlename: str
    surname: str

# TEIFile class holds attributes that are derived from passed TEI file
class TEIFile(object):
    def __init__(self, filename):
        self.filename = filename
        self.soup = read_tei(filename)
        self._urn = ''
        self._text = None
        self._textteaser = ''
        self._date = ''
        self._title = ''
        self._licence = ''
        self._revisiondate = ''
        self._revisionauthor = ''
        self._abstract = ''

    # Returns filename (without file type)
    def basename(self):
        stem = Path(self.filename).stem
        if stem.endswith('.tei'):
            return stem[0:-4]
        else:
            return stem

    # Returns relative file path
    def filepath(self):
        path = Path(self.filename).parent
        return str(path)

    # Returns <idno> 'type' attribute
    def idno(self, type):
        idno_elem = self.soup.find('idno', type=type)
        if not idno_elem:
            return ''
        else:
            return idno_elem.getText()

    # <title> text
    @property
    def title(self):
        if not self._title and self.soup.title:
            self._title = self.soup.title.getText()
        return self._title

    # <date> text
    @property
    def date(self):
        if not self._date and self.soup.date:
            self._date = self.soup.date.getText()
        return self._date

    # <licence> text
    @property
    def licence(self):
        if not self._licence and self.soup.licence:
            self._licence = self.soup.licence.getText()
        return self._licence

    # <change> 'when' attribute
    @property
    def revisiondate(self):
        if not self._revisiondate and self.soup.change:
            self._revisiondate = self.soup.change['when']
        return self._revisiondate

    # <change> 'who' attribute
    @property
    def revisionauthor(self):
        if not self._revisionauthor and self.soup.change:
            self._revisionauthor = self.soup.change['who']
        return self._revisionauthor

    # <abstract> text
    @property
    def abstract(self):
        if not self._abstract:
            abstract = self.soup.abstract.getText(separator=' ', strip=True)
            self._abstract = abstract
        return self._abstract

    # <author> texts
    def authors(self):
        authors_in_header = self.soup.analytic.find_all('author')

        result = []
        for author in authors_in_header:
            persname = author.persname
            if not persname:
                continue
            firstname = elem_to_text(persname.find("forename", type="first"))
            middlename = elem_to_text(persname.find("forename", type="middle"))
            surname = elem_to_text(persname.surname)
            person = Person(firstname, middlename, surname)
            result.append(person)
        return result

    # <text> text (parsed as string)
    @property
    def text(self):
        if not self._text:
            divs_text = []
            for div in self.soup.body.find_all("div"):
                # div is neither an appendix nor references, just plain text.
                # if not div.get("type"):
                div_text = div.get_text(separator=' ', strip=True)
                divs_text.append(div_text)

            plain_text = " ".join(divs_text)
            self._text = plain_text
        return self._text

    # Text teaser: first 200 characters of <text>
    @property
    def textteaser(self):
        if not self._text:
            divs_text = []
            for div in self.soup.body.find_all(subtype="section"):
                div_text = div.get_text(separator=' ', strip=True)
                divs_text.append(div_text)

            plain_text = " ".join(divs_text)
            self._text = plain_text[:200].rstrip()
            re.sub('\s+',' ',self._text)
        return self._text



