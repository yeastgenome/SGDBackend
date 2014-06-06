from math import sqrt, pi, acos

__author__ = 'kpaskov'

def calc_venn_measurements(A, B, C):
    e = .01
    r = sqrt(1.0*A/pi)
    s = sqrt(1.0*B/pi)
    if A == C or B == C:
        return r, s, abs(r-s)-1
    elif C == 0:
        return r, s, r+s+1
    else:
        x = binary_search(C, lambda x: area_of_intersection(r, s, x), abs(r-s), r+s, e)
        return r, s, x

    
def binary_search(value, f, lower, upper, e, max_iter=None):
    midpoint = lower + 1.0*(upper-lower)/2
    value_at_midpoint = f(midpoint)

    if max_iter is not None:
        max_iter = max_iter - 1
        
    if abs(value_at_midpoint - value) < e or (max_iter is not None and max_iter == 0):
        return midpoint
    elif value > value_at_midpoint:
        return binary_search(value, f, lower, midpoint, e, max_iter)
    else:
        return binary_search(value, f, midpoint, upper, e, max_iter)
    
def area_of_intersection(r, s, x):
    if x <= abs(r-s):
        return min(pi*pow(r, 2), pi*pow(s, 2))
    elif x > r+s:
        return 0
    else:
        return pow(r,2)*acos(1.0*(pow(x,2) + pow(r,2) - pow(s,2))/(2*x*r)) + pow(s,2)*acos(1.0*(pow(x,2) + pow(s,2) - pow(r,2))/(2*x*s)) - .5*sqrt((-x+r+s)*(x+r-s)*(x-r+s)*(x+r+s))

if __name__ == "__main__":
    e = .001
    assert area_of_intersection(5, 2, 3) - 12.5663706144 < e
    assert area_of_intersection(5, 2, 4) - 9.69915636604 < e
    assert area_of_intersection(5, 2, 5) - 5.7476906924 < e
    assert area_of_intersection(5, 2, 6) - 2.15417291012 < e
    assert area_of_intersection(5, 2, 7) - 0 < e
    
    assert area_of_intersection(2, 5, 6) - 2.15417291012 < e
    
    print calc_venn_measurements(pi*25, pi*4, 2)

