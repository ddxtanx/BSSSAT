import csv

classes =[]
with open('data/Adams-motivic-E2.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        classes.append({"name": row['name'], "stem": int(row['stem']), "Adams filtration": int(row['Adams filtration']), "weight": int(row['weight']), "tautorsion": int(row['tautorsion'])})


def degree(element):
    return (element["stem"], element["Adams filtration"], element["weight"])

def add_degree(degree1, degree2):
    return (degree1[0] + degree2[0], degree1[1] + degree2[1], degree1[2] + degree2[2])


def sfdegree(element):
        return (element["stem"], element["Adams filtration"])
    
group_by_sf = {}
for element in classes:
    if sfdegree(element) not in group_by_sf:
        group_by_sf[sfdegree(element)] = [element]
    else:
        group_by_sf[sfdegree(element)].append(element)

sf_list = list(group_by_sf.keys())


def element_by_degree(a_degree):
    elements_in_degree = []
    for element in group_by_sf.get((a_degree[0], a_degree[1]), []):
        if degree(element)[2] == a_degree[2]:
            elements_in_degree.append(element)
        if degree(element)[2] > a_degree[2]:
            difference_degree =   degree(element)[2] - a_degree[2]
            if int(element["tautorsion"]) == 0:
                 elements_in_degree.append({
                    "name": f"tau^{difference_degree} {element['name']}",
                    "stem": a_degree[0],
                    "Adams filtration": a_degree[1],
                    "weight": a_degree[2],
                })
            if int(element["tautorsion"]) > 0 and difference_degree > int(element["tautorsion"]):
                  elements_in_degree.append({
                     "name": f"tau^{difference_degree} {element['name']}",
                    "stem": a_degree[0],
                    "Adams filtration": a_degree[1],
                    "weight": a_degree[2],
                })
        else:
            continue
    return elements_in_degree

def possible_differentials_by_r(source_degree,r):
    source_elements = element_by_degree(source_degree)
    target_degree = add_degree(source_degree, (r-1, 1, r))
    target_elements = element_by_degree(target_degree)
    differentials = {}
    for source in source_elements:
        source_name = source['name']
        if source_name not in differentials:
             differentials[source_name] = []
        for target in target_elements:
            differentials[source_name].append(f"d_{r}({source_name})=rho^{r} {target['name']}")
    return differentials
            
def group_by_degree(bounds):
    grouped = {}
    for s in range(bounds[0] + 1):
        for f in range(bounds[1] + 1):
            for w in range(-bounds[2], int(bounds[2]) + 1):
                a_degree = (s, f, w)
                elements = element_by_degree(a_degree)
                if elements:
                    grouped[a_degree] = elements
    return grouped

# test
# print(group_by_degree((10, 10, 10)))


def possible_differentials_in_a_range(bounds,r):
    grouped = group_by_degree(bounds)
    differentials = {}
    degree_list = set(grouped.keys())
    for source_degree, source_elements in grouped.items():
        target_degree = add_degree(source_degree, (r-1, 1, r))
        if target_degree in degree_list:
            for source in source_elements:
                source_name = source['name']
                if source_name not in differentials:
                    differentials[source_name] = []
                for target in grouped[target_degree]:
                    differentials[source_name].append(f"d_{r}({source_name})=rho^{r} {target['name']}")
    return differentials

# test
# differentials = possible_differentials_in_a_range((10,10,10), 1)
# for element, diffs in differentials.items():
#    print(f"Possible d_1 differentials for {element}:")#   for diff in diffs:
#   print(diffs)

def possible_differentials_by_source(source_degree, bounds):
    grouped = group_by_degree(bounds)
    differentials = {}
    degree_list = set(grouped.keys())
    source_elements = grouped.get(source_degree, [])
    max_r = min(bounds[0] - source_degree[0] + 1, bounds[2] - source_degree[2])
    if max_r < 1 or not source_elements:
        return {}
    for r in range(1, max_r + 1):
        target_degree = add_degree(source_degree, (r - 1, 1, r))
        if target_degree in degree_list:
            for source in source_elements:
                source_name = source['name']
                if source_name not in differentials:
                    differentials[source_name] = []
                for target in grouped[target_degree]:
                    differentials[source_name].append(f"d_{r}({source_name})=rho^{r} {target['name']}")
    return differentials

#test
#differentials = possible_differentials_by_source((15,8,3),(100, 60, 50))
#for element, diffs in differentials.items():
#   print(f"Possible d_r differentials for {element}:")#   for diff in diffs:
#   print(diffs)


def possible_differentials_within_bounds(bounds):
    grouped = group_by_degree(bounds)
    degree_list = set(grouped.keys())
    differentials = {}
    # Single-pass counting: avoid recomputing possible_differentials_by_source
    # (which rebuilds grouped) for every source degree.
    for source_degree, source_elements in grouped.items():
        max_r = min(bounds[0] - source_degree[0] + 1, bounds[2] - source_degree[2])
        if max_r < 1 or not source_elements:
            continue
        for r in range(1, max_r + 1):
            target_degree = add_degree(source_degree, (r - 1, 1, r))
            if target_degree in degree_list:
                 for source in source_elements:
                     source_name = source['name']
            if source_name not in differentials:
                            differentials[source_name] = []
                            for target in grouped[target_degree]:
                               differentials[source_name].append(f"d_{r}({source_name})=rho^{r} {target['name']}")
    return differentials

def counting_values(classes):
    counting = {}
    for element, values in classes.items():
        counting[element] = len(values)
    return counting

#test
differentials = possible_differentials_within_bounds((110,60,50))
counting = counting_values(differentials)
maximal_number_from_one_source = max(counting.values()) if counting else 0

def finding_sources_with_fixed_number_of_differentials(classes, number):
    sources = []
    for element, values in classes.items():
        if len(values) == number:
            sources.append(element)
    return sources
