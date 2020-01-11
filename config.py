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

# App Name
APP_NAME = "Could Try Harder"
APP_VERSION = "1.0"

# Location to store saved data
DATA_FOLDER = "./data/"

# Default window size
DEFAULT_WINDOW_SIZE = "800x600"

# Pronouns: these follow the form: [subjective-pronoun, objective-pronoun, possesive-adj, possessive-pronoun]
# TODO add gender neutral option
PRONOUNS = {
    'male': ['he', 'him', 'his', 'his', 'himself'],
    'female': ['she', 'her', 'her', 'hers', 'herself']
}

# Custom style rules for the comments. These are tuples which get passed to
# re.sub() and are case-insensitive to catch more potential typos. E.g. 'CLaSs
# NiNE' gets corrected to 'Year 9'
STYLE_RULES = [
    # Class 1-6
    ("(class|year) *(1|one)", "Class 1"),
    ("(class|year) *(2|two)", "Class 2"),
    ("(class|year) *(3|three)", "Class 3"),
    ("(class|year) *(4|four)", "Class 4"),
    ("(class|year) *(5|five)", "Class 5"),
    ("(class|year) *(6|six)", "Class 6"),

    # Year 7-12
    ("(class|year) *(7|seven)", "Year 7"),
    ("(class|year) *(8|eight)", "Year 8"),
    ("(class|year) *(9|nine)", "Year 9"),
    ("(class|year) *(10|ten)", "Year 10"),
    ("(class|year) *(11|eleven)", "Year 11"),
    ("(class|year) *(12|twelve)", "Year 12"),

    # Capitalise languages
    ("japanese", "Japanese"),
    ("german", "German"),

    # Semester should be lower case
    ("semester", "semester"),

    # Except for the following special cases
    ("(semester) *(1|one)", "Semester 1"),
    ("(semester) *(2|two)", "Semester 2"),

    # Term 1-4
    ("(term) *(1|one)", "Term 1"),
    ("(term) *(2|two)", "Term 2"),
    ("(term) *(3|three)", "Term 3"),
    ("(term) *(4|four)", "Term 4"),

    # Misc.
    ("bookwork", "book work"),
    ("classwork", "class work"),
    ("exam(?!ination)", "examination")
]

PLACEHOLDER_INSTRUCTIONS = """
Placeholders:
<name> = Student name
<sp> = subjective pronoun e.g. he, she or they
<op> = objective pronoun e.g. him, her or them
<pa> = possesive adjective e.g. his, her or their project
<pp> = possesive pronoun e.g. the project was his, hers or theirs
<rp> = reflexive pronoun e.g. himself, herself or themself
"""

STYLESHEET = """
QLabel[styleClass="heading"] {
    font-weight:bold;
}

QLabel[styleClass="title"] {
    font-weight:bold;
    background-color: #fff;
    border-radius:10px;
    padding:10px;
}
"""
