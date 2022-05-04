# -*- coding: utf-8 -*-
"""AI_project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/gist/rcf4765/1850c3151edcf6d87ee2852b2142a769/ai_project.ipynb

#####Note: Please keep all the image files inside the folder as the code before running and try to run it in colab

###Importing Libraries
"""

import cv2
# from google.colab.patches import cv2_imshow
import random
import math as m
import time
import glob
import numpy as np

"""###Function to find difference between two colors"""


def getcolordiff(r1, g1, b1, r2, g2, b2):
    red = float(r1) - float(r2)
    green = float(g1) - float(g2)
    blue = float(b1) - float(b2)
    return m.sqrt(red ** 2 + green ** 2 + blue ** 2)


"""###Function for applying k-means segmentation to an image"""


def kMeansSegmentation(img, k=10):
    # First we will take 10 random pixels from image and store it in a list
    initial_seed = []

    while len(initial_seed) < 10:
        x = random.randint(0, img.shape[1] - 1)
        y = random.randint(0, img.shape[0] - 1)
        # Check if x,y is already present in list, if not add it to the list
        if [x, y, img[y][x][2], img[y][x][1], img[y][x][0]] in initial_seed:
            continue

        initial_seed.append([x, y, img[y][x][2], img[y][x][1], img[y][x][0]])

        # List to store lists of k clusters
    required_clusters = []
    # set convergence as false initially
    convergence = False

    while (convergence == False):
        # Start with fresh clusters list
        required_clusters = []

        # Append it with empty lists so we can easily access it through numbers
        for i in range(k):
            required_clusters.append([])

            # Check for every pixel
        # Which pixel from random pixels list has the least color diff
        # with the selected pixel
        for r in range(img.shape[0]):
            for c in range(img.shape[1]):
                # This variable gives the index of random pixel which has smallest color diff
                index = 0
                # This variable stores curr min distance, initially set it to high value
                minimumdiff = 10000000000

                # Looping through all random pixels selected
                for i in range(k):
                    # rgb values for current pixel from original image
                    pixel_r = img[r][c][2]
                    pixel_g = img[r][c][1]
                    pixel_b = img[r][c][0]

                    # rgb values for the current selected random pixel
                    current_r = initial_seed[i][2]
                    current_g = initial_seed[i][3]
                    current_b = initial_seed[i][4]

                    # current difference between pixel colors
                    current_diff = getcolordiff(pixel_r, pixel_g, pixel_b, current_r, current_g, current_b)

                    # if current difference is smaller than minimum distance
                    # update the minimum distance and the index of random pixel
                    if current_diff < minimumdiff:
                        index = i
                        minimumdiff = current_diff

                        # Add current image pixel to the cluster
                # formed by the random pixel which has the shortest
                # color difference with the current image pixel
                required_clusters[index].append([c, r, img[r][c][2], img[r][c][1], img[r][c][0]])

                # Loop through the clusters obtained
        # to find the cluster center (average of all pixels present in each cluster)
        for i in range(k):
            current_cluster = required_clusters[i]

            # Finding mean color value of all pixels in a cluster
            mean_r = 0
            mean_g = 0
            mean_b = 0

            for j in range(len(current_cluster)):
                mean_r += current_cluster[j][2]
                mean_g += current_cluster[j][3]
                mean_b += current_cluster[j][4]

            mean_r = int(mean_r / len(current_cluster))
            mean_g = int(mean_g / len(current_cluster))
            mean_b = int(mean_b / len(current_cluster))

            # Check if cluster mean has changed, if not change it, otherwise we found our cluster combination
            if mean_r != initial_seed[i][2] or mean_g != initial_seed[i][3] or mean_b != initial_seed[i][4]:
                initial_seed[i][2] = mean_r
                initial_seed[i][3] = mean_g
                initial_seed[i][4] = mean_b
            else:
                convergence = True

    ans = img.copy()

    # Change rgb values for all pixels present in a cluster to that cluster's mean value
    for x in range(k):
        mean = initial_seed[x]
        curr = required_clusters[x]

        for point in curr:
            ans[point[1]][point[0]][2] = mean[2]
            ans[point[1]][point[0]][1] = mean[3]
            ans[point[1]][point[0]][0] = mean[4]

    return ans


"""###Function for SLIC"""


def getSLIC(img, block_size=50):
    # getting centre of blocks
    initialized_centroids = []
    half = block_size / 2

    for r in range(img.shape[0]):
        for c in range(img.shape[1]):
            # Check if current pixel is a centre
            if r != 0 and c != 0 and ((r - half) % block_size) == 0 and ((c - half) % block_size) == 0:
                initialized_centroids.append([r, c])

        # moving centre position after checking color grad magnitudes
    for i in range(len(initialized_centroids)):
        # Set min grad to high num initially
        min_grad = 10000000000
        found_pixel = [0, 0]
        y = initialized_centroids[i][0]
        x = initialized_centroids[i][1]

        # Checking 3 x 3 area around the centre
        for j in range(-1, 1):
            for k in range(-1, 1):
                curr_grad = m.sqrt(float(int(img[y + j + 1][x + k + 1][0]) - int(img[y + j][x + k][0])) ** 2 +
                                   float(int(img[y + j + 1][x + k + 1][1]) - int(img[y + j][x + k][1])) ** 2 +
                                   float(int(img[y + j + 1][x + k + 1][2]) - int(img[y + j][x + k][2])) ** 2)
                # If the magnitude is smaller then min grad we have a new best point
                if curr_grad < min_grad:
                    min_grad = curr_grad
                    found_pixel = [y + j, x + k]

        initialized_centroids[i] = found_pixel

    return getkmeansonSLIC(img, initialized_centroids)


"""###Definition to find Euclidean distance between two points"""


def getdist(x1, y1, r1, g1, b1, x2, y2, r2, g2, b2):
    red = (float(r1) - float(r2))
    green = (float(g1) - float(g2))
    blue = (float(b1) - float(b2))
    x = (float(x1) - float(x2))
    y = (float(y1) - float(y2))
    return m.sqrt(red ** 2 + green ** 2 + blue ** 2 + (x ** 2) / 2 + (y ** 2) / 2)


"""###Definition to find k-means segmentation on the centroids obtained from SLIC"""


def getkmeansonSLIC(img, points):
    convergence = False
    initial_seed = []

    # Push the centroids into initial seed
    # Since we have to use 5D we push [x,y,R,G,B]
    for i in range(len(points)):
        x = points[i][1]
        y = points[i][0]
        initial_seed.append([x, y, img[y][x][2], img[y][x][1], img[y][x][0]])

    # This is simply applying k-means segmentation
    # to an already defined set of intial seed instead
    # of just taking random centers
    # Setting max_itr = 3
    curr_itr = 0
    max_itr = 3

    while (convergence == False and curr_itr < max_itr):
        curr_itr += 1

        # clearing clusters
        required_clusters = []
        for i in range(len(points)):
            required_clusters.append([])

            # Check for every pixel
        # Which pixel from random pixels list has the least color diff
        # with the selected pixel
        for r in range(img.shape[0]):
            for c in range(img.shape[1]):
                # This variable gives the index of random pixel which has smallest color diff
                index = 0
                # This variable stores curr min distance, initially set it to high value
                minimumdiff = 10000000000

                # Looping through all random pixels selected
                for i in range(len(points)):
                    curr = initial_seed[i]

                    # rgb values for the current selected random pixel
                    current_r = curr[2]
                    current_g = curr[3]
                    current_b = curr[4]

                    # rgb values for current pixel from original image
                    pixel_r = img[r][c][2]
                    pixel_g = img[r][c][1]
                    pixel_b = img[r][c][0]

                    # current difference between pixel colors
                    if (m.sqrt((float(curr[0]) - float(c)) ** 2 + (float(curr[1]) - float(r)) ** 2) > 100):
                        continue
                    else:
                        current_diff = getdist(curr[0], curr[1], pixel_r, pixel_g, pixel_b, c, r, current_r, current_g,
                                               current_b)
                        # if current difference is smaller than minimum distance
                        # update the minimum distance and the index of random pixel
                        if current_diff < minimumdiff:
                            index = i
                            minimumdiff = current_diff

                            # Add current image pixel to the cluster
                # formed by the random pixel which has the shortest
                # color difference with the current image pixel
                required_clusters[index].append([c, r, img[r][c][2], img[r][c][1], img[r][c][0]])

        for i in range(len(points)):
            current_cluster = required_clusters[i]

            # Finding mean color value of all pixels in a cluster
            mean_r = 0
            mean_g = 0
            mean_b = 0

            for j in range(len(current_cluster)):
                mean_r += current_cluster[j][2]
                mean_g += current_cluster[j][3]
                mean_b += current_cluster[j][4]

            mean_r = int(mean_r / len(current_cluster))
            mean_g = int(mean_g / len(current_cluster))
            mean_b = int(mean_b / len(current_cluster))

            # Check if cluster mean has changed, if not change it, otherwise we found our cluster combination
            if mean_r != initial_seed[i][2] or mean_g != initial_seed[i][3] or mean_b != initial_seed[i][4]:
                initial_seed[i][2] = mean_r
                initial_seed[i][3] = mean_g
                initial_seed[i][4] = mean_b
            else:
                convergence = True

        # segmented image to return
    ans = img.copy()

    # change colors of all pixels in a cluster to mean's color
    for x in range(len(points)):
        curr = required_clusters[x]

        for point in curr:
            ans[point[1]][point[0]][2] = initial_seed[x][2]
            ans[point[1]][point[0]][1] = initial_seed[x][3]
            ans[point[1]][point[0]][0] = initial_seed[x][4]

    return ans


"""###Definition to add black border"""


def getborders(img):
    ans = img.copy()

    for r in range(img.shape[0] - 1):
        for c in range(img.shape[1] - 1):
            # If at edge, continue
            if r == 0 or c == 0:
                continue
            else:
                # Check if pixel's color == neighbour's color
                # if not change the color of curr pixel to black
                for i in range(-1, 1):
                    for j in range(-1, 1):
                        if (img[r][c][0] == img[r + i][c + j][0]) and (img[r][c][1] == img[r + i][c + j][1]) and (
                                img[r][c][2] == img[r + i][c + j][2]):
                            continue
                        else:
                            ans[r][c] = [0, 0, 0]

    return ans


"""###Performing k-means"""

init_img = cv2.imread("wmu.png")
cv2.imshow("image before kmeans", init_img)
# cv2_imshow(init_img)
cv2.waitKey(0)

img_after_kmeans = kMeansSegmentation(init_img, 10)
cv2.imshow("image after kmeans", img_after_kmeans)
# cv2_imshow(img_after_kmeans)
cv2.waitKey(0)

"""###Performing SLIC"""

init_img = cv2.imread("wmu_slic.png")
cv2.imshow("image before slice", init_img)
# cv2_imshow(init_img)
cv2.waitKey(0)

img_after_slic = getSLIC(init_img, 50)
cv2.imshow("image after slice", img_after_slic)
# cv2_imshow(img_after_slic)
cv2.waitKey(0)

slic_with_border = getborders(img_after_slic)
cv2.imshow("image after slice", img_after_slic)
# cv2_imshow(slic_with_border)
cv2.waitKey(0)

"""###Pixel Classification"""


def kmeancluster(set_of_points, k=10):
    # Same program as earlier
    # only difference is instead of picking completely random points
    # we pick random points from set_of_points
    initial_seed = []

    while len(initial_seed) < k:
        x = random.randint(0, len(set_of_points) - 1)

        if [set_of_points[x][0], set_of_points[x][1], set_of_points[x][2]] in initial_seed:
            continue
        else:
            initial_seed.append([set_of_points[x][0], set_of_points[x][1], set_of_points[x][2]])

    required_clusters = []
    convergence = False

    while (convergence == False):
        required_clusters = []

        for i in range(k):
            required_clusters.append([])

        for i in range(len(set_of_points)):
            mindist = 10000000000
            index = 0

            for j in range(len(required_clusters)):
                cent_r = initial_seed[j][0]
                cent_g = initial_seed[j][1]
                cent_b = initial_seed[j][2]

                pix_r = set_of_points[i][0]
                pix_g = set_of_points[i][1]
                pix_b = set_of_points[i][2]

                currdist = getcolordiff(cent_r, cent_g, cent_b, pix_r, pix_g, pix_b)

                if currdist < mindist:
                    mindist = currdist
                    index = j

            required_clusters[index].append([set_of_points[i][0], set_of_points[i][1], set_of_points[i][2]])

        for i in range(k):
            curr = required_clusters[i]

            if len(curr) == 0:
                continue
            mean_r = 0
            mean_g = 0
            mean_b = 0

            for j in range(len(curr)):
                mean_r += curr[j][0]
                mean_g += curr[j][1]
                mean_b += curr[j][2]

            mean_r = int(mean_r / len(curr))
            mean_g = int(mean_g / len(curr))
            mean_b = int(mean_b / len(curr))

            if mean_r != initial_seed[i][0] or mean_g != initial_seed[i][1] or mean_b != initial_seed[i][2]:
                initial_seed[i][0] = mean_r
                initial_seed[i][1] = mean_g
                initial_seed[i][2] = mean_b
            else:
                convergence = True

    print("Final centers: " + str(initial_seed))

    return initial_seed


def sky():
    img_with_sky = cv2.imread("sky_train.jpg")
    img_with_no_sky = cv2.imread("no_sky_train.jpg")
    cv2.imshow("with sky", img_with_sky)
    # cv2_imshow(img_with_sky)
    cv2.waitKey(0)
    cv2.imshow("no sky", img_with_no_sky)
    # cv2_imshow(img_with_no_sky)
    cv2.waitKey(0)
    # set of points which symbolize sky and no sky
    sky = []
    no_sky = []
    color = img_with_no_sky[0][0]

    for i in range(img_with_no_sky.shape[0]):
        for j in range(img_with_no_sky.shape[1]):
            # check if pixel color of no sky matches mask color, if yes
            # append that point from image with sky into sky set
            if img_with_no_sky[i][j][0] == color[0] and img_with_no_sky[i][j][1] == color[1] and img_with_no_sky[i][j][
                2] == color[2]:
                sky.append([img_with_sky[i][j][2], img_with_sky[i][j][1], img_with_sky[i][j][0]])
            else:
                no_sky.append([img_with_no_sky[i][j][2], img_with_no_sky[i][j][1], img_with_no_sky[i][j][0]])

    print("Sky Clustered Centers:")
    sky_clustered = kmeancluster(sky, 10)
    print(sky_clustered)

    print("No Sky Clustered Centers:")
    no_sky_clustered = kmeancluster(no_sky, 10)
    print(no_sky_clustered)

    # creating a list of test files
    print("All test files:")
    test_imgs = glob.glob("*test*.jpg")
    print(test_imgs)

    for fname in test_imgs:
        curr_img = cv2.imread(fname)

        cv2.imshow("image", curr_img)
        # cv2_imshow(curr_img)
        cv2.waitKey(0)

        ans = curr_img.copy()

        for i in range(curr_img.shape[0]):
            for j in range(curr_img.shape[1]):

                # curr rgb values of pixel
                blue = curr_img[i][j][0]
                green = curr_img[i][j][1]
                red = curr_img[i][j][2]

                mindist = 100000000000

                # Find closest distance from non sky clustered center
                for c in range(len(no_sky_clustered)):
                    # curr distance
                    dist_non_sky = getcolordiff(red, green, blue, no_sky_clustered[c][0], no_sky_clustered[c][1],
                                                no_sky_clustered[c][2])

                    # check if curr distance is smaller, if yes update
                    if dist_non_sky < mindist:
                        mindist = dist_non_sky

                # Find closest distance from sky clustered center
                for c in range(len(sky_clustered)):
                    # curr distance
                    dist_sky = getcolordiff(red, green, blue, sky_clustered[c][0], sky_clustered[c][1],
                                            sky_clustered[c][2])

                    # Check if new distance is smaller
                    if dist_sky < mindist:
                        ans[i][j] = [234, 62, 146]
                        break

        # cv2_imshow(ans)
        cv2.imshow("ans image", ans)
        cv2.waitKey(0)


sky()