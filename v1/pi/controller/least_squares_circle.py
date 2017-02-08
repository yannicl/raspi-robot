#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
http://www.scipy.org/Cookbook/Least_Squares_Circle
"""

from numpy import *

# Coordinates of the 2D points
x = r_[  9,  35, -13,  10,  23,   0]
y = r_[ 34,  10,   6, -14,  27, -10]

# == METHOD 1 ==
method_1 = 'algebraic'

# coordinates of the barycenter
x_m = mean(x)
y_m = mean(y)

# calculation of the reduced coordinates
u = x - x_m
v = y - y_m

# linear system defining the center in reduced coordinates (uc, vc):
#    Suu * uc +  Suv * vc = (Suuu + Suvv)/2
#    Suv * uc +  Svv * vc = (Suuv + Svvv)/2

Suv  = sum(u*v)
Suu  = sum(u**2)
Svv  = sum(v**2)
Suuv = sum(u**2 * v)
Suvv = sum(u * v**2)
Suuu = sum(u**3)
Svvv = sum(v**3)

# Solving the linear system
A = array([ [ Suu, Suv ], [Suv, Svv]])
B = array([ Suuu + Suvv, Svvv + Suuv ])/2.0
uc, vc = linalg.solve(A, B)

xc_1 = x_m + uc
yc_1 = y_m + vc

# Calculation of all distances from the center (xc_1, yc_1)
Ri_1     = sqrt((x-xc_1)**2 + (y-yc_1)**2)
R_1      = mean(Ri_1)
residu_1 = sum((Ri_1-R_1)**2)

#  == METHOD 2 ==
from scipy      import optimize

method_2 = "leastsq"

def calc_R(c):
    """ calculate the distance of each 2D points from the center c=(xc, yc) """
    return sqrt((x-c[0])**2 + (y-c[1])**2)

def calc_ecart(c):
    """ calculate the algebraic distance between the 2D points and the mean circle centered at c=(xc, yc) """
    Ri = calc_R(c)
    return Ri - Ri.mean()

center_estimate = x_m, y_m
center_2, ier = optimize.leastsq(calc_ecart, center_estimate)

xc_2, yc_2 = center_2
Ri_2       = calc_R(center_2)
R_2        = Ri_2.mean()
residu_2   = sum((Ri_2 - R_2)**2)

# == METHOD 3 ==
from scipy      import  odr

method_3 = "odr"

def calc_f(beta, x):
    """ implicit function of the circle """
    xc, yc, r = beta
    return (x[0]-xc)**2 + (x[1]-yc)**2 -r**2

def calc_estimate(data):
    """ Return a first estimation on the parameter from the data  """
    xc0, yc0 = data.x.mean(axis=1)
    r0 = sqrt((data.x[0]-xc0)**2 +(data.x[1] -yc0)**2).mean()
    return xc0, yc0, r0

# for implicit function :
#       data.x contains both coordinates of the points
#       data.y is the dimensionality of the response
lsc_data  = odr.Data(row_stack([x, y]), y=1)
lsc_model = odr.Model(calc_f, implicit=True, estimate=calc_estimate)
lsc_odr   = odr.ODR(lsc_data, lsc_model)
lsc_out   = lsc_odr.run()

xc_3, yc_3, R_3 = lsc_out.beta
Ri_3 = calc_R([xc_3, yc_3])
residu_3 = sum((Ri_3 - R_3)**2)

# Summary
fmt = '%-15s %10.5f %10.5f %10.5f %10.6f %10.6f'
print '\n%-15s %10s %10s %10s %10s %10s' % tuple('METHOD Xc Yc Rc std(Ri) residu'.split())
print '-'*(15 +5*(10+1))
print  fmt % (method_1, xc_1, yc_1, R_1, Ri_1.std(), residu_1)
print  fmt % (method_2, xc_2, yc_2, R_2, Ri_2.std(), residu_2)
print  fmt % (method_3, xc_3, yc_3, R_3, Ri_3.std(), residu_3)

# plotting functions

from matplotlib import pyplot as p, cm

f = p.figure()
p.plot(x, y, 'ro', label='data', ms=9, mec='b', mew=1)

theta_fit = linspace(-pi, pi, 180)

x_fit1 = xc_1 + R_1*cos(theta_fit)
y_fit1 = yc_1 + R_1*sin(theta_fit)
p.plot(x_fit1, y_fit1, 'b-' , label=method_1, lw=2)

x_fit2 = xc_2 + R_2*cos(theta_fit)
y_fit2 = yc_2 + R_2*sin(theta_fit)
p.plot(x_fit2, y_fit2, 'k--', label=method_2, lw=2)

x_fit3 = xc_3 + R_3*cos(theta_fit)
y_fit3 = yc_3 + R_3*sin(theta_fit)
p.plot(x_fit3, y_fit3, 'r-.', label=method_3, lw=2)

p.plot([xc_1], [yc_1], 'bD', mec='y', mew=1)
p.plot([xc_2], [yc_2], 'gD', mec='r', mew=1)
p.plot([xc_3], [yc_3], 'kD', mec='w', mew=1)

# draw
p.axis('equal')
p.xlabel('x')
p.ylabel('y')
p.legend(loc='best',labelspacing=0.1)

# plot the residu fields
nb_pts = 100

p.draw()
xmin, xmax = p.xlim()
ymin, ymax = p.ylim()

vmin = min(xmin, ymin)
vmax = max(xmax, ymax)

xg, yg = ogrid[vmin:vmax:nb_pts*1j, vmin:vmax:nb_pts*1j]
xg = xg[..., newaxis]
yg = yg[..., newaxis]

Rig    = sqrt( (xg - x)**2 + (yg - y)**2 )
Rig_m  = Rig.mean(axis=2)[..., newaxis]
residu = sum( (Rig-Rig_m)**2 ,axis=2)

lvl = exp(linspace(log(residu.min()), log(residu.max()), 15))

p.contourf(xg.flat, yg.flat, residu.T, lvl, alpha=0.75, cmap=cm.YlGnBu_r)
cbar = p.colorbar(format='%.1f')
cbar.set_label('Residu')
p.xlim(xmin=vmin, xmax=vmax)
p.ylim(ymin=vmin, ymax=vmax)

p.grid()
p.title('Leasts Squares Circle')
p.show()
# vim: set et sts=4 sw=4:
