# Parse HL7v2 Message Using the HL7apy Library #

## The hypothetical scenario: ##

You are part of a team tasked with building an analytics system for a new
set of data. Luckily, you are able to leverage the infrastructure of
a previous project. So, for this project, all you you need to do is
write 2 functions to replace the key data organization functionality.
The first function will be given an HL7 string and will return a Python
data structure. The second function will take the Python data structure
and save it to MongoDB.

### This task has been broken down as follows: ###

1. **Receive and parse HL7 messages using the HL7apy library**

   The first function called `parse_hl7()` will take
   a single string as an input parameter. This string represents
   a single, complete HL7 message. It then extracts the relevant
   fields from the HL7 message and stores these data in a Python data
   structure. 

   The `parse_hl7()` function will return a Python dictionary that
   encapsulates the FHIR structure. This dictionary will be passed to
   the next function for persistence to the database.

2. **Process and structure the data with UMLS concepts and JSON-LD**

   Based on the documentation, the appropriate terminology and codes were
   chosen for best translating the data from the HL7 message. For example,
   one of the fields within the HL7 message may be a CBC lab test as 
   described in the documentation.

   Every HL7 message that is processed in this example will be an ORU R01 message  
   containing a PID segment identifying the patient, an OBR segment identifying the
   test being ordered, and an OBX segment identifying the result. This
   data is taken from a real dataset that has been de-identified and
   reflects the original data including those test results that are not
   backed by LOINC codes.

   As such, everything is either matched to LOINC or not matched to anything.

   The specific format of the JSON documents that were created are:

   ### Patient

    ```json
    {
    "resourceType": "Patient",
    "identifier": [
     {
      "use": "usual",
      "label": "MRN",
      "system": "urn:oid:2.16.840.1.113883.19.5",
      "value": "12345" 
     }
    ],
    "gender": {
     "coding": [
      {
       "system": "http://hl7.org/fhir/v3/AdministrativeGender",
       "code": "M" 
      }
     ]
    },
    "birthDate": "1932-09-24", 
    "managingOrganization": {
     "reference": "Organization/2.16.840.1.113883.19.5",
     "display": "MIMIC2"
    },
    }
    ```

   ### Observation ###

    ```json
    {
     "resourceType": "Observation",
     "name": {
      "coding": [
       {
        "system": "http://loinc.org",
        "code": "2339-0", 
        "display": "Glucose [Mass/volume] in Blood"
       }
      ]
     },
     "valueQuantity": {
      "value": 6.3, 
     },
     "issued": "2013-04-03T15:30:10+01:00",
     "status": "final",
     "subject": {
      "reference": "Patient/f001", 
      "display": "P. van de Heuvel"
     },
    }
    ```

3. **Save the JSON-LD document to MongoDB**

   Takes the return value of the `parse_hl7()` function as an input to a second 
   function called `save()`. This function can actually accept two
   different types of inputs - a Python dictionary or a Python list of
   dictionaries. If the argument is a dictionary, it will just save this
   to MongoDB. If the argument is a list of dictionaries, it will
   sequentially save each dictionary to MongoDB.


