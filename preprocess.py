# coding=utf-8
import os


def text_caption():
    filelist2 = []
    dir2 = "data/health/CUB_200_2011/images"
    filenames = os.listdir(dir2)
    for a in filenames:
        if a.split('.')[0] != '':
            filelist2.append(a.split('.')[0])
    print(filelist2)

    for c in filelist2:
        l3 = []
        ff = os.listdir('data/health/CUB_200_2011/images/' + c)
        for a in ff:
            if a.split('.')[0] != '':
                l3.append(a.split('.')[0])
        print(l3)
        for b in l3:
            f22 = open('data/health/text/' + c + '/' + b + '.txt', 'w')
            # f22.write(b + '\n' + b + '\n' + b + '\n' + b + '\n' + b + '\n' +b + '\n' + b + '\n' + b + '\n' + b + '\n' + b)
            for d in b.split('-'):
                f22.write(d + ' ')


def filenames_pkl():
    i = 5
    filelist2 = []
    dir2 = "data/health/CUB_200_2011/images/Vessel"
    filenames = os.listdir(dir2)
    for a in filenames:
        if a.split('.')[0] != '':
            filelist2.append(a.split('.')[0])
    print(filelist2)

    f = open("list.txt", 'w')
    for c in filelist2:
        f.write('p' + str(i) + '\n' + 'aV' + dir2[32:] + '/' + c + '\n')
        i = i + 1


def classinfo_pkl():
    i = 1
    j = 0
    filelist2 = []
    dir2 = "data/health/CUB_200_2011/images"
    filenames = os.listdir(dir2)
    for a in filenames:
        if a.split('.')[0] != '':
            filelist2.append(a.split('.')[0])
    print(filelist2)

    f = open("list.txt", 'w')
    f2 = open("list2.txt", 'w')
    for c in filelist2:
        if c == 'Muscular' or c == 'Circulatory' or c == 'Dental_Tooth':
            continue
        ff = os.listdir('data/health/CUB_200_2011/images/' + c)
        for a in ff:
            if a.split('.')[0] != '':
                f.write('p' + str(j) + '\n' + 'aV' + c + '/' + a.split('.')[0] + '\n')
                j = j + 1
            # print(l3)
                print(c + '/' + a, 'aI' + str(i))
                f2.write('aI' + str(i) + '\n')
        i = i + 1


def caption_json():
    from collections import defaultdict, OrderedDict
    import json
    from PIL import Image
    import cv2

    minshape = 2000

    i_img = 1
    i_caption = 100000
    i_caption2 = 200000

    images = []
    annotations = []

    dir = "data/health/CUB_200_2011/images"
    dirlist = os.listdir(dir)
    filelist = []
    for a in dirlist:
        if a.split('.')[0] != '':
            filelist.append(a.split('.')[0])
    # print(filelist)

    for a in filelist:
        # Oral_region (190, 190, 3)
        # Liver (190, 190, 3)
        # Gastric (190, 190, 3)
        if a == 'Oral_region' or a == 'Liver' or a == 'Gastric' or a == 'Muscular' or a == 'Circulatory' or a == 'Dental_Tooth':
            continue

        ff = []
        bb = os.listdir('data/health/CUB_200_2011/images/' + a)
        for c in bb:
            if c.split('.')[0] != '':
                ff.append(c)
        # print(ff)
        for d in ff:
            path = 'data/health/CUB_200_2011/images/' + a + '/' + d
            # print(path)

            img = cv2.imread(path)

            dd = {}
            id = {}
            id2 = {}
            dd["file_name"] = a + '/' + d
            dd["id"] = i_img
            # print(img.shape[1])
            dd["height"] = img.shape[0]
            dd["width"] = img.shape[1]
            id["image_id"] = i_img
            id["id"] = i_caption
            caption = ' '.join(d.split('.')[0].split('-'))
            id["caption"] = caption
            i_img = i_img + 1
            i_caption = i_caption + 1

            images.append(dd)
            annotations.append(id)

            id2["image_id"] = i_img
            id2["id"] = i_caption2
            id2["caption"] = caption
            # annotations.append(id2)
            i_caption2 = i_caption2 + 1

            print(a, img.shape)
            if img.shape[0] < minshape:
                minshape = img.shape[0]

    print(minshape)

    test_dict = {
        'info': {
            "description": "This is a medical dataset.",
            "version": "0.1",
            "year": 2020,
            "copyright": "ZHAO WANG"
        },
        'images': images,
        'annotations': annotations
    }

    json_str = json.dumps(test_dict, indent=4)
    with open('data/health/captions.json', 'w') as json_file:
        json_file.write(json_str)


# caption_json()
# text_caption()
# filenames_pkl()
classinfo_pkl()
