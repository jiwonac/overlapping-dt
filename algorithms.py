import random
import pprint
import math
import pprint
from datagenerator import data_generator

def argmin(iterable):
    return min(enumerate(iterable), key=lambda x: x[1])[0]

def argmax(iterable):
    return max(enumerate(iterable), key=lambda x: x[1])[0]

def binary_dt(dataset, query, type):
	"""
	Implements the known binary DT algorithm. 
	Parameters:
		dataset: a properly formatted dataset generated by data_generator
		query: list of count requirements for each group
		type: a string identifying the data source choice rule used
			"orig": original (data source with maximum % of minority group)
			"ours": argmax{[1 - P(overlap)] / [1 + P(overlap)]}
			"random": choose data sources randomly
			"ratio": choose more common groups rarely and rare groups more often
	"""
	# Things to keep track of
	num_sources = dataset["num_sources"]
	unified_set = set()
	expected_from_sources = [None] + [0 for x in range(num_sources + 1)]
	total_cost = 0.0
	total_sampling_attempts = 0
	# Find the minority group overall
	num_groups = dataset["num_groups"]
	group_counts = [0.0 for x in range(num_groups)]
	group_dists = dataset["group_dists"]
	for source in range(1, num_sources  + 1):
		for group in range(num_groups):
			group_counts[group] += group_dists[source][group]
	minority_group = argmin(group_counts)
	# Keep on adding data points to unified set
	while(all(query)): # While at least one count requirement is not 0
		total_sampling_attempts += 1
		# Choose the optimal data source
		data_source = None
		if (type == "orig"):
			minority_group_ratios = [float('-inf')] + [group_dists[source][minority_group]
				/ (len(dataset["sources"][source]) * dataset["costs"][source]) for source in range(1, num_sources + 1)]
			data_source = argmax(minority_group_ratios)
		elif (type == "ours"):
			expected_overlap_prob = [None] + [expected_from_sources[source] 
				/ len(dataset["sources"][source]) for source in range(1, num_sources + 1)]
			#print(expected_overlap_prob)
			minority_group_ratios = [float('-inf')] + [
				(group_dists[source][minority_group] / len(dataset["sources"][source])) 
				* math.pow(((1 - expected_overlap_prob[source]) / (1 + expected_overlap_prob[source])), 1)
				* (1 / dataset["costs"][source]) for source in range(1, num_sources + 1)]
			data_source = argmax(minority_group_ratios)
		elif (type == "random"):
			data_source = random.randrange(1, num_sources)
		else:
			return
		# Sample a data point from chosen source
		new_point = random.choice(dataset["sources"][data_source])
		new_point_val = new_point["val"]
		total_cost += dataset["costs"][data_source] # Pay cost			
		# Duplicate check & branch
		if (new_point_val not in unified_set): # Not Overlap
			unified_set.add(new_point_val)
			# Update expected number of samples
			for source in range(1, num_sources + 1):
				if (source == data_source):
					expected_from_sources[data_source] += 1.0
				else:
					mytuple = ()
					for s in range(1, num_sources + 1):
						if (s == data_source or s == source):
							mytuple += (s,)
						else:
							mytuple += (-s,)
					expected_from_sources[source] += (dataset["distribution"][mytuple]) / (len(dataset["sources"][source]))
			# Update query
			new_group = new_point["group"]
			query[new_group] -= 1
	return unified_set, total_cost, total_sampling_attempts

def general_dt(dataset, query, type):
	"""
	Implements the known general DT algorithm. 
	Parameters:
		dataset: a properly formatted dataset generated by data_generator
		query: list of count requirements for each group
		type: a string identifying the data source choice rule used
			"orig": original (data source with maximum % of minority group)
			"ours": argmax{[1 - P(overlap)] / [1 + P(overlap)]}
			"random": choose data sources randomly
			"ratio": choose more common groups rarely and rare groups more often
	"""
	# Things to keep track of
	num_sources = dataset["num_sources"]
	unified_set = set()
	expected_from_sources = [None] + [0 for x in range(num_sources + 1)]
	total_cost = 0.0
	total_sampling_attempts = 0
	# Find the minority group overall
	num_groups = dataset["num_groups"]
	# Keep on adding data points to unified set
	while(True):
		for minority_group in range(num_groups):
			if (not all(query)):
				return unified_set, total_cost, total_sampling_attempts
			elif (query[minority_group] > 0):
				total_sampling_attempts += 1
				# Choose the optimal data source
				data_source = None
				if (type == "orig"):
					minority_group_ratios = [float('-inf')] + [group_dists[source][minority_group]
						/ (len(dataset["sources"][source]) * dataset["costs"][source]) for source in range(1, num_sources + 1)]
					data_source = argmax(minority_group_ratios)
				elif (type == "ours"):
					expected_overlap_prob = [None] + [expected_from_sources[source] 
						/ len(dataset["sources"][source]) for source in range(1, num_sources + 1)]
					#print(expected_overlap_prob)
					minority_group_ratios = [float('-inf')] + [
						(group_dists[source][minority_group] / len(dataset["sources"][source])) 
						* math.pow(((1 - expected_overlap_prob[source]) / (1 + expected_overlap_prob[source])), 1)
						* (1 / dataset["costs"][source]) for source in range(1, num_sources + 1)]
					data_source = argmax(minority_group_ratios)
				elif (type == "random"):
					data_source = random.randrange(1, num_sources)
				else:
					return
				# Sample a data point from chosen source
				new_point = random.choice(dataset["sources"][data_source])
				new_point_val = new_point["val"]
				total_cost += dataset["costs"][data_source] # Pay cost			
				# Duplicate check & branch
				if (new_point_val not in unified_set): # Not Overlap
					unified_set.add(new_point_val)
					# Update expected number of samples
					for source in range(1, num_sources + 1):
						if (source == data_source):
							expected_from_sources[data_source] += 1.0
						else:
							mytuple = ()
							for s in range(1, num_sources + 1):
								if (s == data_source or s == source):
									mytuple += (s,)
								else:
									mytuple += (-s,)
							expected_from_sources[source] += (dataset["distribution"][mytuple]) / (len(dataset["sources"][source]))
					# Update query
					new_group = new_point["group"]
					query[new_group] -= 1

if __name__ == "__main__":
	pp = pprint.PrettyPrinter()
	experiments = 30
	types = ["orig", "ours", "random"]
	### Experiment 1: Binary sources, binary equi-cost
	# Generate dataset
	distribution = {(1, -2): 70, (-1, 2): 70, (1, 2): 30}
	costs = [None, 1.0, 1.0]
	group_dists = [None, (60, 40), (70, 30)]
	dataset = data_generator(2, distribution, costs, 2, group_dists)
	# Conduct experiment
	query_counts = [5, 10, 20, 30, 40, 50]
	results = {"orig": [], "ours": [], "random": []}
	for alg_type in types: # For each type of algorithm
		for query_count in query_counts: # For each query count
			total_cost_sum = 0
			for i in range(experiments): # Conduct experiment several times
				query = [query_count, query_count]
				unified_set, total_cost, sampling_attempts = binary_dt(dataset, query, alg_type)
				total_cost_sum += total_cost
			results[alg_type].append(total_cost_sum / experiments)
	print("Experiment 1: Binary sources, binary groups equi-cost using binary DT algorithm.")
	print("Query counts: ", query_counts)
	pp.pprint(results)
	print()
	
	### Experiment 2: Binary sources, binary groups skewed-cost.
	costs = [None, 2.0, 1.0]
	dataset = data_generator(2, distribution, costs, 2, group_dists)
	# Conduct experiment
	query_counts = [5, 10, 20, 30, 40, 50]
	results = {"orig": [], "ours": [], "random": []}
	for alg_type in types: # For each type of algorithm
		for query_count in query_counts: # For each query count
			total_cost_sum = 0
			for i in range(experiments): # Conduct experiment several times
				query = [query_count, query_count]
				unified_set, total_cost, sampling_attempts = binary_dt(dataset, query, alg_type)
				total_cost_sum += total_cost
			results[alg_type].append(total_cost_sum / experiments)
	print("Experiment 2: Binary sources, binary groups skewed-cost using Binary DT algorithm.")
	print("Query counts: ", query_counts)
	pp.pprint(results)
	print()

	# Experiment 3: Five sources, binary groups equi-cost
	distribution = {
		(1, -2, -3, -4, -5): 40,
		(-1, 2, -3, -4, -5): 40,
		(-1, -2, 3, -4, -5): 40,
		(-1, -2, -3, 4, -5): 40,
		(-1, -2, -3, -4, 5): 40,
		(1, 2, -3, -4, -5): 15,
		(1, -2, 3, -4, -5): 15,
		(1, -2, -3, 4, -5): 15,
		(1, -2, -3, -4, 5): 15,
		(-1, 2, 3, -4, -5): 15,
		(-1, 2, -3, 4, -5): 15,
		(-1, 2, -3, -4, 5): 15,
		(-1, -2, 3, 4, -5): 15,
		(-1, -2, 3, -4, 5): 15,
		(-1, -2, -3, 4, 5): 15,
		(-1, -2, 3, 4, 5): 0,
		(-1, 2, -3, 4, 5): 0,
		(-1, 2, 3, -4, 5): 0,
		(-1, 2, 3, 4, -5): 0,
		(1, -2, -3, 4, 5): 0,
		(1, -2, 3, -4, 5): 0,
		(1, -2, 3, 4, -5): 0,
		(1, 2, -3, -4, 5): 0,
		(1, 2, -3, 4, -5): 0,
		(1, 2, 3, -4, -5): 0,
		(-1, 2, 3, 4, 5): 0,
		(1, -2, 3, 4, 5): 0,
		(1, 2, -3, 4, 5): 0,
		(1, 2, 3, -4, 5): 0,
		(1, 2, 3, 4, -5): 0
	}
	costs = [None, 1.0, 1.0, 1.0, 1.0, 1.0]
	group_dists = [None, (90, 10), (80, 20), (70, 30), (60, 40), (50, 50)]
	dataset = data_generator(5, distribution, costs, 2, group_dists)
	# Conduct experiment
	query_counts = [5, 10, 20, 30, 40, 50]
	results = {"orig": [], "ours": [], "random": []}
	for alg_type in types: # For each type of algorithm
		for query_count in query_counts: # For each query count
			total_cost_sum = 0
			for i in range(experiments): # Conduct experiment several times
				query = [query_count, query_count]
				unified_set, total_cost, sampling_attempts = general_dt(dataset, query, alg_type)
				total_cost_sum += total_cost
			results[alg_type].append(total_cost_sum / experiments)
	print("Experiment 3: Five sources, binary groups equi-cost using general DT algorithm.")
	print("Query counts: ", query_counts)
	pp.pprint(results)
	print()

	# Experiment 4: Five sources, binary groups skewed-cost
	costs = [None, 1.0, 1.25, 1.5, 1.75, 2.0]
	dataset = data_generator(5, distribution, costs, 2, group_dists)
	# Conduct experiment
	query_counts = [5, 10, 20, 30, 40, 50]
	results = {"orig": [], "ours": [], "random": []}
	for alg_type in types: # For each type of algorithm
		for query_count in query_counts: # For each query count
			total_cost_sum = 0
			for i in range(experiments): # Conduct experiment several times
				query = [query_count, query_count]
				unified_set, total_cost, sampling_attempts = general_dt(dataset, query, alg_type)
				total_cost_sum += total_cost
			results[alg_type].append(total_cost_sum / experiments)
	print("Experiment 3: Five sources, binary groups skewed-cost using general DT algorithm.")
	print("Query counts: ", query_counts)
	pp.pprint(results)
	print()