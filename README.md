# PROJECT: Fake Trip
- [마이리얼트립](https://www.myrealtrip.com/) 클론 사이트
- **국내 숙소** 카테고리를 한정으로 검색, 조건별 필터링, 예약 기능 구현
<img src="https://velog.velcdn.com/images/miracle-21/post/71493c6e-5b0b-44ee-8b9a-aebbdec89d26/image.png">

## 📆 개발 기간
- 개발 기간 : 2022-07-04 ~ 2022-07-15 (12일)

## 🧑🏻‍💻 팀 인원
- BE(2명): [박민하](https://github.com/miracle-21), [정진관](https://github.com/dingwan0331)
- FE(4명): [김인태](https://github.com/dlsxody1), [장류광](https://github.com/dkzks44), 정현준, [조예지](https://github.com/Dumibell)
  - [FE GitHub 링크](https://github.com/wecode-bootcamp-korea/34-2nd-Fake-Trip-frontend)

## 🖥 Backend 역할

**박민하**
- ERD 모델링
- 메인페이지(Product List) API
  - GET
  - 숙소리스트 조건별 필터링
- 검색페이지(Product List) API
  - GET
  - 기간, 인원별 검색에 대한 필터링
  - 숙소 종류, 금액 범위, 시설 다중 체크박스 필터링
  - 만실인 경우 자동 필터링

**정진관**
- ERD 모델링
- 웹 서버 구축(AWS: EC2 & RDS)
- 회원가입/로그인(SigninView)
  - GET
  - Kakao API를 통한 소셜로그인 기능
  - JWT를 이용하여 토큰 발급
- 상품페이지(ProductView & RoomsView)
  - GET
  - 방의 재고와 예약테이블 현황에 따른 예약가능 여부 반환
  - 예약인원 + 예약기간에 따라 예약가능한 rooms 데이터만 반환
- 리뷰 기능(Review)
  - POST, GET, DELETE
  - S3 & Form Data를 이용한 이미지 업로드 기능
  - 
- 유저 정보 변경 기능(UserView)
- 예약 기능(ReservationView)
  - POST
  - 예약자 정보와 투숙객 정보를 분리하여 관리
  - validators moulde의 클래스화
  - Json Field를 활용한 투숙객 정보 관리
## 💻 Backend 기술 스택

|                                                Language                                                |                                                Framwork                                                |                                               Database                                               |                                                     ENV                                                      |                                                   HTTP                                                   |                                                  Deploy                                                 |
| :----------------------------------------------------------------------------------------------------: | :----------------------------------------------------------------------------------------------------: | :--------------------------------------------------------------------------------------------------: | :----------------------------------------------------------------------------------------------------------: | :------------------------------------------------------------------------------------------------------: |:------------------------------------------------------------------------------------------------------: |
| <img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white"> | <img src="https://img.shields.io/badge/django-092E20?style=for-the-badge&logo=django&logoColor=white"> | <img src="https://img.shields.io/badge/mysql-4479A1?style=for-the-badge&logo=mysql&logoColor=black"> | <img src="https://img.shields.io/badge/miniconda3-44A833?style=for-the-badge&logo=anaconda&logoColor=white"> | <img src="https://img.shields.io/badge/postman-FF6C37?style=for-the-badge&logo=postman&logoColor=white"> | <img src="https://img.shields.io/badge/aws-232F3E?style=for-the-badge&logo=Amazon AWS&logoColor=white"> 


## ❓ 프로젝트 선정 이유
- AWS, Kakao Rest Api, 다양한 orm 구현 가능.

## 📚 팀 프로젝트 자료

### ERD
![](https://velog.velcdn.com/images/miracle-21/post/79930301-e01b-433b-90c5-a8ffa096cb55/image.png)

### 사이트 시현 사진
![](https://velog.velcdn.com/images/miracle-21/post/cc383f7c-c4ec-4696-9acf-f5d1c42f33ae/image.gif)

### 사이트 시현 영상
[데모 영상](https://ifh.cc/v/oppC60.mp4)

## 🛠 협업 툴
![](https://velog.velcdn.com/images/miracle-21/post/0e0445ab-4831-4592-9db0-6c1eeae03c08/image.png)

## 🔖 Reference
- 이 프로젝트는 [마이리얼트립](https://www.myrealtrip.com/) 사이트를 참조하여 학습 목적으로 만들었습니다.
- 실무수준의 프로젝트이지만 학습용으로 만들었기 때문에 이 코드를 활용하여 이득을 취하거나 무단 배포할 경우 법적으로 문제될 수 있습니다.

