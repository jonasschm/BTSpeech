import re
import json
import glob
import os
import sys
from typing import Dict
import xml.etree.ElementTree as ET


PARTYS = ["AFD", "SPD", "DIE LINKE", "CDU/CSU", "BÜNDNIS 90/DIE GRÜNEN", "FDP"]
REGEX_START_SPEECH = r"^(\D+) \((.+)\):"
REGEX_END_SESSION = r"^\(Schluss: .*\)$"


def get_date_from_xml(filename: str) -> str:
    """
    Extract date from the XML file, denoted by DATUM node
    """
    root = ET.parse(filename).getroot()
    date_node = root.find(".//DATUM")
    if not isinstance(date_node, ET.Element) or not isinstance(date_node.text, str):
        raise RuntimeError(f"Cannot find DATUM tag in {filename}")
    return date_node.text


def extract_speech_text(filename: str, start_line: int) -> str:
    """
    Extract speech text, beginning at start line, until next speech starts
    """
    ret = ""
    content = open(filename, encoding="utf-8").readlines()[start_line:]
    for line in content:
        match = re.match(REGEX_START_SPEECH, line)
        if match:
            # Seems to be the beginning of the next speech -> stop
            break
        match = re.match(REGEX_END_SESSION, line)
        if match:
            # Seems to be the end of the session -> stop
            break

        if line.startswith("Deutscher Bundestag "):
            # Likely to be some annotation we want to ignore
            continue

        if line.endswith(":\n"):
            # Not a match per speech begin criteria, but still a ":" detected -> someone else is talking! >:(
                break

        # Postprocessing of an individual line
        line = line.strip().replace(" .", ".").replace("–", "-")
        was_break = False
        if line.endswith("-"):
            was_break = True
            line = line[:-1]
        if was_break:
            ret += line
        else:
            ret += line + " "

    # Postprocess complete text
    ret = re.sub(r"\(.*?\)", "", ret)  # Remove brackets and everything inside of them

    # Remove artifacts at the end of the speech (everthing after the last sentence)
    words = [word for word in ret.split(" ") if word]
    while True:
        try:
            if not words[-1].endswith(".") and not words[-1].endswith("?") and not words[-1].endswith("!"):
                del(words[-1])
            else:
                break
        except IndexError as e:
            print(f"Skipping incomplete or malformatted speech: {ret}")
            return ""

    return " ".join(words)


def parse(filename: str) -> Dict:
    """
    Parse speech and metadata from an XML file.
    Returns a dictionary of the form:

    {
        "date",
        "file",
        "speeches": [{"name", "party", "text"}, ...]
    }
    """
    data_dict = {"file": filename, "speeches":[]}
    data_dict["date"] = get_date_from_xml(filename)

    with open(filename, encoding="utf-8") as fp:
        line_ctr = 0

        for line in fp:
            line_ctr += 1
            match = re.match(REGEX_END_SESSION, line)
            if match:
                break

            match = re.match(REGEX_START_SPEECH, line)
            if match:
                # Start of speech
                name = match.group(1).strip()
                party = match.group(2).strip()
                if party.lower() not in map(str.lower, PARTYS):
                    print(f"Discarded party {party}")
                    continue

                speech_dict = {}
                speech_dict["name"] = re.sub(r"\(.*?\)", "", name)
                speech_dict["name"] = speech_dict["name"].strip()
                speech_dict["party"] = party
                speech_dict["text"] = extract_speech_text(filename, line_ctr)

                # Probably not a speech when too short
                if len(speech_dict["text"]) < 200:
                    continue

                if data_dict["speeches"] and data_dict["speeches"][-1]["name"] == name and data_dict["speeches"][-1]["party"] == party:
                    # Same person -> continue speech
                    data_dict["speeches"][-1]["text"] += speech_dict["text"]
                else:
                    # New speaker
                    data_dict["speeches"].append(speech_dict)

    return data_dict


def print_usage():
    print(f"Usage: {sys.argv[0]} <input_folder> <output_folder>")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print_usage()
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isdir(input_dir):
        print(f"No such directory: {input_dir}")
        sys.exit(1)

    if not os.path.isdir(output_dir):
        print(f"No such directory: {output_dir}")
        sys.exit(1)

    for xml in glob.glob(f"{input_dir}/*.xml"):
        print(f"Processing file {xml} ...")
        d = parse(xml)
        output_f = f"{output_dir}/" + os.path.basename(xml).replace(".xml", ".json")
        with open(output_f, "w", encoding="utf-8") as fp:
            json.dump(d, fp, indent=4, sort_keys=True, ensure_ascii=False)

    print("OK")
