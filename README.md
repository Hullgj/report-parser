# report-parser
Report Parser is the Ransomware Deployment Classifier
Requirements:
Python 2.7,
CasperJS,
PhantomJS

Example Run:
`python report_parser.py -v path/to/your/cuckoo/sandbox/json/reports/ path/to/output/file/output_file.json`

If you already have the output_file.json with parsed results. Then you can supply the '-s' or '--skip' flag to skip parsing the Cuckoo Sandbox reports.

This repository has sample reports in json-reports/. If you want the JSON reports for the ransomware sample analyses, extract them from the zip folder supplied with the Corpus in "RanDep Classifier/Cuckoo Reports/json-ransomware-reports.zip".

This can be run without any reports using the supplied JSON files as follows:
`python report_parser.py -v -s json-ransomware-reports/ docs/parse.json`
