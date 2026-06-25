import csv
import json

def get_classes():
    classes = []
    with open('Adams-motivic-E2.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            classes.append({"name": row['name'], "stem": int(row['stem']), "Adams filtration": int(row['Adams filtration']), "weight": int(row['weight']), "tautorsion": int(row['tautorsion'])})
    return classes

def degree(element):
    return (element["stem"], element["Adams filtration"], element["weight"])

def add_degree(degree1, degree2):
    return (degree1[0] + degree2[0], degree1[1] + degree2[1], degree1[2] + degree2[2])


def sfdegree(element):
        return (element["stem"], element["Adams filtration"])

group_by_sf = {}
for element in get_classes():
    if sfdegree(element) not in group_by_sf:
        group_by_sf[sfdegree(element)] = [element]
    else:
        group_by_sf[sfdegree(element)].append(element)

sf_list = list(group_by_sf.keys())


#this function adds the tau multiples and gives the elements in a given degree (s, f, w).

def element_by_degree(a_degree):
    elements_in_degree = []
    for element in group_by_sf.get((a_degree[0], a_degree[1]), []):
        if degree(element)[2] == a_degree[2]:
            elements_in_degree.append(element)
        if degree(element)[2] > a_degree[2]:
            difference_degree =   degree(element)[2] - a_degree[2]
            if element["tautorsion"] == 0:
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
#print(element_by_degree((0, 0, -1)))

#defining the index of an element in a given degree.
def class_index(a_degree):
    indexed_elements = []
    for index, element in enumerate(element_by_degree(a_degree)):
        indexed_element = element.copy()
        indexed_element["index"] = index
        indexed_elements.append(indexed_element)
    return indexed_elements


#always remenber that index starts from 0.
def class_name_by_index(a_degree, index):
    for element in class_index(a_degree):
        if element["index"] == index:
            return element["name"]
    return None

#print(class_name_by_index((110, 34, 58), 0))


#then this differential function takes a source degree and a differential degree r and returns the possible differentials.

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


#returns a dictionary for all the elements in a range.
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




#returns a dictionary for all the possible differentials for a range of r.
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



#returns a dictionary for all the possible differentials for a range of r and a range of source degrees.
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

def finding_sources_with_fixed_number_of_differentials(classes, number):
    sources = []
    for element, values in classes.items():
        if len(values) == number:
            sources.append(element)
    return sources

# group the elements by degree and write to a CSV file
# elements = get_classes()
# max_stem = max(element["stem"] for element in elements)
# max_filtration = max(element["Adams filtration"] for element in elements)
# max_weight = max(element["weight"] for element in elements)
# grouped = group_by_degree((max_stem, max_filtration+1, max_weight+1))

# with open("grouped_by_degree.csv", "w", newline="") as f:
#     writer = csv.writer(f)
#     writer.writerow(["degree", "number_of_elements", "elements"])
#     for degree_key, source_elements in sorted(grouped.items()):
#         names = [element["name"] for element in source_elements]
#         writer.writerow([str(degree_key), len(names), json.dumps(names, ensure_ascii=False)])


