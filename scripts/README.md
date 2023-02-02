# Scripts

requesting reference data from the usno dataservice from https://aa.usno.navy.mil/calculated/positions/topocentric 


- ```gather_reference_data.py``` implements
    - generating a url for a specific request
    - parse the results
    - write the data to logfiel
    - generate random parameters
    - run consecutively for large datasets.
- the file ```response.txt``` contains a sample response from the API and was the testcase for parsing the data
- the file ```log_reference_test.csv``` is a logfile, that contains some data, that was requested while testing. It serves as a reference for what output the script generates.
- 