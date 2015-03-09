#!/usr/bin/env python

from math import sin, cos, asin, atan2, sqrt, degrees, radians

from collections import namedtuple

GeoPoint = namedtuple('GeoPoint',['lat','lon'])

earth_radius = 6371000.0

# from http://www.movable-type.co.uk/scripts/latlong.html
# from a to b
def distance_and_direction(a, b):
    if a == b:
        return 0, 0

    lat_s = radians(a[0])
    lon_s = radians(a[1])
    lat_f = radians(b[0])
    lon_f = radians(b[1])
    lat_d = lat_f - lat_s
    lon_d = lon_f - lon_s

    R = earth_radius

    t1 = sin(lat_d/2)
    t2 = sin(lon_d/2)
    distance = R*2*asin(sqrt(t1*t1 + cos(lat_s)*cos(lat_f)*t2*t2))

    y = sin(lon_d)*cos(lat_f)
    x = cos(lat_s)*sin(lat_f) - sin(lat_s)*cos(lat_f)*cos(lon_d)
    heading = degrees(atan2(y, x))

    return distance, heading

def point_from_distance_and_heading(a, distance, heading):
    lat_s = radians(a[0])
    lon_s = radians(a[1])
    t = radians(heading)
    d = distance

    R = earth_radius

    lat_f = asin(sin(lat_s)*cos(d/R) + cos(lat_s)*sin(d/R)*cos(t))
    lon_f = lon_s + atan2(sin(t)*sin(d/R)*cos(lat_s), cos(d/R) - sin(lat_s)*sin(lat_f))

    return (degrees(lat_f), degrees(lon_f))

def point_from_xy(a, x, y):
    # this only works for small x,y distances.
    d = sqrt(x**2 + y**2)
    h = degrees(atan2(x,y)) # +y is north
    return point_from_distance_and_heading(a, d, h)

def distance_in_xy(a, b):
    distance, heading = distance_and_direction(a, b)
    t = radians(heading)
    x = distance*sin(t)
    y = distance*cos(t)
    return x,y

if __name__ == '__main__':
    a = (-33.80784, 151.176614)
    b = (-23.5237,148.157959)
    
    dist,heading = distance_and_direction(a,b)
    c = point_from_distance_and_heading(a, dist, heading)
    
    d = (-33.808107,151.183845)
    
    print('distance = %d meters, heading = %0.2f degrees' % (dist, heading))
    print('c = %s' % (c,))

    dist, heading = distance_and_direction(a, d)
    print('from %s to %s is %d meters, heading %0.2f degrees, ### %s' % (a, d, dist, heading, point_from_distance_and_heading(a, dist, heading)))
    dist, heading = distance_and_direction(d, a)    
    print('from %s to %s is %d meters, heading %0.2f degrees, ### %s' % (d, a, dist, heading, point_from_distance_and_heading(d, dist, heading)))


    print('x=%f y=%f from %s is %s' % (1000, 100, a, point_from_xy(a, 1000, 100)))
    print('x=%f y=%f from %s is %s' % (200, 200, a, point_from_xy(a, 200, 200)))
    e = point_from_xy(a, 200, -200)
    dist,heading = distance_and_direction(a, e)
    print('x=%f y=%f from %s is %s' % (200, 200, a, e))
    print('%s to %s is %d at %0.2f degrees.' % (a, e, dist, heading))

    print(distance_in_xy(a, e))
    


