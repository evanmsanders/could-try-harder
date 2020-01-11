# Could Try Harder - Simple report comment builder for teachers.
# Copyright (C) 2020 Evan M. Sanders
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
import os
import csv
import json
import re
from textblob import TextBlob
import config

def get_saved_list():
    """
    Get a list of saved class reports.
    Scans the data folder defined in config.DATA_FOLDER for json files and returns a list of strings containing the file names (but not extensions).

    Returns:
        list of strings
    """
    saved_list = []
    with os.scandir(config.DATA_FOLDER) as saved_files:
        for saved_file in saved_files:
            if saved_file.name.endswith('.json') and saved_file.is_file():
                # Append the filename without the extension
                saved_list.append(saved_file.name[:-5])
    return saved_list

def import_class_list(filename, subject_name):
    """
    Import a csv file of students and create a json save file.

    Params:
        filename: string containing the full path to the csv file
    """
    students = []

    # TODO: This should be handled by proper input validation in the GUI.
    # Remove everything except a-z, A-Z, 0-9, - and _ and space from subject_name
    subject_name = re.sub("[^a-zA-Z0-9-_\s]+", "", subject_name)
    # Now remove leading or trailing spaces
    # subject_name = re.sub("(?:^\s+)|(?:\s+$)", "", subject_name)
    subject_name = subject_name.strip()
    # Replace remaining spaces with -
    subject_name = subject_name.replace(" ", "-")

    # TODO: check if file exists

    try:
        with open(filename) as csvf:
            reader = csv.reader(csvf)
            for row in reader:
                students.append({
                    "first_name": row[0].strip(),
                    "last_name": row[1].strip(),
                    "gender": row[2].strip(),
                    "pronouns": [],
                    "comment": ""
                })
    except Exception as err:
        # TODO: better error handling here
        print(err)
        return False

    # Set up pronouns for each student
    # TODO support for non-binary gender field
    # support it.
    for student in students:
        if student['gender'] == 'Male':
            student['pronouns'] = config.PRONOUNS['male']
        else:
            # Female pronouns as default
            # TODO: gn pronouns as default
            student['pronouns'] = config.PRONOUNS['female']

    # Create the json file for the subject
    with open(str(config.DATA_FOLDER + subject_name + '.json'), 'w') as json_out:
        try:
            json.dump({
                "subject_name": subject_name,
                "intro_comment": "",
                "comment_bank": [],
                "students": students},
                json_out,
                indent=4)
        except Exception as err:
            #TODO better error handling here
            print(err)
            return False
    return True

def load(subject_name):
    """
    Loads comment banks, students and report comments from saved json file.

    Params:
        subject_name: string - matching a saved json file
    Returns:
        dict
    """
    class_reports = {}
    # Load saved json file
    try:
        with open(str(config.DATA_FOLDER + subject_name + '.json'), 'r') as json_in:
            class_reports = json.load(json_in)
    except Exception as err:
        # TODO better error handling here
        print(err)
    return class_reports

def save(subject):
    """
    Saves a subject dict to json file.

    Params:
        subject: dict
    Returns:
        Boolean
    """
    try:
        with open(str(config.DATA_FOLDER + subject['subject_name'] + '.json'), 'w') as json_out:
            json.dump(subject, json_out, indent=4)
    except Exception as err:
        # TODO better error handling here
        print(err)
        return False
    return True

def export(subject_name, filename):
    """
    Generates a text file of the report comments ready for transferring into student database or reporting system.

    Params:
        subject_name: string that matches a json saved file in config.DATA_FOLDER
        filename: file path for exported file
    Returns:
        Boolean
    """
    output = []
    subject = load(subject_name)
    if not subject:
        # TODO better error handling here
        print("Export failed - got an empty save file.")
        return False

    # Heading
    output.append("=" * 80)
    output.append("Report Comments for: " + subject_name)
    output.append("=" * 80)
    output.append("\n")

    # Add student names and comments
    for student in subject['students']:
        output.append("-" * 80)
        output.append(student['first_name'] + " " + student['last_name'])
        output.append("-" * 80)
        output.append(do_placeholders(subject['intro_comment'], student['first_name'], student['pronouns']) + " " + student['comment'])
        output.append("\n")

    # Collapse down to one string for export
    output = "\n".join(output)

    # TODO remove extra newlines?

    # Write prepared reports to specified file
    with open(str(filename), 'w') as txt_out:
        try:
            txt_out.write(output)
        except Exception as err:
            # TODO better error handling here
            print(err)
    return True

def delete(subject_name):
    """
    Deletes a saved json file from the config.DATA directory.

    Params:
        subject_name: string
    Returns:
        Boolean
    """
    try:
        os.remove(str(config.DATA_FOLDER + subject_name + '.json'))
    except Exception as err:
        # TODO better error handling here
        print(err)
        return False
    return True

def do_placeholders(text, name, pronouns):
    """
    Replace placeholders in a given string. Also fixes sentence capitalisation problems cause as a result.

    Pronoun codes are:
        <sp> - subjective pronoun e.g. "He" or "She"
        <op> - objective pronoun e.g. "Him" or "Her"
        <pa> - possesive adjective e.g. "his" or "her" "project"
        <pp> - possesive pronoun e.g. The project is his/hers.
        <rp> - reflexive pronoun e.g. "himself" or "herself"

    Params:
        text: a string containing pronoun codes to replace.
        name: string - student name
        pronouns: a list of custom pronouns in the form [subjective-pronoun, objective-pronoun, possesive-adjective, possesive-pronoun]

    Returns:
        string
    """
    text = text.replace('<name>', name)
    text = text.replace('<sp>', pronouns[0])
    text = text.replace('<op>', pronouns[1])
    text = text.replace('<pa>', pronouns[2])
    text = text.replace('<pp>', pronouns[3])
    text = text.replace('<rp>', pronouns[4])

    # TODO: add extra replacements for participles relating to "they" pronouns
    # TODO: do this automatically with TextBlob?

    text = _capitalise_sentences(text)

    return text

def do_style(text):
    """
    Apply replacement patterns defined in config. Also fixes an sentence capitalisation errors.

    Params:
        text: string

    Returns:
        string
    """
    for pattern, replacement in config.STYLE_RULES:
        # Case insensitive to cover more possible errors.
        text = re.sub(pattern, replacement, text, flags=re.I)

    # Recapitalise sentences to fix errors introduced.
    text = _capitalise_sentences(text)

    return text

def _capitalise_sentences(text):
    """
    Uses TextBlob to capitalise sentences.

    Params:
        text: string

    Returns:
        string: capitalised text
    """
    output = []
    blob = TextBlob(text)
    for sentence in blob.sentences:
        # Using .capitalize() removes capitalisation elsewhere in the
        # sentence, so instead capitalise the first letter only and then
        # append the rest of the sentence.
        output.append(str(sentence[:1].upper() + sentence[1:]))
    return " ".join(output)
