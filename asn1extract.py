'''
This script is intended to extract ASN.1 definitions of various protocol 
elements from O-RAN specifications. The specifications uploaded as samples are 
obtained from this site and subject to O-RAN Alliance IPR policies.  Please 
consult appropriate documents for the same.

Copyright (c) 2024-25 Makarand Kulkarni (makarand.kulkarni@saankhyalabs.com)
'''
import re
import sys

from enum import Enum

import docx2txt

class State(Enum):
    '''
    Values for 'state' of the Parser. Parser is initially in 'IDLE' state until 
    it encounters '-- ASN1START' string in it's input wherein it moves to state
    'PARSING' It continues to be in 'PARSING' until it encounters string 
    '-- ASN1STOP' in its input
    '''
    ASN1_IDLE = 0
    ASN1_PARSING = 1
    ASN1_ERROR = 2

class Parser:
    '''
    class for parsing the docx files which contain ASN1 specifications. 
    '''
    def __init__(self):
        self.state = State.ASN1_IDLE
        self.ofp = None
        self.pvstring = None

    def load_file(self, filename):
        '''
        loads the docx file into internal structures for processing, first 
        convert the file into txt format and split the intpu into lines it then
        finds the protocol (E2SM, E2AP etc) and version from the first line of 
        the input
        '''
        text = docx2txt.process(filename)

        lines = [i for i in text.split("\n") if i]
        r = re.compile(r'(O-RAN.WG\d.)([a-zA-Z,0-9]*)-([a-zA-Z,0-9,\-,\.]+)')
        mo = r.search(lines[0])
        self.pvstring = (mo.group(2), mo.group(3))

        return lines

    def write_line(self, line):
        ''' writes line to ASN1 file *only* in parsing state, else ignore '''
        if self.state == State.ASN1_PARSING:
            print(line, file=self.ofp)

    def process_line(self, this, prev=""):
        '''
        Implement the statemachine for the parser by handling each line based on
        the contents. Causes state transitions on encountering special strings 
        as described in the State enum above

        Stores the extracted modules in separate files bearing the module name 
        and other information about protocol and versions
        '''
        self.write_line(this)

        if this == '-- ASN1START':
            if self.state == State.ASN1_IDLE:
                self.state = State.ASN1_PARSING
                self.ofp = open(self.pvstring[0] +
                                    "-" + 
                                    "-".join(prev.split()[1:]) + 
                                    "-" + self.pvstring[1] + 
                                    ".asn", 
                                "wb")
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
        '''
        Load the lines of file in memory and process each line. Since we are 
        state dependent need to keep track of previous line (Suggest a better 
        way to do this?)
        '''
        lines = self.load_file(filename)
        prev = lines[0]
        for line in lines[1:]:
            prev = self.process_line(line, prev)

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print(f"Usage: {sys.argv[0]} file1 [file2 ..]")
        sys.exit(1)

    for doc in sys.argv[1:]:
        try:
            Parser().parse_file(doc)
        except Exception as e:
            print(f"{sys.argv[0]}: Error parsing file {doc} ({e})")
