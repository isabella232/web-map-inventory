import pytest

# noinspection PyProtectedMember
from bas_web_map_inventory.utils import OGCProtocol, validate_ogc_capabilities, _process_xmllint_errors, \
    build_base_data_source_endpoint


@pytest.mark.parametrize(
    argnames=['protocol', 'capabilities_document', 'mode', 'results'],
    argvalues=[
        (
            OGCProtocol.WMS,
            'tests/resources/validate_ogc_capabilities/wms-1.3.0-valid.xml',
            False,
            []
        ),
        (
            OGCProtocol.WMS,
            'tests/resources/validate_ogc_capabilities/wms-1.3.0-valid.xml',
            True,
            []
        ),
        (
            OGCProtocol.WMS,
            'tests/resources/validate_ogc_capabilities/wms-1.3.0-invalid-single-missing-style-title.xml',
            False,
            ["Element '{http://www.opengis.net/wms}LegendURL': This element is not expected. Expected is ( {http://www.opengis.net/wms}Title )., line 140"]
        ),
        (
            OGCProtocol.WMS,
            'tests/resources/validate_ogc_capabilities/wms-1.3.0-invalid-single-missing-style-title.xml',
            True,
            ["line:140: element LegendURL: Schemas validity error : Element '{http://www.opengis.net/wms}LegendURL': This element is not expected. Expected is ( {http://www.opengis.net/wms}Title )."]
        ),
        (
            OGCProtocol.WMS,
            'tests/resources/validate_ogc_capabilities/wms-1.3.0-invalid-multiple-missing-style-title.xml',
            False,
            ["Element '{http://www.opengis.net/wms}LegendURL': This element is not expected. Expected is ( {http://www.opengis.net/wms}Title )., line 140"]
        ),
        (
            OGCProtocol.WMS,
            'tests/resources/validate_ogc_capabilities/wms-1.3.0-invalid-multiple-missing-style-title.xml',
            True,
            [
                "line:140: element LegendURL: Schemas validity error : Element '{http://www.opengis.net/wms}LegendURL': This element is not expected. Expected is ( {http://www.opengis.net/wms}Title ).",
                "line:169: element LegendURL: Schemas validity error : Element '{http://www.opengis.net/wms}LegendURL': This element is not expected. Expected is ( {http://www.opengis.net/wms}Title )."
            ]
        ),
        (
            OGCProtocol.WMS,
            'tests/resources/validate_ogc_capabilities/wms-1.3.0-invalid-single-invalid-extent.xml',
            False,
            ["Element '{http://www.opengis.net/wms}westBoundLongitude': [facet 'minInclusive'] The value '-190' is less than the minimum value allowed ('-180')., line 131"]
        ),
        (
            OGCProtocol.WMS,
            'tests/resources/validate_ogc_capabilities/wms-1.3.0-invalid-single-invalid-extent.xml',
            True,
            [
                "line:131: element westBoundLongitude: Schemas validity error : Element '{http://www.opengis.net/wms}westBoundLongitude': [facet 'minInclusive'] The value '-190' is less than the minimum value allowed ('-180').",
                "line:134: element southBoundLatitude: Schemas validity error : Element '{http://www.opengis.net/wms}southBoundLatitude': [facet 'minInclusive'] The value '-190' is less than the minimum value allowed ('-90')."
            ]
        ),
        (
            OGCProtocol.WMS,
            'tests/resources/validate_ogc_capabilities/wms-1.3.0-invalid-multiple-invalid-extent.xml',
            False,
            ["Element '{http://www.opengis.net/wms}westBoundLongitude': [facet 'minInclusive'] The value '-190' is less than the minimum value allowed ('-180')., line 110"]
        ),
        (
            OGCProtocol.WMS,
            'tests/resources/validate_ogc_capabilities/wms-1.3.0-invalid-multiple-invalid-extent.xml',
            True,
            [
                "line:110: element westBoundLongitude: Schemas validity error : Element '{http://www.opengis.net/wms}westBoundLongitude': [facet 'minInclusive'] The value '-190' is less than the minimum value allowed ('-180').",
                "line:112: element eastBoundLongitude: Schemas validity error : Element '{http://www.opengis.net/wms}eastBoundLongitude': [facet 'minInclusive'] The value '-190' is less than the minimum value allowed ('-180').",
                "line:131: element westBoundLongitude: Schemas validity error : Element '{http://www.opengis.net/wms}westBoundLongitude': [facet 'minInclusive'] The value '-190' is less than the minimum value allowed ('-180').",
                "line:134: element southBoundLatitude: Schemas validity error : Element '{http://www.opengis.net/wms}southBoundLatitude': [facet 'minInclusive'] The value '-190' is less than the minimum value allowed ('-90')."
            ]
        ),
    ]
)
def test_validate_ogc_capabilities(protocol, capabilities_document, mode, results):
    result = validate_ogc_capabilities(
        ogc_protocol=protocol,
        capabilities_url=capabilities_document,
        multiple_errors=mode
    )
    assert len(result) == len(results)
    assert result == results


def test_validate_ogc_capabilities_invalid_protocol():
    with pytest.raises(ValueError) as e:
        # noinspection PyTypeChecker
        validate_ogc_capabilities(ogc_protocol='invalid', capabilities_url=None)

        assert e.value == 'Invalid or unsupported OGC protocol'


def test_validate_ogc_capabilities__process_xmllint_errors_no_trailing_slash():
    with pytest.raises(RuntimeError) as e:
        _process_xmllint_errors(error="testing", file_name='testing')
    assert 'xmllint error - error output is not recognised (no trailing new line)' in str(e.value)


def test_validate_ogc_capabilities__process_xmllint_errors_no_final_validation_status():
    with pytest.raises(RuntimeError) as e:
        _process_xmllint_errors(error="testing\n", file_name='testing')
    assert 'xmllint error - error output is not recognised (no final validation status)' in str(e.value)


def test_build_base_data_source_endpoint_https():
    endpoint = build_base_data_source_endpoint(data_source={'hostname': 'example.com', 'port': '443'})
    assert endpoint == 'https://example.com:443'
