from pylab import *
from numpy import *
from PIL import Image
import scipy.misc

import homography, warp, sift

matches = {}
matches_num = {}
l = {}
d = {}
def convert_points(i,j,cnt):
    ndx = matches[cnt].nonzero()[0]
    fp = homography.make_homog(l[j][ndx,:2].T)
    ndx2 = [int(matches[cnt][k]) for k in ndx]
    tp = homography.make_homog(l[i][ndx2,:2].T)

    fp = vstack([fp[1],fp[0],fp[2]])
    tp = vstack([tp[1],tp[0],tp[2]])
    return fp, tp

def make_panorama(num):
    featname = ['data/Univ'+str(i+1)+'.sift' for i in range(num)]
    imname = ['data/Univ'+str(i+1)+'.jpg' for i in range(num)]

#    l = {}
#    d = {}

    # extract features and match
    for i in range(num) :
        sift.process_image(imname[i],featname[i])
        l[i],d[i] = sift.read_features_from_file(featname[i])

#    matches = {}
#    matches_num = {}
    fp = {}
    tp = {}
    H = {}
    inlier = {}
    cnt = 0
    model = homography.RansacModel()
    delta = 2000
    stop = 0
    for i in range(num) :
        if stop == 1:
            break
        for j in range(num) :
            if j > i :
                print "i:",i,"j:",j
                matches[cnt],matches_num[cnt] = sift.match(d[j],d[i])
                if matches_num[cnt] > 50 :
                    fp[cnt], tp[cnt] = convert_points(i,j,cnt)
                    H[cnt], inlier[cnt] = homography.H_from_ransac(fp[cnt],tp[cnt],model)
                
                    if (float(len(inlier[cnt])) / matches_num[cnt]) > 0.85 :
                        im_first = array(Image.open(imname[i]), "uint8")
                        im_second = array(Image.open(imname[j]), "uint8")
                        im_warping = warp.panorama(H[cnt],im_first,im_second,delta,delta)
                #delete i,j image and im_warping image save and re-numbering image file name
                        nn = 1
                        print "delete i",i,"and j",j,"image"
                        scipy.misc.imsave('data/Univ'+str(nn)+'.jpg',im_warping)
#nn = 1
                        for k in range(num) :
                            if j != k and i != k :
                                im = array(Image.open(imname[k]))
                                Image.fromarray(im).save('data/Univ'+str(nn)+'.jpg')
                                nn = nn + 1
                        scipy.misc.imsave('data/Univ'+str(nn)+'.jpg',im_warping)
                        stop = 1
                        break
                    else :
                        cnt = cnt+1


image_n = 5
while image_n > 1:
    make_panorama(image_n)
    image_n = image_n -1
    print "we make ",image_n,"images"


print "panorama stiching done..."
