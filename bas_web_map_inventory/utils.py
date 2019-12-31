# Exempting Bandit security issue (Consider possible security implications associated with subprocess module)
#
# Long term we want to avoid this but current usage is not a risk as we don't allow user input with subprocess calls
import subprocess  # nosec

from enum import Enum
from tempfile import NamedTemporaryFile
from typing import List

from importlib_resources import path as resource_path

# Exempting Bandit security issue (Using lxml.etree.parse to parse untrusted XML data)
#
# see specific reasons below
# noinspection PyUnresolvedReferences
from lxml import etree  # nosec


class OGCProtocol(Enum):
    """
    Represents various OGC standards
    """

    WMS = "wms"


def validate_ogc_capabilities(
    ogc_protocol: OGCProtocol, capabilities_url: str, multiple_errors: bool = False
) -> List[str]:
    """
    Validates a given OGC GetCapabilities document/response

    Supported OGC standards/protocols:
    * WMS (1.3)

    This method uses the `lxml` module to fetch the GetCapabilities response (typically from a HTTP endpoint) and
    validate it one of two modes, depending on whether this method should return on the first error encountered
    (default) or collect and return all validation errors.

    If you expect an endpoint to be valid, and are validating it as a pre-caution, the 'first error' mode is recommended
    as it's faster and simpler. If you don't know if the endpoint will be valid the 'all errors' mode is recommended as
    it's more useful to return all the errors to the user so they can judge what to do next. Otherwise they have to keep
    validating until they run out of errors, which can't be predicted.

    In 'first error' mode, `lxml` is used for validation. In 'all errors' mode the `xmllint` command line utility is
    used instead as lxml cannot capture multiple errors (due the implementation of underlying libxml library). In both
    modes endpoints are checked against XML Schemas from http://schemas.opengis.net (and so ultimately should agree).

    Currently errors from both modes are returned as is structured as a list. The format of errors does vary between
    modes and is not currently abstracted by this method due to the range and complexity of the validation errors that
    may arise (i.e. it's better for the user to parse the errors themselves). Both formats do include the line number
    however.

    Where `xmllint` is used ('all errors'), the GetCapabilities response is saved as a temporary file. This file is
    managed by python and removed automatically. It's name is dynamically/randomly generated but is stripped from error
    output as it would otherwise cause unit tests to fail. This name should therefore be ignored, however other
    information, such as the line number, is relevant and should match up with the GetCapabilities response (e.g. if
    viewed in a browser).

    :param ogc_protocol: The OGC protocol to validate the Get Capabilities document against, specified as a member from
    an enumeration of supported protocols
    :param capabilities_url: Path to Get Capabilities document/response, can be any form supported by lxml including a
    file or HTTP endpoint
    :param multiple_errors: Whether to fail at the first validation error encountered or return all errors at once

    :return: A list of validation errors, empty if the GetCapabilities is valid
    """
    if ogc_protocol == OGCProtocol.WMS:
        schema_file = "wms-1.3.0.xsd"
    else:
        raise ValueError("Invalid or unsupported OGC protocol")

    with resource_path("bas_web_map_inventory.resources.xml_schemas", schema_file) as schema_file_path:
        schema = etree.parse(str(schema_file_path)).getroot()
    validator = etree.XMLSchema(schema)

    # Exempting Bandit security issue (Using lxml.etree.parse to parse untrusted XML data)
    #
    # Only URLs added for data sources will be checked by this method. It is assumed such data sources will either be
    # operated by us or otherwise trusted enough to added to this inventory, therefore there should be a low risk of
    # them containing a vulnerability.
    capabilities_instance = etree.parse(capabilities_url).getroot()  # nosec

    if not multiple_errors:
        try:
            validator.assertValid(capabilities_instance)
            return list()
        except etree.DocumentInvalid as e:
            return [e.args[0]]
    else:
        with NamedTemporaryFile() as capabilities_instance_file:
            capabilities_instance_file.write(etree.tostring(capabilities_instance, pretty_print=True))

            try:
                with resource_path("bas_web_map_inventory.resources.xml_schemas", schema_file) as schema_file_path:
                    # Exempting Bandit security issue (subprocess call with shell=True identified)
                    #
                    # The file passed to this method is taken from the URL given, which will be for a data source we
                    # have added. It is assumed such data sources will either be operated by us or otherwise trusted
                    # enough to added to this inventory, therefore there should be a low risk of them containing a
                    # vulnerability.
                    subprocess.run(  # nosec
                        [f"xmllint --noout --schema {str(schema_file_path)} {capabilities_instance_file.name}"],
                        shell=True,
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )

                    # Return empty errors list
                    return list()
            except subprocess.CalledProcessError as e:
                return _process_xmllint_errors(error=e.stderr.decode(), file_name=capabilities_instance_file.name)


def _process_xmllint_errors(error: str, file_name: str) -> List[str]:
    """
    Processes errors returned by `xmllint` CLI tool

    Error output is broken down into individual errors, with blank and summary lines removed.
    Individual errors are formatted to remove potentially inconsistent output, such as file names.

    This is a standalone method to aid in mocking during testing.

    :param error: raw output from xmllint tool
    :param file_name: name of the file passed to xmllint

    :return: list of formatted errors
    """
    error_lines = error.split("\n")
    if error_lines[len(error_lines) - 1] != "":
        raise RuntimeError("xmllint error - error output is not recognised (no trailing new line)")
    error_lines.pop()
    if error_lines[len(error_lines) - 1] != f"{file_name} fails to validate":
        raise RuntimeError("xmllint error - error output is not recognised (no final validation status)")
    error_lines.pop()

    # Strip temporary file name from errors as this confuses tests
    for i, error_line in enumerate(error_lines):
        error_lines[i] = error_line.replace(file_name, "line")

    return error_lines


def build_base_data_source_endpoint(data_source: dict) -> str:
    """
    Shared method to construct a base URL for a data source

    If a HTTPS is used set the protocol is set to HTTPS.

    :param data_source: data source information
    :return: fully qualified URL for data source
    """
    protocol = "http"
    if data_source["port"] == "443":
        protocol = "https"

    return f"{protocol}://{data_source['hostname']}:{data_source['port']}"
