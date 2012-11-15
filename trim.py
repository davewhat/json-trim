import json

example = {
	'people': [
		{
			'first': 'David',
			'last': 'W',
			'favoriteColor': 'Red', # who cares?
			'gender': 'male',
			'photo' : {
				'name': 'david.jpg',
				'size': {'width': 480, 'height': 640},
				'fileSize': 32465 # who cares?
			},
			'backpack': 
			[
				{
					'type': 'camera', # who cares?
					'object':
					{
						'brand': 'Nikon',
						'model': '4D',
						'battery-life': '2 hours'
					}					
				},
				{
					'type': 'sandwich', # for males, we care about sandwich
					'object':
					{
						'kind': 'Tuna',
						'mustard': False,
						'cost': 4.00,
					}
				}
			]
		},{
			'first': 'Angela',
			'last': 'W',
			'favoriteColor': 'Yellow', # who cares?
			'gender': 'female',
			'photo' : {
				'name': 'angela.jpg',
				'size': {'width': 480, 'height': 640},
				'fileSize': 32465 # who cares?
			},
			'backpack': 
			[
				{
					'type': 'camera',  # for females, we care about camera
					'object':
					{
						'brand': 'Cannon',
						'model': 'D5',
						'battery-life': '5 hours'
					}					
				},
				{
					'type': 'sandwhich', #who cares?
					'object':
					{
						'kind': 'Turkey',
						'mustard': True,
						'cost': 5.00,
					}
				}
			]
		}
	]
}
# print json.dumps(example)	
# data = json.loads(read_data)


# with open('lwassers.json', 'r') as f:
#     read_data = f.read()
# f.closed	

filters = {    
	'attributes': ['people'],
	'people': {
		# note, we drop favoriteColor from the attribute list as we don't care about it
		'attributes': ['first', 'last', 'gender'],
		# for nested dictionaries/arrays we write additional filter logic
		'photo': {
			# note, we drop fileSize from photos
			'attributes': ['name', 'size']
			# no nested filter logic as there are no dictionary items on a photo
		},
		# for nested dictionaries we can have advanced logical filters
		'backpack#gender#female': {
			'attributes': ['type', 'object'],
			# for females, keep camera information
			'object#type#camera': {
				'attributes': ['make', 'model']
			}
		},
		'backpack#gender#male': {
			# for males, keep sandwich information
			'attributes': ['type', 'object'],
			'object#type#sandwich': {
				'attributes': ['kind', 'mustard']
			}
		}
	}
}

# returns True if compound 'filter_key' is valid for a 'key' in the 'input' dictionary
def compound_key_matcher(filter_key, key, input):
	if (filter_key == key):
		#basic filter_key matching
		return True
	if len(filter_key.split('#'))==3:
		#compound filter_key matching
		(k, a, v) = filter_key.split('#')
		if k==key:
			if a in input.keys():
				return (k==key and input[a]==v)
	return False


# applies the filter to a given input. set debug True for verbose output
def strip(input, filters, debug = False):
	# separate value keys from object keys
	value_keys = []
	object_keys = []
	for key in input.keys():
		if input[key].__class__ == type({}):
			object_keys.append(key)
		elif input[key].__class__ == type([]):
			# could be an array of values, which we treat as a value
			if len(input[key]) > 0:
				# test the first element
				if input[key][0].__class__ == type({}):
					object_keys.append(key)
				elif input[key][0].__class__ == type([]):
					# is it a nested array of values or objects? we guess.
					print("warning: arrays of arrays are treated as objects.")
					object_keys.append(key)
				else:
					value_keys.append(key)
			else:
				# no elements to test, fall back to the filter rules
				object_filter_keys = filter(lambda filter_key: compound_key_matcher(filter_key, key, input), filters.keys())
				if object_filter_keys > 0:
					object_keys.append(key)
				else:
					value_keys.append(key)
		else:
			value_keys.append(key)


	if filters.has_key('!_allow_all'):
		# debug logic
		if debug:
			for key in object_keys:
				if input[key].__class__ == type({}):
					# handle as a nested dictionary
					strip(input[key], filters, debug)
				elif input[key].__class__ == type([]):
					# handle as a nested array
					map(lambda x: strip(x, filters, debug), input[key])							
				input[key.upper()] = input[key]
				input.pop(key)
			for key in value_keys:
				input[key.upper()] = input[key]
				input.pop(key)
	else:
		for key in object_keys:
			# find object filter to apply
			object_filter_keys = filter(lambda filter_key: compound_key_matcher(filter_key, key, input), filters.keys())
			if len(object_filter_keys) != 1:
				# nested dictionaries and arrays require filters
				if not debug:
					input.pop(key)				
			else:
				if input[key].__class__ == type({}):
					# handle as a nested dictionary
					strip(input[key], filters[object_filter_keys[0]], debug)
				else:
					# handle as a nested array
					map(lambda x: strip(x, filters[object_filter_keys[0]], debug), input[key])				
				# debug logic
				if debug:
					input[key.upper()] = input[key]
					input.pop(key)			
		for key in value_keys:
			if not key in filters['attributes']:
				# remove attributes not explicitly allowed
				if not debug:
					input.pop(key)			
			else:
				# debug logic
				if debug:
					input[key.upper()] = input[key]
					input.pop(key)	
