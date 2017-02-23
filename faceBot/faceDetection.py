# coding: utf-8

import cv2
import numpy as np
from PIL import Image
import random


face_cascade = cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_eye.xml')


def detectFaces(img_path, debug=False):
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x,y,w,h) in faces:
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]
        eyes = eye_cascade.detectMultiScale(roi_gray)
        if debug:
            cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
            for (ex,ey,ew,eh) in eyes:
                cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
    if debug:
        cv2.imshow('img',img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return faces


def insertFace(face_path, ref_img, face_rect):
    # Resize rect to accomodate for full head
    face_rect = rectMargin(35, face_rect)

    new_height = face_rect[3]
    new_width = face_rect[2]

    # Resize the face image to fit into the resized rectangle
    img = Image.open(face_path, 'r')
    img_w, img_h = img.size

    resized_height = new_width * img_h / img_w
    resized_width = new_height * img_w / img_h
    # img = img.resize((resized_width, resized_height), Image.ANTIALIAS)
    img.thumbnail((new_width, new_height), Image.ANTIALIAS)

    # Add a 50% chance of horizontal flip
    if random.randint(0, 1):
        img = img.transpose(Image.FLIP_LEFT_RIGHT)

    # Open background image and copy it into a new RGBA image
    if type(ref_img) in (unicode, str):
        ref = Image.open(ref_img, 'r')
    else:
        ref = ref_img
    ref_w, ref_h = ref.size
    background = Image.new('RGBA', ref.size, (255, 255, 255, 255))
    background.paste(ref, (0, 0))
    bg_w, bg_h = background.size

    # Paste the face and save
    background.paste(img, (face_rect[0], face_rect[1]), img)
    return background


def rectMargin(percent, face_rect):
    """As we detect faces but insert a head, we need to widen the face rectangle"""
    width = face_rect[2]
    height = face_rect[3]

    padding_width = int(percent * (width / 100) / 2)
    padding_height = int(percent * (height / 100) / 2)

    return [face_rect[0] - padding_width,
            face_rect[1] - padding_height * 3,
            face_rect[2] + padding_height * 2,
            face_rect[3] + padding_height * 5]
