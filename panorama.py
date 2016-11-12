from pylab import *
from numpy import *
from PIL import Image

import homography, warp
import sift

"""
This is the panorama example from section 3.3.
"""

# set paths to data folder
featname = ['data/Univ'+str(i+1)+'.sift' for i in range(5)] 
imname = ['data/Univ'+str(i+1)+'.jpg' for i in range(5)]

# extract features and match
l = {}
d = {}
for i in range(5): 
    sift.process_image(imname[i],featname[i])
    l[i],d[i] = sift.read_features_from_file(featname[i])


matches = {}
matches_num = {}
cnt = 0
for i in range(5):
    for j in range(5):
        if j > i:
            matches[cnt], matches_num[cnt] = sift.match(d[j],d[i])
            cnt = cnt + 1
for i in range(cnt):
    print i, "matches num : ", matches_num[i]
   

"""
cnt = 0
# visualize the matches (Figure 3-11 in the book)
for i in range(5):
    for j in range(5):
        if j > i:
            im1 = array(Image.open(imname[i]))
            im2 = array(Image.open(imname[j]))
            figure()
            sift.plot_matches(im2,im1,l[j],l[i],matches[cnt],show_below=True)
            cnt = cnt + 1
            show()
"""

# function to convert the matches to hom. points
def convert_points(i,j,cnt):
    ndx = matches[cnt].nonzero()[0]
    fp = homography.make_homog(l[j][ndx,:2].T) 
    ndx2 = [int(matches[cnt][k]) for k in ndx]
    tp = homography.make_homog(l[i][ndx2,:2].T) 
    
    # switch x and y - TODO this should move elsewhere
    fp = vstack([fp[1],fp[0],fp[2]])
    tp = vstack([tp[1],tp[0],tp[2]])
    return fp,tp


# estimate the homographies
model = homography.RansacModel() 

fp = {}
tp = {}
H = {}
inlier = {}
cnt = 0
for i in range(5):
    for j in range(5):
        if j > i :
            if matches_num[cnt] > 50 :
                fp[cnt], tp[cnt] = convert_points(i,j,cnt)
                H[cnt], inlier[cnt] = homography.H_from_ransac(fp[cnt],tp[cnt],model)
            cnt = cnt + 1


for i in range(cnt):
    if matches_num[i] > 50:
        print i,":", float(len(inlier[i]))/matches_num[i]

    
"""
fp,tp = convert_points(1)
H_12 = homography.H_from_ransac(fp,tp,model)[0] #im 1 to 2 

fp,tp = convert_points(0)
H_01 = homography.H_from_ransac(fp,tp,model)[0] #im 0 to 1 

tp,fp = convert_points(2) #NB: reverse order
H_32 = homography.H_from_ransac(fp,tp,model)[0] #im 3 to 2 

tp,fp = convert_points(3) #NB: reverse order
H_43 = homography.H_from_ransac(fp,tp,model)[0] #im 4 to 3    
"""

# warp the images
delta = 2000 # for padding and translation

cnt = 0
for i in range(5):
    for j in range(5):
        if j > i:
            if matches_num[cnt]>50 and (float(len(inlier[cnt]))/matches_num[cnt]) > 0.85:
                im_first = array(Image.open(imname[i]), "uint8")
                im_second = array(Image.open(imname[j]), "uint8")
                im_warping = warp.panorama(H[cnt],im_first,im_second,delta,delta)
                print "cnt:",cnt, "i:",i,"j:",j,"matches_num:",matches_num[cnt]
                figure()
                imshow(array(im_warping, "uint8"))
                axis('off')
                show()
            cnt = cnt + 1	



"""
im1 = array(Image.open(imname[1]), "uint8")
im2 = array(Image.open(imname[2]), "uint8")
im_12 = warp.panorama(H_12,im1,im2,delta,delta)

im1 = array(Image.open(imname[0]), "f")
im_02 = warp.panorama(dot(H_12,H_01),im1,im_12,delta,delta)

im1 = array(Image.open(imname[3]), "f")
im_32 = warp.panorama(H_32,im1,im_02,delta,delta)

im1 = array(Image.open(imname[4]), "f")
im_42 = warp.panorama(dot(H_32,H_43),im1,im_32,delta,2*delta)


figure()
imshow(array(im_42, "uint8"))
axis('off')
show()
"""
