""" Simple flask server allowing AJAX requests to validate addresses using the USPS API. """
import json
import logging
import os
import urllib

import flask
import lxml.etree


USPS_API_URL = os.environ['USPS_API_URL']
USPS_USER_ID = os.environ['USPS_USER_ID']
APPLICATION = flask.Flask(__name__)
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    APPLICATION.logger.handlers = gunicorn_logger.handlers
    APPLICATION.logger.setLevel(gunicorn_logger.level)


def validate(address):
    """ Validates an address over the USPS API.
    :param address: A dictionary containing the address to validate. Must
        contain the keys ``address_line_1``, ``address_line_2``, ``city``,
        ``state``, and ``zip_code`` all with string values. Some values may be
        empty strings and the USPS API will attempt to fill them in if
        possible.
    :type address: dictionary
    :returns: A dictionary containing the same fields as the ``address``
        parameter as validated by the USPS API.  If the USPS API returns extra
        fields, they will be returned in a ``usps_extra`` key on the return
        value containing a dictionary of the returned fields.
    :rtype: dictionary
    """
    APPLICATION.logger.debug('USPS validation request: %s', address)

    # Create the XML request.
    def add_child(parent_xml, name, value):
        """ Helper function to add an XML tag with text value. """
        lxml.etree.SubElement(parent_xml, name).text = value
    xml = lxml.etree.Element('AddressValidateRequest', USERID=USPS_USER_ID)
    address_xml = lxml.etree.SubElement(xml, 'Address', ID=str(0))
    add_child(address_xml, 'Address1', address['address_line_2'])
    add_child(address_xml, 'Address2', address['address_line_1'])
    add_child(address_xml, 'City', address['city'])
    add_child(address_xml, 'State', address['state'])
    add_child(address_xml, 'Zip5', address['zip_code'][:5])
    add_child(address_xml, 'Zip4', address['zip_code'][5:].replace('-', ''))
    params = urllib.parse.urlencode([('API', 'Verify'), ('XML', lxml.etree.tostring(xml))])
    url = '{0}?{1}'.format(USPS_API_URL, params)

    # Issue the request.
    APPLICATION.logger.debug('Issuing request: %s', url)
    try:
        response = urllib.request.urlopen(url)
    except Exception as exc:
        APPLICATION.logger.error('Request failed: %s', exc)
        raise
    APPLICATION.logger.debug('Received response.')

    # The response is expected to be valid XML.
    try:
        response = lxml.etree.parse(response).getroot()
    except Exception as exc:
        APPLICATION.logger.error('Unable to parse response as XML: %s', exc)
        raise

    # For bad requests the USPS API adds an Error tag to the response.
    if response.tag == 'Error':
        error_description = response.find('Description').text
        APPLICATION.logger.error('USPS API responded with an error: %s',
                                 error_description)
        raise RuntimeError(error_description)

    # For good requests with bad addresses, the USPS API addes an Error tag to
    # the Address tag.
    response = response.find('Address')
    error = response.find('Error')
    if error is not None:
        error_description = error.find('Description').text
        APPLICATION.logger.warning('USPS API responded with an address error: %s',
                       error_description)
        raise RuntimeError(error_description)

    # Translate the response into our address format.
    APPLICATION.logger.debug('Good response received.')
    usps_format = {c.tag: c.text for c in response.iterchildren()}
    validated = {}
    validated['address_line_1'] = usps_format.pop('Address2', '')
    validated['address_line_2'] = usps_format.pop('Address1', '')
    validated['city'] = usps_format.pop('City', '')
    validated['state'] = usps_format.pop('State', '')
    validated['zip_code'] = usps_format.pop('Zip5', '')
    zip4 = usps_format.pop('Zip4', '')
    if zip4:
        validated['zip_code'] += '-' + zip4
    validated['usps_extra'] = usps_format
    APPLICATION.logger.debug('Parsed response: %s', validated)
    return validated


@APPLICATION.route('/validate', methods=['POST'])
def validate_endpoint():
    """ Validates an address that comes in as JSON data.
    See muse_usps.validate documentation for request structure. Any extra fields are ignored.
    Returns a 400 error if the request was valid, but an error was reported by the USPS API. The 400
    response will include an "error" field with the error message returned by the USPS API. All
    other backend errors will result in a 500 error with no response. """
    try:
        APPLICATION.logger.info('Address validation request: %s', flask.request.json)
        validated = validate(flask.request.json)
        APPLICATION.logger.debug('Address validation response: %s', validated)
        return flask.jsonify(validated)
    except RuntimeError as ex:
        APPLICATION.logger.error('Address validation runtime error: %s', ex)
        return flask.jsonify({'error': str(ex).strip()}), 400
    except Exception as ex:
        APPLICATION.logger.error('Address validation unknown error: %s', ex)
        raise # This will result in a 500 error.
