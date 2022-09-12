from datetime import datetime

from fhirclient.models import coding


def generate_code(coding: coding.Coding) -> dict:
    code = {
        "@code": coding.code,
        "@displayName": coding.display,
        "@codeSystemName": coding.system,
    }

    return code


def templateId(root: str, extension: str) -> list:
    """
    takes root and extensions and returns list for proper
    ccda formatting
    """
    template = [{"@root": root}, {"@root": root, "@extension": extension}]

    return template


def date_helper(isodate):
    """
    takes iso string and returns to format valid for ccda

    """
    new_date = datetime.strptime(isodate[:10], "%Y-%m-%d").strftime("%Y%m%d")

    return new_date
