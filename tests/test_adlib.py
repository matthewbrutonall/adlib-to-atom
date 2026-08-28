import pytest
import os
import xml.etree.ElementTree as ET
from adlib_core import parse_adlib_record, load_mapping

@pytest.fixture
def default_mapping():
    mapping_path = os.path.join(os.path.dirname(__file__), '..', 'default_mapping.json')
    return load_mapping(mapping_path)

def test_parallel_arrays_padding(default_mapping):
    xml = '''<record>
        <creator>John</creator>
        <production.date.start>1990</production.date.start>
        <production.date.start>2000</production.date.start>
    </record>'''
    elem = ET.fromstring(xml)
    row = parse_adlib_record(elem, default_mapping, "repo", "en")
    
    assert row["eventActors"] == "John|NULL"
    assert row["eventTypes"] == "Creation|Creation"
    assert row["eventStartDates"] == "1990|2000"
    assert row["eventEndDates"] == "NULL|NULL"
    
def test_parallel_arrays_no_actors_yes_dates(default_mapping):
    xml = '''<record>
        <production.date.start>1990</production.date.start>
    </record>'''
    elem = ET.fromstring(xml)
    row = parse_adlib_record(elem, default_mapping, "repo", "en")
    
    assert row["eventActors"] == "NULL"
    assert row["eventTypes"] == "Creation"
    assert row["eventStartDates"] == "1990"
    assert row["eventEndDates"] == "NULL"

def test_multilingual_value_culture_selection(default_mapping):
    xml = '''<record>
        <title>
            <value lang="nl">Paard</value>
            <value lang="en">Horse</value>
        </title>
    </record>'''
    elem = ET.fromstring(xml)
    row = parse_adlib_record(elem, default_mapping, "repo", "en")
    assert row["title"] == "Horse"
    
def test_multilingual_value_fallback(default_mapping):
    xml = '''<record>
        <title>
            <value lang="fr">Cheval</value>
            <value lang="nl">Paard</value>
        </title>
    </record>'''
    elem = ET.fromstring(xml)
    row = parse_adlib_record(elem, default_mapping, "repo", "en")
    # Should fallback to the first translation if 'en' is missing
    assert row["title"] == "Cheval"

def test_dedupe_priref(default_mapping):
    xml = '''<record priref="10"><priref>10</priref></record>'''
    elem = ET.fromstring(xml)
    row = parse_adlib_record(elem, default_mapping, "repo", "en")
    assert row["legacyId"] == "10"
    assert row["identifier"] == "10"

def test_no_dedupe_other_fields(default_mapping):
    xml = '''<record>
        <creator>Smith</creator>
        <creator>Smith</creator>
    </record>'''
    elem = ET.fromstring(xml)
    row = parse_adlib_record(elem, default_mapping, "repo", "en")
    # Should keep both creators even if identical
    assert row["eventActors"] == "Smith|Smith"
