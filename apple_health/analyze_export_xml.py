import xml.etree.ElementTree as ET
import argparse
import os
import time

''' This script is used to analyze new versions of export.xml to see if new type keys have been added that
    we want to support.

    The current strategy is to export the data from each key into a separate file so that users can load
    only the data they are interested in.
'''


def process_file(xml_file_path):
    # we want to only print out the types that are not handled by the parsing scripts or that we don't care about
    handled_or_ignored_types = [
        'HKQuantityTypeIdentifierHeight',  # just ignoring this as it is not collected by the watch
        'HKQuantityTypeIdentifierBodyMass',  # just ignoring this as it is not collected by the watch
        'HKQuantityTypeIdentifierHeartRate',
        'HKQuantityTypeIdentifierRestingHeartRate',
        'HKQuantityTypeIdentifierEnvironmentalAudioExposure',
        'HKQuantityTypeIdentifierHeadphoneAudioExposure',
        'HKQuantityTypeIdentifierBloodPressureSystolic',
        'HKQuantityTypeIdentifierBloodPressureDiastolic',
        'HKQuantityTypeIdentifierStepCount',
        'HKQuantityTypeIdentifierDistanceWalkingRunning',
        'HKQuantityTypeIdentifierDistanceCycling',
        'HKQuantityTypeIdentifierVO2Max',
        'HKQuantityTypeIdentifierFlightsClimbed',
        'HKQuantityTypeIdentifierAppleStandTime',
        'HKCategoryTypeIdentifierAppleStandHour',  # ignored because it is redundant to stand time
        'HKQuantityTypeIdentifierHeartRateVariabilitySDNN',
        'HKQuantityTypeIdentifierWalkingHeartRateAverage',
        'HKQuantityTypeIdentifierBasalEnergyBurned',
        'HKQuantityTypeIdentifierActiveEnergyBurned',
        'HKQuantityTypeIdentifierAppleExerciseTime',
        'HKQuantityTypeIdentifierRespiratoryRate',
        'HKQuantityTypeIdentifierWalkingStepLength',
        'HKQuantityTypeIdentifierWalkingDoubleSupportPercentage',
        'HKCategoryTypeIdentifierSleepAnalysis',  # there seems to be no data in this tag
        'HKDataTypeSleepDurationGoal',  # this seems to be a log of user input rather than a measurement
    ]

    # Create a dictionary to store the type values and their counts
    type_counts = {}

    # Open the XML file and create an ElementTree object
    with open(xml_file_path, 'r') as xml_file:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Loop through each 'Record' element in the XML file
        for record_elem in root.findall(".//Record"):
            # Extract the value of the 'type' field
            type_value = record_elem.get('type')

            # If the type value is not in the dictionary, add it with a count of 1
            # Otherwise, increment the count for the type value by 1
            if type_value not in type_counts:
                type_counts[type_value] = 1
            else:
                type_counts[type_value] += 1

    # remove ignored keys
    for k in handled_or_ignored_types:
        if k in type_counts:
            del type_counts[k]

    # Print the summary of type values and their counts
    print("Summary of Type Values and Counts:")
    for type_value, count in type_counts.items():
        print("Type Value: {}, Count: {}".format(type_value, count))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='transform export.xml into data files')
    parser.add_argument("filename", type=str, help='pathname to the export.xml file')
    args = parser.parse_args()

    filename = args.filename
    if os.path.exists(filename):
        
        start_time = time.time()  # Start the timer
        process_file(filename)
        end_time = time.time()  # End the timer
        runtime = end_time - start_time  # Calculate the runtime
        print("Runtime: {:.2f} seconds".format(runtime))
    else:
        print(f'The file "{filename}" does not exist')
    
    
