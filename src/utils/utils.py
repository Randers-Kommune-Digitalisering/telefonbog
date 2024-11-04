import sys
import logging


# Logging configuration
def set_logging_configuration():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(name)s - %(module)s:%(funcName)s - %(message)s', datefmt='%d-%m-%Y %H:%M:%S')


def get_cpr_list(text):
    if text:
        text = ''.join(text.split())
        cpr_list = text.split(',')
        if not cpr_list[-1]:
            cpr_list.pop()
        if all(verify_cpr(cpr) for cpr in cpr_list):
            cpr_list = [cpr.replace('-', '') for cpr in cpr_list]
            return cpr_list


def verify_cpr(cpr):
    cpr = cpr.replace('-', '')
    return cpr.isdigit() and len(cpr) == 10


def markdown_template(name, user, deaprtment, email, phone, mobile):
    return f"""
        >
        |Navn|DQ-nummer|Afdeling|
        |-|-|-|
        |{name}|{user}|{deaprtment}|
        >
        |E-mail|Telefon|Mobil|
        |-|-|-|
        |{email}|{phone}|{mobile}|
    """
