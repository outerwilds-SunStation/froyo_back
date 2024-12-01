import base64
import json
import os
import random
import sys
import tempfile
from io import BytesIO

import cv2
import numpy as np
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import DEV_MOD


class ImageMaker():
    target_file = None
    def __init__(self, image_data = None):
        if DEV_MOD:
            test_images_directory = "src/pic/test_images"
            files = os.listdir(test_images_directory)
            random_file = random.choice(files)
            self.target_file = os.path.join(test_images_directory, random_file)
        else:
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))
            
            # 임시 파일로 저장
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            image.save(temp_file.name, format="JPEG")
            self.target_file = temp_file.name

    def get_morphological_edge(self, src):
        imgBlur = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)  # gray image
        thresh = cv2.threshold(imgBlur, 128, 255, cv2.THRESH_BINARY)[1]
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
        dilate = cv2.morphologyEx(thresh, cv2.MORPH_DILATE, kernel)
        diff = cv2.absdiff(dilate, thresh)
        edges = diff
        return edges

    def get_contours(self, edge, imgContour):
        contours, hierarchy =cv2.findContours(edge, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        min_area = 400
        max_area = edge.shape[0] * edge.shape[1] / 8
        ptsCandidate = []
        approxCandidate = []

        for cnt in contours:
            if len(cnt) == 0: continue
            area = cv2.contourArea(cnt) #   윤곽선의 면적
            if  area < min_area: continue  #최소 크기 제약조건
            cv2.drawContours(imgContour, cnt, -1, (255,0,0), 3)
            peri = cv2.arcLength(cnt, True)     #윤곽선의 길이
            epsilon = 0.02 * peri
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            x, y, w, h = cv2.boundingRect(approx)
            if w*h > max_area: continue     #최대 크기 제약조건
            ptsCandidate.append([x,y,x+w,y+h])
            approxCandidate.append(approx)
        return ptsCandidate,approxCandidate

    def quiz(self, ptsCandidate, approxCandidate, num, imgMask, ref):
        centers = []  # 중심점 저장할 리스트
        approxs = []
        # 항상 문제가 달라지게
        indexes = np.random.permutation(np.arange(len(ptsCandidate)))  # 인덱스를 섞음
        cnt = 0
        min_distance = 1

        # 문제들마다 일정한 거리가 있었으면 좋겠어
        for i in indexes:
            if cnt >= num:
                break


            x1 = ptsCandidate[i][0]
            y1 = ptsCandidate[i][1]
            x2 = ptsCandidate[i][2]
            y2 = ptsCandidate[i][3]

            scale_factor = 1.2  # 확대 비율 (20% 더 크게)
            x_center = (x1 + x2) / 2
            y_center = (y1 + y2) / 2
            width = (x2 - x1) * scale_factor
            height = (y2 - y1) * scale_factor
            x1 = x_center - width / 2
            x2 = x_center + width / 2
            y1 = y_center - height / 2
            y2 = y_center + height / 2

            TOO_CLOSE = False
            # 두 영역 사이의 거리(d)가 너무 가까우면 선택 안하겠어
            for j in centers:
                c1 = [(x1 + x2) / 2, (y1 + y2) / 2]  # 현재 사각형의 중심
                c2 = j  # 이미 선택된 사각형의 중심

                d = np.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)
                if d < min_distance:
                    TOO_CLOSE = True
                    break

            if TOO_CLOSE:
                continue

            approxCandidate[i] = np.int32([approxCandidate[i]])  # fillPoly 에러 방지
            cv2.fillPoly(imgMask, approxCandidate[i], (0, 0, 0))
            cv2.fillPoly(ref, approxCandidate[i], (255, 255, 255))

            centers.append([(x1 + x2) / 2, (y1 + y2) / 2])  # 중심점 저장
            approxs.append(approxCandidate[i])
            cnt += 1

        return centers

    def dev_img_save(self, src, dst, ref):
        current_dir = os.path.dirname(os.path.abspath(__file__))
    
        # test_result 폴더 경로
        result_dir = os.path.join(current_dir, 'test_result')
        
        # test_result 폴더가 없으면 생성
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)

        # 이미지 크기를 동일하게 맞추기
        height = max(src.shape[0], dst.shape[0], ref.shape[0])
        width = max(src.shape[1], dst.shape[1], ref.shape[1])
        
        src = cv2.resize(src, (width, height))
        dst = cv2.resize(dst, (width, height))
        ref = cv2.resize(ref, (width, height))
        cv2.imwrite("result.jpg", np.hstack([src, dst, ref]))

    def centering_image(self, src, dst, ref):
        h, w = src.shape[:2]
        
        # 새 이미지 크기 계산 (원본 이미지보다 크게)
        new_size = max(h, w)
        new_size = new_size + (new_size % 2)  # 짝수로 만들기
        
        # 새 이미지 생성
        src_output = np.zeros((new_size, new_size, 3), dtype=np.uint8)
        dst_output = np.zeros((new_size, new_size, 3), dtype=np.uint8)
        ref_output = np.zeros((new_size, new_size, 3), dtype=np.uint8)
        
        # 원본 이미지를 새 이미지의 중앙에 배치
        x_offset = (new_size - w) // 2
        y_offset = (new_size - h) // 2
        
        src_output[y_offset:y_offset+h, x_offset:x_offset+w] = src
        dst_output[y_offset:y_offset+h, x_offset:x_offset+w] = dst
        ref_output[y_offset:y_offset+h, x_offset:x_offset+w] = ref
    
        # 이동한 좌표 계산
        t = (x_offset, y_offset)
        
        return src_output, dst_output, ref_output, t



    def gen_quiz_image(self):
        src = cv2.imread(self.target_file)
        dst = src.copy()
        ref = src.copy()
        edges = self.get_morphological_edge(src)
        imgContour = src.copy()                 #   contour를 얻고
        imgMask = np.full(src.shape[:2], 255, np.uint8)  # 흰색바탕에 마스크부분만 검은색         4

        # #   퀴즈 후보 & 퀴즈
        ptsCandidate, approxCandidate = self.get_contours(edges, imgContour)
        pts = self.quiz(ptsCandidate, approxCandidate, 5, imgMask, ref)

        cv2.xphoto.inpaint(ref, imgMask, dst, 0)

        # 이미지 중앙으로 위치시키기
        src, dst, ref , t = self.centering_image(src, dst, ref)
        if DEV_MOD:
            self.dev_img_save(src, dst, ref)
        # # 이미지를 가로로 병합하기
        # img = np.hstack([src,dst,ref])
        # return img, pts, t # (원본, 틀린그림, 정답그림), 정답 좌표, 이동한 좌표
        src_base64 = self.image_to_base64(src)
        dst_base64 = self.image_to_base64(dst)
        ref_base64 = self.image_to_base64(ref)

        response_data = {"src": src_base64, "dst": dst_base64, "ref": ref_base64, "t": t, "pts": pts}

        return response_data
    
    def image_to_base64(self, img):
        _, buffer = cv2.imencode('.jpg', img)
        img_str = base64.b64encode(buffer).decode()
        return img_str


# a = ImageMaker()
# a.gen_quiz_image()
