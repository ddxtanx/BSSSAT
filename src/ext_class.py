import csv

classes =[]
with open('Adams-motivic-E2.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        classes.append({"name": row['name'], "stem": int(row['stem']), "Adams filtration": int(row['Adams filtration']), "weight": int(row['weight']), "tautorsion": int(row['tautorsion'])})


def degree(element):
    return (element["stem"], element["Adams filtration"], element["weight"])

def add_degree(degree1, degree2):
    return (int(degree1[0]) + int(degree2[0]), int(degree1[1]) + int(degree2[1]), int(degree1[2]) + int(degree2[2])) 

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
        if int(degree(element)[2]) == int(a_degree[2]):
            elements_in_degree.append(element)
        if int(degree(element)[2]) > int(a_degree[2]):
            difference_degree =   int(degree(element)[2]) - int(a_degree[2])
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

for stem in range(0,12):
    for adams_filtration in range(0,13):
        for weight in range(0,12):
            source_degree = (stem, adams_filtration, weight)
            for r in range(1,3):
                for element in possible_differentials_by_r(source_degree,r):
                    print(f"Possible d_{r} differentials for {element}:")
                for diff in possible_differentials_by_r(source_degree,r):
                    print(f"{diff}")




    