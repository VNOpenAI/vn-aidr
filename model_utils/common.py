
def area(vs):
    a = 0
    x0, y0 = vs[0]
    for [x1, y1] in vs[1:]:
        dx = x1-x0
        dy = y1-y0
        a += 0.5*(y0*dx - x0*dy)
        x0 = x1
        y0 = y1
    return a

def get_areamax2(contours):
    area_max = 0.0
    area_amax = 0.0
    id_max = 0
    id_amax = 0
    for i, contour in enumerate(contours):
        contour = contour.reshape((-1, 2))
        s = area(contour)
        if s > area_max:
            area_amax = area_max
            area_max = s
            id_amax = id_max
            id_max = i
        elif s > area_amax:
            area_amax = s
            id_amax = i
    return id_max, id_amax