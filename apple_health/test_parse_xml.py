import pytest
from parse_xml import device_string_to_json, append_device_string

def test_parse_device():
    device = "&lt;&lt;HKDevice: 0x2809514f0&gt;, name:iPhone, manufacturer:Apple Inc., model:iPhone, hardware:iPhone13,3, software:14.5.1&gt;"
    jdata = device_string_to_json(device)
    assert jdata['name'] == 'iPhone'
    assert jdata['manufacturer'] == 'Apple Inc.'
    assert jdata['model'] == 'iPhone'
    print(jdata['hardware'])
    assert jdata['hardware'] == 'iPhone13,3'
    assert jdata['software'] == '14.5.1'

def test_append_device():
    device = "&lt;&lt;HKDevice: 0x2809514f0&gt;, name:iPhone, manufacturer:Apple Inc., model:iPhone, hardware:iPhone13,3, software:14.5.1&gt;"
    jdata = {'startDate': 1, 'endDate': 2}
    jdata = append_device_string(device, jdata)
    assert jdata['startDate'] == 1
    assert jdata['endDate'] == 2
    assert jdata['name'] == 'iPhone'
    assert jdata['manufacturer'] == 'Apple Inc.'
    assert jdata['model'] == 'iPhone'
    assert jdata['hardware'] == 'iPhone13,3'
    assert jdata['software'] == '14.5.1'

    device = "&lt;&lt;HKDevice: 0x280ac48c0&gt;, name:Apple Watch, manufacturer:Apple Inc., model:Watch, hardware:Watch5,4, software:9.3&gt;"
    jdata = device_string_to_json(device)
    assert jdata['name'] == 'Apple Watch'
    assert jdata['manufacturer'] == 'Apple Inc.'
    assert jdata['model'] == 'Watch'
    assert jdata['hardware'] == 'Watch5,4'
    assert jdata['software'] == '9.3'

    device = "&lt;&lt;HKDevice: 0x280a57d90&gt;, name:iPhone, manufacturer:Apple Inc., model:iPhone, hardware:iPhone12,8, software:16.5&gt;"
    jdata = device_string_to_json(device)
    assert jdata['name'] == 'iPhone'
    assert jdata['manufacturer'] == 'Apple Inc.'
    assert jdata['model'] == 'iPhone'
    assert jdata['hardware'] == 'iPhone12,8'
    assert jdata['software'] == '16.5'    