def toponym_to_spn(toponym):
    bounds = tuple(map(float, toponym['boundedBy']['Envelope']['lowerCorner'].split())), tuple(
        map(float, toponym['boundedBy']['Envelope']['upperCorner'].split())
    )
    return (abs(bounds[0][0] - bounds[1][0]), abs(bounds[0][1] - bounds[1][1]))


def toponyms_to_spn(*bounds):
    min_lon = min_lat = float('inf')
    max_lon = max_lat = -float('inf')

    for bound_set in bounds:
        if isinstance(bound_set, dict):
            bound_set = list(bound_set.values())
            lower = tuple(map(float, bound_set[0].split()))
            upper = tuple(map(float, bound_set[1].split()))
        elif isinstance(bound_set, (tuple, list)):
            lower = tuple(map(float, bound_set[0]))
            upper = tuple(map(float, bound_set[1]))
        elif isinstance(bound_set, str):
            if ',' in bound_set:
                splitted = bound_set.split(',')
                if len(splitted) == 2:
                    lower = upper = tuple(map(float, splitted))
                else:
                    lower = tuple(map(float, bound_set.split(',')[:len(splitted) // 2]))
                    upper = tuple(map(float, bound_set.split(',')[len(splitted) // 2:]))
            else:
                splitted = bound_set.split()
                lower = tuple(map(float, bound_set.split()[0]))
                upper = tuple(map(float, bound_set.split()[1]))
        else:
            raise NotImplementedError(type(bound_set))
        min_lon = min(min_lon, lower[0], upper[0])
        min_lat = min(min_lat, lower[1], upper[1])
        max_lon = max(max_lon, lower[0], upper[0])
        max_lat = max(max_lat, lower[1], upper[1])

    spn_x = abs(max_lon - min_lon)
    spn_y = abs(max_lat - min_lat)

    return spn_x, spn_y
