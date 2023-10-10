from . import tokens as tokens_bx24


def verification(application_token):
    if application_token == tokens_bx24.get_secret("application_token"):
        return True
