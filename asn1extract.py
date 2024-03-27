import docx2txt
import re
import sys

from enum import Enum

class State(Enum):
    ASN1_IDLE = 0,
    ASN1_PARSING = 1,
    ASN1_ERROR = 2

class Parser:
    def __init__(self):
        self.state = State.ASN1_IDLE
        self.ofp = None
        self.pvstring = None

    def load(self, filename):
        text = docx2txt.process(filename)

        lines = [i for i in text.split("\n") if i]
        r = re.compile(r'(O-RAN.WG\d.)([a-zA-Z,0-9]*)-([a-zA-Z,0-9,\-,\.]+)')
        mo = r.search(lines[0])
        self.pvstring = (mo.group(2), mo.group(3))

        return lines

    def write_line(self, line):
        if self.state == State.ASN1_PARSING:
            print(line, file=self.ofp)

    def process_line(self, this, prev=""):
        self.write_line(this)

        if this == '-- ASN1START':
            if self.state == State.ASN1_IDLE:
                self.state = State.ASN1_PARSING
                self.ofp = open(self.pvstring[0] + 
                                    "-" + 
                                    "-".join(prev.split()[1:]) + 
                                    "-" + self.pvstring[1] + 
                                    ".asn", 
                                "w")
            else:
                raise Exception("Error: ASN1START encountered in parsing state")
        elif this == '-- ASN1STOP':
            if self.state == State.ASN1_PARSING:
                self.state = State.ASN1_IDLE
                self.ofp.close()
            else:
                raise Exception("Error: ASN1STOP encountered in non-parsing state")
        return this

    def parse_file(self, filename):
        lines = self.load(filename)
        prev = lines[0]
        for line in lines[1:]:
            prev = self.process_line(line, prev)

if __name__ == '__main__':
    for doc in sys.argv[1:]:
        try:
            Parser().parse_file(doc)
        except Exception as e:
            print(f"{sys.argv[0]}: Error parsing file {doc} ({e})")

