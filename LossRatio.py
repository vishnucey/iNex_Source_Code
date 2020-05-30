from flask import *
from functions import *



RESET_KEYWORDS = ['reset', 'restart','stop','quit', 'main menu']
ERR_RESTRICT_CHOICE = "Please choose one of the above"


class LossRatio(object):
    print('in LossRatio')