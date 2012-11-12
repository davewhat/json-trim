#Summary

json-trim is a tool used to reduce the amount of JSON sent from a server.  It acts as a simple proxy server between the client and server.

#Usage

to start a local proxy server on port 8080:

    python server.py

note: you need to edit server.py to set the target server.

#Filtering

By default, all members of an object are filtered.  json-trim's philosophy is to require explicit approval.  Any values and nested objects which should be proxied are expressed in the JSON filter.

example:

    {
     "attributes": ["keep_this_attribute", "and_this_one"]
     "childObject" : {
         "attributes": ["child_object_attribute_to_keep"]
     }
    } 

In the example above, the attributes *keep\_this\_attribute* and *and\_this\_one* will be preserved.  All nested objects will be removed except for the one named *childObject*.  The attribute *child\_object\_attribute\_to\_keep* on *childObject* will also be preserved.

#Advanced Filtering

Child object filters can express required conditions for them to be used.  This is done using the following key name:

    child_attribute#parent_attribute#parent_attribute_required_value

example:

    {
     "attributes": ["name", "ageClass"]
     "address#ageClass#adult": {
         "attributes": ["address", "city", "state"]
     }
     "address#ageClass#child": {
         "attributes": ["city", "state"]
     }
    }

In the example above, the *address* object will preserve *address*, *city*, and *state* if the person has an *ageClass* of *adult*.  If *ageClass* is *child* then only *city* and *state* are preserved.  (Note: if *ageClass* is any other value, such as *senior*, it will be dropped.)

#to do

1. basic code review (this is really rough at this point)
1. command line arguments
1. make sure POST is working