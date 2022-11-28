def ControlPoints(n=18):
    '''
    Function to distribute fictious points in the river border and interpolate the levels
    Use n = 18 gives 18 points back. That is a perfect number.
    '''
    ControlPoint = [50.96454391, 13.92163433] #fictious point close to the site
    river_angle = 9.8 #angles with the east in degrees
    river_anglerad = river_angle * 2 * np.pi / 360 #angle in rad
    hypotenuse = 3e-4 #distance between points
    dx = np.cos(river_anglerad) * hypotenuse
    dy = np.sin(river_anglerad) * hypotenuse
    x = np.arange(ControlPoint[1], ControlPoint[1] + (n)*dx , dx)
    y = np.arange(ControlPoint[0], ControlPoint[0] + (n)*dy , dy)
    control_points_list = [[y[i],x[i]] for i,j in enumerate(x)]
    df = pd.DataFrame(control_points_list, columns = ['y', 'x'])
    return df