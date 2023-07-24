# BTSpeech
Python scripts to extract textual data from unstructured parliamentary protocol files (XML) provided by the German Bundestag. For all protocols from the 19th legislative period onwards please use my new repository BTSpeech2.0.

Python 3 scripts to extract speech texts from XML data provided by [Bundestag Open Data Service](https://www.bundestag.de/services/opendata "Bundestag Open Data") for election periods where the provided XMLs do not follow a structured form (true for datasets of the 19th election period and earlier). Due to the unstructured nature of the provided data, the speech extraction will not always be 100% accurate. However, the quality of the generated dataset should be sufficient for performing quantitative text analysis.

### Usage
First, run:
```
python process_xmls.py <folder_with_xmls> <output_folder>
```
This will extract the individual speeches from every XML file in *folder_with_xmls* and write the speaker's name, their fraction, date of the speech and the speech text to a json file in *output_folder*.

Then, to generate a CSV dataset from these json files, run the second script:
```
python process_jsons.py <output_folder> <output_dataset.csv>
```
with *output_folder* as the folder where the json files were generated previously.

## Requirements
- Python >= 3.6
- Pandas
