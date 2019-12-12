import pytest

from bas_web_map_inventory.utils import validate_ogc_capabilities, OGCProtocol


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
                "line:131: element westBoundLongitude: Schemas validity error : Element '{http://www.opengis.net/wms}westBoundLongitude': '-190' is not a valid value of the atomic type '{http://www.opengis.net/wms}longitudeType'.",
                "line:134: element southBoundLatitude: Schemas validity error : Element '{http://www.opengis.net/wms}southBoundLatitude': [facet 'minInclusive'] The value '-190' is less than the minimum value allowed ('-90').",
                "line:134: element southBoundLatitude: Schemas validity error : Element '{http://www.opengis.net/wms}southBoundLatitude': '-190' is not a valid value of the atomic type '{http://www.opengis.net/wms}latitudeType'."
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
                "line:110: element westBoundLongitude: Schemas validity error : Element '{http://www.opengis.net/wms}westBoundLongitude': '-190' is not a valid value of the atomic type '{http://www.opengis.net/wms}longitudeType'.",
                "line:112: element eastBoundLongitude: Schemas validity error : Element '{http://www.opengis.net/wms}eastBoundLongitude': [facet 'minInclusive'] The value '-190' is less than the minimum value allowed ('-180').",
                "line:112: element eastBoundLongitude: Schemas validity error : Element '{http://www.opengis.net/wms}eastBoundLongitude': '-190' is not a valid value of the atomic type '{http://www.opengis.net/wms}longitudeType'.",
                "line:131: element westBoundLongitude: Schemas validity error : Element '{http://www.opengis.net/wms}westBoundLongitude': [facet 'minInclusive'] The value '-190' is less than the minimum value allowed ('-180').",
                "line:131: element westBoundLongitude: Schemas validity error : Element '{http://www.opengis.net/wms}westBoundLongitude': '-190' is not a valid value of the atomic type '{http://www.opengis.net/wms}longitudeType'.",
                "line:134: element southBoundLatitude: Schemas validity error : Element '{http://www.opengis.net/wms}southBoundLatitude': [facet 'minInclusive'] The value '-190' is less than the minimum value allowed ('-90').",
                "line:134: element southBoundLatitude: Schemas validity error : Element '{http://www.opengis.net/wms}southBoundLatitude': '-190' is not a valid value of the atomic type '{http://www.opengis.net/wms}latitudeType'."
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
