import re
import io
from google.cloud import vision
from google.cloud.vision import types


# Using Google Cloud Vision API
#
# Usage:
#
# $ export GOOGLE_APPLICATION_CREDENTIALS="<path_to_your_json"
# $ python3.6 image_to_json.py
def image_to_text(path):
    print(path)
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content = content)

    # Document detection was taking minor details precisely and grouping/block
    # were not formed due to which it was hard to recognize which value
    # is what, so text_detection is better relatively
    response = client.text_detection(image=image)
    document = response.full_text_annotation

    return document.text


def report1(path):

    data = image_to_text(path).split('\n')

    # All the regex required to extract meaningful data
    date = re.compile(r'(\d+/\d+/\d+)')
    time = re.compile(r'(\d+(:|\s)\d+(:|\s)\d+)PM')
    lab_number = re.compile(r'(\d{5,})')
    name = re.compile(r'(^(Mrs. | Mr. ))\w+\s\w+')
    age = re.compile(r'.*\d+\sYears')
    gender = re.compile(r'.*(Male|Female)')
    value = re.compile(r'^(\d+)\.\d+')
    test = re.compile('^[A-Z]+(,|\s|:)+[A-Z]+(.*)')
    ac_status = re.compile(r'(^([A-Z])\w+\sStatus\w)')
    ref = re.compile(r'^Ref.*')
    report = re.compile(r'^Report.*')

    # Error handling is important so we need to find this seperately
    # because of assignment I'll avoid doing that and show to the
    # quickist way to get it by assuming that image data is there
    print(list(filter(name.match, data)))
    sample_data = {
            'Name': list(filter(name.match, data))[0],
            'LabNo.': list(filter(lab_number.match, data))[0],
            'Age': " ".join(list(filter(age.match, data))[0].split(' ')[-2:]),
            'Gender': list(filter(gender.match, data))[0].split(' ')[-1],
            'A/c Status': list(filter(ac_status.match, data))[0][-1],
            'Ref By': list(filter(ref.match, data))[0].split(' ')[-1],
            'Report Status': list(filter(report.match, data))[0].split(' ')[-1],
            'Collected': list(filter(date.match, data))[0],
            'Received': list(filter(date.match, data))[1],
            'Reported': list(filter(date.match, data))[2],
            }

    test_name = list(filter(test.match, data))
    value_number = list(filter(value.match, data))
    count = 0

    for name in test_name:
        if count < len(value_number):
            sample_data[name] = value_number[count]
        else:
            sample_data[name] = '-'

    return sample_data


def report2(path):
    data = image_to_text(path).split('\n')

    name = re.compile(r'^[A-Z]{,20}.*([A-Z]$)')
    doctor = re.compile(r'^Dr\..*')
    date = re.compile(r'(\d+/\d+/\d+)')
    age = re.compile(r'^Age.*')
    report = re.compile('^Report\sNo.*')
    ignore = re.compile(r'^([A-Z]+\s[A-Z]+)')
    ignore_2 = re.compile(r'.*[a-z]:$')
    report_key = re.compile(r'(?!.*Reactive|Contact$)^[A-Z].*[a-z]$|^[A-Z]{3}')
    report_value = re.compile(r'(?=(.*Reactive$))|(?!\d+/\d+/\d+|.*\)$)\d+')

    sample_data = {
            'Patient Name': list(filter(name.match, data))[0],
            'Ref By': list(filter(doctor.match, data))[0],
            'Dated': list(filter(date.match, data))[0],
            'Age': list(filter(age.match, data))[0].split(' ')[-1],
            'Report No.': list(filter(report.match, data))[0].split(' ')[-1],
            }

    count = data.index('Normal') + 1
    sample_key = list(filter(report_key.match, data[count:]))
    sample_value = list(filter(report_value.match, data))

    # We don't know which value is for which key, so assuming that we have order
    # We will zip key value pair. Using coordinates will give more accurate
    # results
    for i in zip(sample_key, sample_value):
        sample_data[i[0]] = i[1]

    return sample_data


if __name__ == '__main__':
    print('Report 1')
    print(report1('report1.jpg'))
    print('Report 2')
    print(report2('report2.jpg'))
