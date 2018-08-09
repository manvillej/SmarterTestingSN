# SmarterTestingSN
SmarterTestingSN

This project is an experiment on improving the testing capabilities of a platform called ServiceNow.
[ServiceNow](https://www.servicenow.com/) is a Platform as a service that is used to host a specific set of applications for the purpose of delivering IT services.
ServiceNow is an extremely data driven application with records, forms, server side code, client side code, and code libraries represented as records in tables.
Despite this highly segmented parts, testing is a very blunt instrument. Tests are generally user tests and grouped into test suites.
This may be suitable for user acceptance testing, but I believe there is a better way.

By creating a mapping between specific objects and specific tests, this tool is able to identify exactly what tests should be run by which objects have been impacted.
Right now, the tool is limited to just direct relationships between an object and a test.
In the future, Objects should be able to be related to other objects.
This will allow a change to an object will pull tests for objects that were impacted by the original object.

Generally, when a company is using ServiceNow, they have three environments or instances of ServiceNow: a Development, Test, and Production environment.
Changes are moved through update sets which are just XML files. I learned through this project that their XML files are very complicated.

Once I converted the xml to json, I identified 7 different formats for the first layer of keys. When I investigated just one of those, the second layer has 12 different formats.
The XMl files generally has 5 layers of keys. I also discovered that while the xmltodict translated most of the file, the payload of an individual update was a string in an xml format which also had to be converted to json.

## My tool only handles one path at this moment which is:

1. ["unload"]["sys_update_xml"] -> returns a list of dicts, must be a list of dicts
2. ["payload"] -> returns xml string which is translated into a dict
3. ["record_update"]["@table"] -> must have @table key or it is skipped, return table acted on
4. ["Type"] -> return type of object created

## This current iteration has several limitations that I would feel needs to be addressed before anyone should rely on it

 * No security around XML upload
 * Not able link objects
 * Not able to decode/handle every possible type of update in an update set
 * create users inactive until admin activates them. Admin should be notified by email

## There are several feature I would also like to add

 * Store the XML files and allow them to be retreived/downloaded
 * Enable javascript code to be analyzed when pulled from servicenow instance
 * allow multiple update sets to be analyzed together and detect collisions
 * automatically create test suite from the tests found in an upload


## This application requires a few environment variables to run and will throw a runtime error if it does not find them

 * "SN_INSTANCE" - instance name of the servicenow.
 * "SN_USERNAME" - username of the user for interacting with that instance
 * "SN_PASSWORD" - password for interacting with that instance

## Some notes

 * Only staff can upload records, look at upload, and add relationships
 * logged in users can see SNObject and tests and see the tests/object that affect them
