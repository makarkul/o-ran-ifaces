# asn1extract.py
This script is intended to extract ASN.1 definitions of various protocol elements from O-RAN specifications. The specifications uploaded as samples are obtained from [this](https://orandownloadsweb.azurewebsites.net/specifications) site and subject to O-RAN Alliance IPR policies. Please consuult appropriate documents for the same.
# Usage
This utility requires Python's `docx2txt` package which can be installed as `pip3 install docx2txt`. After installation use the script as:
```
python3 asn1extract.py file1 [file2, file3 ..]
```
The specification files above should have the naming convention as in O-RAN distributed files as: `O-RAN.WG[%d].[%section]-[%release]-[%version].docx`. Only `docx` file extension is recognized as of now and `pdf` support is underway. The script generates one file per container

# Bugs, Errors
Please report using the issues on GitHub
