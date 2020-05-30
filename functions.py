import re
from collections import OrderedDict
import datetime as dat
from datetime import date


DECIMALS_REGEX = re.compile(r"^\d*[.,]?\d*$")


def sanitize_text(raw_text):

    # Replace all non alphanumeric characters with some exceptions
    exceptions = " .,"
    filtered_text = re.sub(r'[^\w' + exceptions + ']', '', raw_text)

    # Eliminate multiple spaces
    filtered_text = re.sub(r'[\s]+', ' ', filtered_text)
    #Eliminate full stop
    filtered_text = re.sub(r'\.', ' ', filtered_text)

    # Strip out terminal and leading spaces
    return filtered_text.strip()


def sanitize_lowertext(raw_text):
    return sanitize_text(raw_text).lower()


def find_intent(user_input, intent_dict):
    """
        Takes in user_input and an OrderedDict of intents
        and returns the key of the intent if it finds any
        of the key's values in the user_input
    """
    print (intent_dict)

    for k in intent_dict.keys():
        print ("Searching key", k)
        for keyword in intent_dict[k]:
            if(user_input.find(keyword) >= 0):
                return k
    return 0


def generate_actions(intents):
    if(intents):
        return [{'text': x, 'trigger': x} for x in intents]


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def is_int_try(str):
    try:
        int(str)
        return True
    except ValueError:
        return False

def previous_quarter(ref):
    if int(ref.month) < 4:
        return dat.date(ref.year - 1, 12, 31)
    elif int(ref.month) < 7:
        return dat.date(ref.year, 3, 31)
    elif int(ref.month) < 10:
        return dat.date(ref.year, 6, 30)
    return dat.date(ref.year, 9, 30)
