from hl7apy.parser import parse_message
from pymongo import MongoClient
import sys


def parse_hl7(hl7_msg=None):
    """Parses an HL7 message into a JSON-LD document suitable for persisting
    into MongoDB.

    Parameters
    ----------
    hl7_msg : str
        A string containing the HL7 message to be parsed.

    Returns
    -------
    list, tuple
        An iterable of Python dictionaries, where the first item in the iterable
        is the Patient resource and the second is the Observation resource from
        the HL7 message.
    """
    # parses the hl7 message to access segments, fields and components within the message
    message = parse_message(hl7_msg, find_groups=False)

    # creates a dictionary corresponding to the Patient resource
    patient_dict = {"resourceType": "Patient", "identifier": [{"use": "usual", "label": "MRN", 
    "system": "urn:oid:2.16.840.1.113883.19.5", "value": message.PID.pid_3.pid_3_1.value}], 
    "gender": {"coding": [{"system": "http://hl7.org/fhir/v3/AdministrativeGender", "code": message.PID.pid_8.value}]}, 
    "birthDate": message.PID.pid_7.value[:4] + "-" + message.PID.pid_7.value[4:6] + "-" + message.PID.pid_7.value[6:], 
    "managingOrganization": {"reference": "Organization/2.16.840.1.113883.19.5", "display": "MIMIC2"},}
    
    # creates a dictionary corresponding to the Observation resource
    obs_dict = {"resourceType": "Observation", "name": {"coding": [{"system": "http://loinc.org", 
    "code": message.OBX.obx_3.obx_3_1.value, "display": message.OBR.obr_4.obr_4_2.value}]}, 
    "valueQuantity": {"value": message.OBX.obx_5.value}, "issued": "2013-04-03T15:30:10+01:00", 
    "status": "final", "subject": {"reference": "Patient/" + message.PID.pid_3.pid_3_1.value, 
    "display": "P. van de Heuvel"},}
    
    return patient_dict, obs_dict


def save(data, db_name="encounters", port=27017):
    """Saves the data to MongoDB at the specified port and database.

    If the "resourceType" of the data is HL7's "Patient" then the data should
    be saved to the MongoDB collection called "patients" (all lowercase). If the
    "resourceType" is "Observation" then the data should be saved to the
    "observations" collection.

    Parameters
    ----------
    data : dict, list
        A dictionary or a list of dictionaries where each dictionary is to be
        saved into MongoDB. Dictionaries should represent a FHIR resource.
    db_name: str
        The name of the MongoDB database to save data to. DO NOT change the
        default value.
    port : int
        The port at which MongoDB is listening. Defaults to 27017, MongoDB's
        default port. Again, DO NOT change the default value.

    Returns
    -------
    list
        A list containing the ObjectID's of the document(s) that were saved.
    """
    # connects to the host and port
    client = MongoClient('localhost', port)
    # access the database to save data to
    db = client[db_name]
    object_ids = []
    # check to see if data variable is of type dictionary or list of dictionaries
    if isinstance(data, dict):
        # check to see if resourceType is Patient or Observation
        if data['resourceType'] == 'Patient':
            # access the collection to save the data to
            patients = db.patients
            # inserts the data document to the collection within the database
            _id = patients.insert(data)
            # adds the unique ObjectID for the document that was inserted into the collection to a list of ObjectID's
            object_ids += [_id]
        elif data['resourceType'] == 'Observation':
            observations = db.observations
            _id = observations.insert(data)
            object_ids += [_id]
    elif isinstance(data, list):
        # if the data is of type list it will loop through the list of dictionaries and add each one to the correct collection
        for i in data:
            if i['resourceType'] == 'Patient':
                patients = db.patients
                _id = patients.insert(i)
                object_ids += [_id]
            elif i['resourceType'] == 'Observation':
                observations = db.observations
                _id = observations.insert(i)
                object_ids += [_id]
    return object_ids


if __name__ == '__main__':
    args = sys.argv[1:]
    for input_file in args:
        lines = [line.rstrip() for line in open(input_file)]
        msh = lines[0] + "\r"
        pid = lines[1] + "\r"
        obx = lines[2] + "\r"
        obr = lines[3]
        s = msh + pid + obx + obr
        patient_dict, obs_dict = parse_hl7(s)
        save(patient_dict, db_name="encounters", port=27017)
        save(obs_dict, db_name="encounters", port=27017)

