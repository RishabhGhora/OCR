# Load the necessary modules 
import numpy as np

def fillIsland(arr, i, j):
    """
    Uses a depth first search on a boolean matrix 
    to fill in an island of Trues with False 
    and returns the bounds 
    arr: a 2d boolean numpy array
    i: the y coordinate for a point that is true
    j: the x coordinate for a point that is true
    minx, maxx, miny, maxy: returns the bounds of the island
    """
    q = [(i,j)]
    minx = i
    miny = j
    maxx = i
    maxy = j
    while len(q) > 0:
        i, j = q.pop()
        if i >= 0 and i < arr.shape[0] and j >= 0 and j < arr.shape[1] and arr[i,j]:
            arr[i,j] = False
            minx = min(minx, i)
            maxx = max(maxx, i)
            miny = min(miny, j)
            maxy = max(maxy, j)
            for a in range(3):
                for b in range(3):
                    if a != 1 or b != 1:
                        q.append((i+a-1,j+b-1))
    return minx, maxx, miny, maxy

def findIslands(arr):
    """
    Finds all the islands in a boolean matrix
    arr: a boolean matrix
    res: returns a list of bounds for the islands, 
    along with a coordinate that is contained in them
    so that they can be found again
    """
    res = []
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            if arr[i,j]:
                res.append((i,j,fillIsland(arr,i,j)))
    return res

def overlap(a,b,power):
    """
    Finds the overlap between the y values of 
    two islands as a fraction and puts it to the 
    power of power
    a: the first island's bounds
    b: the second island's bounds 
    power: the power to put the result to
    returns the overlap to the provided power
    """
    if a[0] > b[1] or a[1] < b[0]:
        return 0
    return ((min(a[1],b[1])-max(a[0],b[0]))/(max(a[1],b[1])-min(a[0],b[0])))**power

def isolateText(img):
    """
    Converts image to islands
    img: the image inputed by the user
    combined: the island filtered image
    """
    origislands = []
    C = 180
    F2 = np.logical_and(np.logical_and(img[:,:,0] > C, img[:,:,1] > C), img[:,:,2] > C).reshape([img.shape[0],img.shape[1]])
    combined = F2 * False
    origislands = findIslands(np.copy(F2))
    islands = [i for i in origislands if i[2][3]-i[2][2] > 0 and i[2][1]-i[2][0] > 10]
    wb = np.median([i[2][3]-i[2][2] for i in islands])
    hb = np.median([i[2][1]-i[2][0] for i in islands])
    for isl in islands:
        bounds = isl[2]
        overlaps = [overlap(i[2],bounds,1) for i in islands]
        S = sum(overlaps)
        if sum([overlap(i[2],bounds,2) for i in islands]) > 3 and sum(sorted(overlaps)[-4:]) > 3:
            im = np.zeros([img.shape[0],img.shape[1]])
            t = np.copy(F2)
            fillIsland(t,isl[0],isl[1])
            im[np.logical_and(F2,np.logical_not(t))] = 255
            combined = np.logical_or(combined,im)
            im = im[bounds[0]-5:bounds[1]+5,bounds[2]-5:bounds[3]+5]

    for isl in origislands:
        i = isl[2]
        if i[3]-i[2] < wb and i[1] - i[0] < hb/3 and i[1] and max(i[3]-i[2],i[1]-i[0]) > wb/3:
            for j in islands:
                q = j[2]
                #add the dots to i's
                if q[0] > i[1] and (abs(q[3]-i[3])+abs(q[2]-i[2])) * (q[0]-i[1])*10/hb < 5:
                    im = np.zeros([img.shape[0],img.shape[1]])
                    t = np.copy(F2)
                    fillIsland(t,isl[0],isl[1])
                    im[np.logical_and(F2,np.logical_not(t))] = 255
                    combined = np.logical_or(combined,im)
                    break
                #and the apostrophes
                if i[1] > q[0] and (i[1]-q[0])/hb < 0.2 and q[2] > i[3] and q[2]-i[3] < wb*3:
                    im = np.zeros([img.shape[0],img.shape[1]])
                    t = np.copy(F2)
                    fillIsland(t,isl[0],isl[1])
                    im[np.logical_and(F2,np.logical_not(t))] = 255
                    combined = np.logical_or(combined,im)
                    break
    combined = np.logical_not(combined)
    return combined