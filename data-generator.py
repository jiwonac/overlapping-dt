import pprint

def data_generator(num_sources, distribution, costs, num_groups, group_dists):
	"""
	Generates overlapping synthetic data based on number of sources and a precise
	specification of the distribution of data. 

	Parameters:
		num_sources (int): a nonnegative number of sources
		distribution (dict): a dictionary that maps from a tuple of sources to a
							 nonnegative number of tuples in the overlap
							 e.g.: (1, -2): 3, (-1, 2): 2, (1, 2): 1
							 means 3 tuples in source 1 but not in source 2, 
							 2 tuples in source 2 but not in source 1, and
							 1 tuple in source 1 and 2. 
							 The dictionary must be correctly and thoroughly
							 formatted as this function doesn't check if it
							 is valid. 
		costs (list): a list of costs for each source of length num_sources
		num_groups (int): a positive number of groups
		group_dists (list): a list of group distributions
							e.g. [(5, 6), (1, 2), (2, 3)] is a valid group 
							distribution 3 data sources and 2 groups. 
	
	Returns:
		a list of data sources
		a data point is a dictionary: {"val": "some_string", "cost": some_float, 
									   "group": some_int}
		a data source is a list of data points
	"""
	dataset = [[] for source in range(num_sources + 1)]
	# Now generate the list of strings
	for key, value in distribution.items():
		if (value <= 0): # Skip string appending if there is 0 strings
			continue
		# First generate the template string
		template_string = "" # of form: 1_!2_!3_4...
		for source in key:
			template_string += str(source) + ","
		# Now generate the actual strings and add them to all
		for source in key:
			source_cost = costs[abs(source)]
			if source > 0:
				for i in range(value):
					new_string = template_string + str(i)
					data_point = {"val": new_string, "cost": source_cost}
					dataset[source].append(data_point)
	# Now assign each string in a data source a group
	for source in range(1, num_sources + 1):
		group_dist = group_dists[source]
		i = 0
		for group in range(num_groups):
			for j in range(group_dist[group]):
				dataset[source][i]["group"] = group
				i += 1
	return dataset
			


# Test the data generator
if __name__ == "__main__":
	num_sources = 3
	distribution = {(1, -2, -3): 10, (-1, 2, -3): 20, (-1, -2, 3): 30, 
					(1, 2, -3): 5, (1, -2, 3): 4, (-1, 2, 3): 3, (1, 2, 3): 1}
	costs = [None, 1.0, 2.0, 3.0]
	num_groups = 2
	group_dists = [None, (17, 3), (9, 20), (30, 7)]

	dataset = data_generator(num_sources, distribution, costs, num_groups, group_dists)
	pp = pprint.PrettyPrinter(width=41, compact=True)
	pp.pprint(dataset)