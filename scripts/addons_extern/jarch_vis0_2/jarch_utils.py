#convert
def convert(num, to):
    if to == "ft":
        out = num / 3.28084
    elif to == "in":
        out = num / 39.3701
    re = round(out, 5)
    return re

#point rotation
def point_rotation(data, origin, rot):
    from math import sin, cos
    ###Takes in a single tuple (x, y) or a tuple of tuples ((x, y), (x, y)) and rotates them rot radians around origin, returns new (x, y) or ((x, y), (x, y)) values###
    if len(data) == 2 and (isinstance(data[0], float) or isinstance(data[0], int)):
        point = data; new_point = (point[0] - origin[0], point[1] - origin[1]); x = new_point[0]; y = new_point[1]
        new_x = (x * cos(rot)) - (y * sin(rot)); new_y = (x * sin(rot)) - (y * cos(rot))
        out = (new_x + origin[0], new_y + origin[1])
        return (round(out[0], 4), round(out[1], 4))
    else:
        out_list = []
        for point in data:
            new_point = (point[0] - origin[0], point[1] - origin[1]); x = new_point[0]; y = new_point[1]
            new_x = (x * cos(rot)) - (y * sin(rot)); new_y = (x * sin(rot)) - (y * cos(rot))
            out = (new_x + origin[0], new_y + origin[1]); out_list.append((round(out[0], 4), round(out[1], 4)))
        return out_list 