from pylab import *
from numpy import *
from PIL import Image
import sift

imname = 'Univ1.jpg'
im1 = array(Image.open(imname).convert('L'))
sift.process_image(imname,'Univ1.sift')
l1,d1 = sift.read_features_from_file('Univ1.sift')
figure()
gray()
sift.plot_features(im1,l1,circle=True)
show()
