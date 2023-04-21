import xml.etree.ElementTree as ET
import json
import re
import pdb

''' This parses the XML data produced by the Apple Health App on the iPhone and converts it to JSON format.

    This script does not attempt to preserve all the information in the XML file but rather only keeps the
    data that would be useful in performing data analyses on the data.  In order to allow the user to work 
    with only the data relevant to them, as well as to keep the data in as simple a format as possible, each
    type of data is written to a separate JSON file.

    Since is likely that a user will use this as a starting point to customize the format of data they wish
    to produce I have kept the handling of each record type as a separate function.  This creates code 
    duplication but allows someone to change one data type without concerning themselves of the impact on 
    the others.

    TODO:
      * it might be nice to create a duration field (end_date - start_date)
      * the conversion summary should include a date range that the records cover
'''

# Define the XML file path and JSON file path
xml_file_path = 'export_small.xml'

HKMetadataKeyHeartRateMotionContext = {'0': 'notSet', '1': 'sedentary', '2': 'active', '3': 'ECG'}


def replace_unicode_chars(text):
    # Replace \u00a0 with space
    text = text.replace('\u00a0', ' ')
    text = text.replace('\xa0', ' ')
    
    # Replace \u2019 with apostrophe
    text = text.replace('\u2019', "'")
    
    return text


def device_string_to_json(string):
    regex = r'([\w]+):([\w\s\d.]+)'

    if (not string) or string == '':
        pdb.set_trace()
        return None

    # Find all key-value pairs using regex
    matches = re.findall(regex, string)

    # Create a dictionary with the key-value pairs
    data = {}
    for match in matches:
        key = match[0].strip()
        value = match[1].strip()
        data[key] = value

    # Convert the dictionary to JSON
    json_data = json.dumps(data)
    return data


def convert_date_format(s):
    ''' make it easy to convert dates to other formats easily in the future
    '''
    return s


def write_data_to_file(file_path, records):
        # Write the extracted data to a JSON file
    with open(file_path, 'w') as json_file:
        json.dump(records, json_file, indent=4)
    print(f"Extraction completed. {len(records)} records written to: " + file_path)


def collect_hr_records(root):
    json_file_path = './heart_rate_data.json'
    records = []    # Loop through each 'Record' element in the XML file
    for record_elem in root.findall(".//Record[@type='HKQuantityTypeIdentifierHeartRate']"):
        # Extract the field values using ElementTree's 'get' method
        source_name = replace_unicode_chars(record_elem.get('sourceName'))
        device = record_elem.get('device')
        unit = record_elem.get('unit')
        creation_date = convert_date_format(record_elem.get('creationDate'))
        start_date = convert_date_format(record_elem.get('startDate'))
        end_date = convert_date_format(record_elem.get('endDate'))
        value = record_elem.get('value')

        # Extract the MetadataEntry value with key HKMetadataKeyHeartRateMotionContext
        metadata_entry_elem = record_elem.find(".//MetadataEntry[@key='HKMetadataKeyHeartRateMotionContext']")
        if metadata_entry_elem is not None:
            metadata_value = metadata_entry_elem.get('value')
        else:
            metadata_value = None

        # if the heart rate comes from an ECG it will be an average which is represented as floating point
        # I want this handled as a different context with the value converted to an integer.
        if '.' in value:
            value = int(round(float(value), 0))
            metadata_value = '3'  # value used for ECG in dict
        else:
            value = int(value)

        # Create a dictionary to store the extracted data for this record
        record_data = {
            'sourceName': source_name,
            'device': device,
            'creationDate': creation_date,
            'startDate': start_date,
            'endDate': end_date,
            'bpm': value,
            # it seems like this can be missing in some cases
            'context': HKMetadataKeyHeartRateMotionContext.get(metadata_value, 'notSet')
        }

        # Append the record data to the list
        records.append(record_data)

    write_data_to_file(json_file_path, records)


def collect_resting_hr_records(root):
    json_file_path = './resting_heart_rate_data.json'
    records = []    # Loop through each 'Record' element in the XML file
    for record_elem in root.findall(".//Record[@type='HKQuantityTypeIdentifierRestingHeartRate']"):
        # Extract the field values using ElementTree's 'get' method
        source_name = replace_unicode_chars(record_elem.get('sourceName'))
        creation_date = convert_date_format(record_elem.get('creationDate'))
        start_date = convert_date_format(record_elem.get('startDate'))
        end_date = convert_date_format(record_elem.get('endDate'))
        value = record_elem.get('value')

        # Create a dictionary to store the extracted data for this record
        record_data = {
            'sourceName': source_name,
            'creationDate': creation_date,
            'startDate': start_date,
            'endDate': end_date,
            'bpm': int(value),
        }

        # Append the record data to the list
        records.append(record_data)

    write_data_to_file(json_file_path, records)


def collect_blood_pressure_records(root):
    json_file_path = './blood_pressure_data.json'
    records = {}    # dict by creation_date so we can match up both pressure types
    for record_elem in root.findall(".//Record[@type='HKQuantityTypeIdentifierBloodPressureSystolic']") + \
                       root.findall(".//Record[@type='HKQuantityTypeIdentifierBloodPressureDiastolic']"):
        # Extract the field values using ElementTree's 'get' method
        rec_type = record_elem.get('type')
        source_name = record_elem.get('sourceName')
        creation_date = convert_date_format(record_elem.get('creationDate'))
        start_date = convert_date_format(record_elem.get('startDate'))
        end_date = convert_date_format(record_elem.get('endDate'))
        value = record_elem.get('value')

        # we need to collect up the systolic and diastolic pressures into one record by matching up creationDate
        if rec_type == 'HKQuantityTypeIdentifierBloodPressureSystolic':
            k = 'systolic'
        else:
            k = 'diastolic'
        if creation_date in records:
            records[creation_date][k] = int(value)
        else:
            records[creation_date] = {
                'sourceName': source_name,
                'creationDate': creation_date,
                'startDate': start_date,
                'endDate': end_date,               
            }
            records[creation_date][k] = int(value)


    # now convert the dict to a list
    records = list(records.values())

    write_data_to_file(json_file_path, records)


def collect_step_records(root):
    json_file_path = './step_data.json'
    records = []    # Loop through each 'Record' element in the XML file
    for record_elem in root.findall(".//Record[@type='HKQuantityTypeIdentifierStepCount']"):
        # Extract the field values using ElementTree's 'get' method
        source_name = replace_unicode_chars(record_elem.get('sourceName'))
        device = record_elem.get('device')
        creation_date = convert_date_format(record_elem.get('creationDate'))
        start_date = convert_date_format(record_elem.get('startDate'))
        end_date = convert_date_format(record_elem.get('endDate'))
        value = record_elem.get('value')

        # Create a dictionary to store the extracted data for this record
        record_data = {
            'sourceName': source_name,
            'creationDate': creation_date,
            'startDate': start_date,
            'endDate': end_date,
            'steps': int(value),
        }

        # because I've found the phone to be a poor source of step data I want to make it easy to filter out that
        # data during analysis
        if not device:
            device = ''

        if 'model:Watch' in device:
            record_data['device_type'] = 'watch'
        else:
            record_data['device_type'] = 'phone'

        # add the device data 
        if device:
            for k, v in device_string_to_json(device).items():
                record_data[k] = v
        # Append the record data to the list
        records.append(record_data)

    # Write the extracted data to a JSON file
    with open(json_file_path, 'w') as json_file:
        json.dump(records, json_file, indent=4)
    print(f"Extraction completed. {len(records)} records written to: " + json_file_path)


def collect_distance_records(root):
    ''' my first thoughts was to just add distance to the step records rather than as a separate file
        but it appears that there are a different number of records of steps and distance.  not sure 
        why but have to keep them separated for analysis.
    '''
    json_file_path = './distance_data.json'
    records = []    # Loop through each 'Record' element in the XML file
    for record_elem in root.findall(".//Record[@type='HKQuantityTypeIdentifierDistanceWalkingRunning']"):
        # Extract the field values using ElementTree's 'get' method
        source_name = replace_unicode_chars(record_elem.get('sourceName'))
        device = record_elem.get('device')
        creation_date = convert_date_format(record_elem.get('creationDate'))
        start_date = convert_date_format(record_elem.get('startDate'))
        end_date = convert_date_format(record_elem.get('endDate'))
        value = record_elem.get('value')

        # Create a dictionary to store the extracted data for this record
        record_data = {
            'sourceName': source_name,
            'creationDate': creation_date,
            'startDate': start_date,
            'endDate': end_date,
            'miles': float(value),
        }

        # because I've found the phone to be a poor source of step data I want to make it easy to filter out that
        # data during analysis
        if not device:
            device = ''

        if 'model:Watch' in device:
            record_data['device_type'] = 'watch'
        else:
            record_data['device_type'] = 'phone'

        # add the device data 
        if device:
            for k, v in device_string_to_json(device).items():
                record_data[k] = v
        # Append the record data to the list
        records.append(record_data)

    # Write the extracted data to a JSON file
    with open(json_file_path, 'w') as json_file:
        json.dump(records, json_file, indent=4)
    print(f"Extraction completed. {len(records)} records written to: " + json_file_path)


def collect_vo2max_records(root):
    json_file_path = './vo2max_data.json'
    HKVO2MaxTestType = {'1': 'maxExercise', '2': 'predictionSubMaxExercise', '3':'predictionNonExercise'}
    
    records = []    # Loop through each 'Record' element in the XML file
    for record_elem in root.findall(".//Record[@type='HKQuantityTypeIdentifierVO2Max']"):
        # Extract the field values using ElementTree's 'get' method
        source_name = replace_unicode_chars(record_elem.get('sourceName'))
        unit = record_elem.get('unit')
        creation_date = convert_date_format(record_elem.get('creationDate'))
        start_date = convert_date_format(record_elem.get('startDate'))
        end_date = convert_date_format(record_elem.get('endDate'))
        value = record_elem.get('value')

        # Extract the MetadataEntry value with key HKMetadataKeyHeartRateMotionContext
        metadata_entry_elem = record_elem.find(".//MetadataEntry[@key='HKVO2MaxTestType']")
        if metadata_entry_elem is not None:
            metadata_value = metadata_entry_elem.get('value')
        else:
            metadata_value = None



        # Create a dictionary to store the extracted data for this record
        record_data = {
            'sourceName': source_name,
            'creationDate': creation_date,
            'startDate': start_date,
            'endDate': end_date,
            'vo2max': value,
            'context': HKVO2MaxTestType.get(metadata_value, 'notSet')
        }

        # Append the record data to the list
        records.append(record_data)

    write_data_to_file(json_file_path, records)


def collect_flights_records(root):
    json_file_path = './flights_climbed_data.json'
    records = []    # Loop through each 'Record' element in the XML file
    for record_elem in root.findall(".//Record[@type='HKQuantityTypeIdentifierFlightsClimbed']"):
        # Extract the field values using ElementTree's 'get' method
        source_name = replace_unicode_chars(record_elem.get('sourceName'))
        device = record_elem.get('device')
        creation_date = convert_date_format(record_elem.get('creationDate'))
        start_date = convert_date_format(record_elem.get('startDate'))
        end_date = convert_date_format(record_elem.get('endDate'))
        value = record_elem.get('value')

        # Create a dictionary to store the extracted data for this record
        record_data = {
            'sourceName': source_name,
            'creationDate': creation_date,
            'startDate': start_date,
            'endDate': end_date,
            'flights': int(value),
        }

        # because I've found the phone to be a poor source of step data I want to make it easy to filter out that
        # data during analysis
        if not device:
            device = ''

        if 'model:Watch' in device:
            record_data['device_type'] = 'watch'
        else:
            record_data['device_type'] = 'phone'

        # add the device data 
        if device:
            for k, v in device_string_to_json(device).items():
                record_data[k] = v
        # Append the record data to the list
        records.append(record_data)

    # Write the extracted data to a JSON file
    with open(json_file_path, 'w') as json_file:
        json.dump(records, json_file, indent=4)
    print(f"Extraction completed. {len(records)} records written to: " + json_file_path)


def collect_cycling_records(root):
    ''' older apple watch records do not have a device string so I've chosen not to capture
        that data as having it only for some records does not make sense.  If you only have
        new records you can uncomment that section below
    '''
    json_file_path = './cycling_data.json'
    records = []    # Loop through each 'Record' element in the XML file
    for record_elem in root.findall(".//Record[@type='HKQuantityTypeIdentifierDistanceCycling']"):
        # Extract the field values using ElementTree's 'get' method
        source_name = replace_unicode_chars(record_elem.get('sourceName'))
        # device = record_elem.get('device')
        creation_date = convert_date_format(record_elem.get('creationDate'))
        start_date = convert_date_format(record_elem.get('startDate'))
        end_date = convert_date_format(record_elem.get('endDate'))
        value = record_elem.get('value')

        # Create a dictionary to store the extracted data for this record
        record_data = {
            'sourceName': source_name,
            'creationDate': creation_date,
            'startDate': start_date,
            'endDate': end_date,
            'miles': float(value),
        }

        # add the device data
        #for k, v in device_string_to_json(device).items():
        #    record_data[k] = v
        # Append the record data to the list
        #records.append(record_data)

    # Write the extracted data to a JSON file
    with open(json_file_path, 'w') as json_file:
        json.dump(records, json_file, indent=4)
    print(f"Extraction completed. {len(records)} records written to: " + json_file_path)


def collect_audio_exposure_records(root):
    ''' my first thoughts was to just add distance to the step records rather than as a separate file
        but it appears that there are a different number of records of steps and distance.  not sure 
        why but have to keep them separated for analysis.
    '''
    json_file_path = './audio_exposure_data.json'
    records = []    # Loop through each 'Record' element in the XML file
    for record_elem in root.findall(".//Record[@type='HKQuantityTypeIdentifierEnvironmentalAudioExposure']"):
        # Extract the field values using ElementTree's 'get' method
        source_name = replace_unicode_chars(record_elem.get('sourceName'))
        device = record_elem.get('device')
        creation_date = convert_date_format(record_elem.get('creationDate'))
        start_date = convert_date_format(record_elem.get('startDate'))
        end_date = convert_date_format(record_elem.get('endDate'))
        value = record_elem.get('value')

        # Create a dictionary to store the extracted data for this record
        record_data = {
            'sourceName': source_name,
            'creationDate': creation_date,
            'startDate': start_date,
            'endDate': end_date,
            'dbASPL': float(value),
        }

        # add the device data 
        if device:
            for k, v in device_string_to_json(device).items():
                record_data[k] = v
        # Append the record data to the list
        records.append(record_data)

    # Write the extracted data to a JSON file
    with open(json_file_path, 'w') as json_file:
        json.dump(records, json_file, indent=4)
    print(f"Extraction completed. {len(records)} records written to: " + json_file_path)


def collect_stand_records(root):
    json_file_path = './stand_data.json'
    records = []    # Loop through each 'Record' element in the XML file
    for record_elem in root.findall(".//Record[@type='HKQuantityTypeIdentifierAppleStandTime']"):
        # Extract the field values using ElementTree's 'get' method
        source_name = replace_unicode_chars(record_elem.get('sourceName'))
        unit = record_elem.get('unit')
        creation_date = convert_date_format(record_elem.get('creationDate'))
        start_date = convert_date_format(record_elem.get('startDate'))
        end_date = convert_date_format(record_elem.get('endDate'))
        value = int(record_elem.get('value'))

        # Create a dictionary to store the extracted data for this record
        record_data = {
            'sourceName': source_name,
            'creationDate': creation_date,
            'startDate': start_date,
            'endDate': end_date,
            'stand_min': value,
        }

        # Append the record data to the list
        records.append(record_data)

    write_data_to_file(json_file_path, records)


def collect_hr_variability_records(root):
    ''' The XML file includes the measurements that the variability was computed over but
        I'm not including that data since I assume the variability was computed correctly
        but knowing the range of beats is useful
    '''
    json_file_path = './heart_rate_variability_data.json'
    records = []    # Loop through each 'Record' element in the XML file
    for record_elem in root.findall(".//Record[@type='HKQuantityTypeIdentifierHeartRateVariabilitySDNN']"):
        # Extract the field values using ElementTree's 'get' method
        source_name = replace_unicode_chars(record_elem.get('sourceName'))
        device = record_elem.get('device')
        unit = record_elem.get('unit')
        creation_date = convert_date_format(record_elem.get('creationDate'))
        start_date = convert_date_format(record_elem.get('startDate'))
        end_date = convert_date_format(record_elem.get('endDate'))
        value = record_elem.get('value')



        # Extract the MetadataEntry value with key HKMetadataKeyHeartRateMotionContext
        beats = []
        for metadata_entry_elem in record_elem.findall(".//InstantaneousBeatsPerMinute"):
            if metadata_entry_elem is not None:
                beats.append(int(metadata_entry_elem.get('bpm')))

        # Create a dictionary to store the extracted data for this record
        record_data = {
            'sourceName': source_name,
            'creationDate': creation_date,
            'startDate': start_date,
            'endDate': end_date,
            'variation_ms': float(value),
            'bpm_min': min(beats),
            'bpm_max': max(beats)
        }

        # add the device data 
        if device:
            for k, v in device_string_to_json(device).items():
                record_data[k] = v
        # Append the record data to the list
        records.append(record_data)

    write_data_to_file(json_file_path, records)


def collect_walking_hr_records(root):
    json_file_path = './hr_walking_avg_data.json'
    records = []    # Loop through each 'Record' element in the XML file
    for record_elem in root.findall(".//Record[@type='HKQuantityTypeIdentifierWalkingHeartRateAverage']"):
        # Extract the field values using ElementTree's 'get' method
        source_name = replace_unicode_chars(record_elem.get('sourceName'))
        unit = record_elem.get('unit')
        creation_date = convert_date_format(record_elem.get('creationDate'))
        start_date = convert_date_format(record_elem.get('startDate'))
        end_date = convert_date_format(record_elem.get('endDate'))
        value = record_elem.get('value')

        # Create a dictionary to store the extracted data for this record
        record_data = {
            'sourceName': source_name,
            'creationDate': creation_date,
            'startDate': start_date,
            'endDate': end_date,
            'walking_hr_avg': float(value),
        }

        # Append the record data to the list
        records.append(record_data)

    write_data_to_file(json_file_path, records)


def collect_energy_resting_records(root):
    json_file_path = './energy_resting_data.json'
    records = []    # Loop through each 'Record' element in the XML file
    for record_elem in root.findall(".//Record[@type='HKQuantityTypeIdentifierBasalEnergyBurned']"):
        # Extract the field values using ElementTree's 'get' method
        source_name = replace_unicode_chars(record_elem.get('sourceName'))
        device = record_elem.get('device')
        creation_date = convert_date_format(record_elem.get('creationDate'))
        start_date = convert_date_format(record_elem.get('startDate'))
        end_date = convert_date_format(record_elem.get('endDate'))
        value = record_elem.get('value')

        # Create a dictionary to store the extracted data for this record
        record_data = {
            'sourceName': source_name,
            'creationDate': creation_date,
            'startDate': start_date,
            'endDate': end_date,
            'kcal': float(value),
        }

        # add the device data 
        if device:
            for k, v in device_string_to_json(device).items():
                record_data[k] = v
        # Append the record data to the list
        records.append(record_data)

    # Write the extracted data to a JSON file
    with open(json_file_path, 'w') as json_file:
        json.dump(records, json_file, indent=4)
    print(f"Extraction completed. {len(records)} records written to: " + json_file_path)


def collect_energy_active_records(root):
    json_file_path = './energy_active_data.json'
    records = []    # Loop through each 'Record' element in the XML file
    for record_elem in root.findall(".//Record[@type='HKQuantityTypeIdentifierActiveEnergyBurned']"):
        # Extract the field values using ElementTree's 'get' method
        source_name = replace_unicode_chars(record_elem.get('sourceName'))
        device = record_elem.get('device')
        creation_date = convert_date_format(record_elem.get('creationDate'))
        start_date = convert_date_format(record_elem.get('startDate'))
        end_date = convert_date_format(record_elem.get('endDate'))
        value = record_elem.get('value')

        # Create a dictionary to store the extracted data for this record
        record_data = {
            'sourceName': source_name,
            'creationDate': creation_date,
            'startDate': start_date,
            'endDate': end_date,
            'kcal': float(value),
        }

        # add the device data
        if device:
            for k, v in device_string_to_json(device).items():
                record_data[k] = v
        # Append the record data to the list
        records.append(record_data)

    # Write the extracted data to a JSON file
    with open(json_file_path, 'w') as json_file:
        json.dump(records, json_file, indent=4)
    print(f"Extraction completed. {len(records)} records written to: " + json_file_path)


def collect_exercise_time_records(root):
    json_file_path = './exercise_time_data.json'
    records = []    # Loop through each 'Record' element in the XML file
    for record_elem in root.findall(".//Record[@type='HKQuantityTypeIdentifierAppleExerciseTime']"):
        # Extract the field values using ElementTree's 'get' method
        source_name = replace_unicode_chars(record_elem.get('sourceName'))
        device = record_elem.get('device')
        creation_date = convert_date_format(record_elem.get('creationDate'))
        start_date = convert_date_format(record_elem.get('startDate'))
        end_date = convert_date_format(record_elem.get('endDate'))
        value = record_elem.get('value')

        # Create a dictionary to store the extracted data for this record
        record_data = {
            'sourceName': source_name,
            'creationDate': creation_date,
            'startDate': start_date,
            'endDate': end_date,
            'exercise_min': int(value),
        }

        # add the device data 
        if device:
            for k, v in device_string_to_json(device).items():
                record_data[k] = v
        # Append the record data to the list
        records.append(record_data)

    # Write the extracted data to a JSON file
    with open(json_file_path, 'w') as json_file:
        json.dump(records, json_file, indent=4)
    print(f"Extraction completed. {len(records)} records written to: " + json_file_path)


# Open the XML file and create an ElementTree object
with open(xml_file_path, 'r') as xml_file:
    tree = ET.parse(xml_file)
    root = tree.getroot()

    collect_hr_records(root)
    collect_resting_hr_records(root)
    collect_blood_pressure_records(root)
    collect_step_records(root)
    collect_distance_records(root)
    collect_vo2max_records(root)
    collect_flights_records(root)
    collect_cycling_records(root)
    collect_audio_exposure_records(root)
    collect_stand_records(root)
    collect_hr_variability_records(root)
    collect_walking_hr_records(root)
    collect_energy_resting_records(root)
    collect_energy_active_records(root)
