from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

import xmltodict


def convert_mime(ccda: dict):
    """
    Takes CCDA and converts it to XOP for sending via SOAP

    Args:
        ccda: dictionary created by convert bundle

    Returns:
        XOP infoset
    """

    ccda_xml = xmltodict.unparse(ccda, pretty=True)

    msg = MIMEMultipart()
    xml = MIMEBase("application", "xop+xml")
    xml.set_payload(ccda_xml)
    msg.attach(xml)

    return msg.as_string()
