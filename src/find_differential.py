import csv

classes =[]
with open('Adams-motivic-E2.csv', newline='') as csvfile:
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
    for s in range(0, int(bounds[0]) + 1):
        for f in range(0, int(bounds[1]) + 1):
            for w in range(-int(bounds[2]), int(bounds[2]) + 1):
                a_degree = (s, f, w)
                elements = element_by_degree(a_degree)
                if elements:
                    grouped[a_degree] = elements
    return grouped

# test
for element in group_by_degree((10, 10, 10)):
    print(f"Degree: {element}, Elements: {[e['name'] for e in group_by_degree((10, 10, 10))[element]]}")



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
# differentials = possible_differentials_in_a_range((5,10,10), 1)
# for element, diffs in differentials.items():
#    print(f"Possible d_1 differentials for {element}:")
#    for diff in diffs:
#       print(diff)