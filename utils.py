'''
네이버 웹툰 크롤러 구현
utils.py
    클래스
        Webtoon
            기존 정보

        Episode
            webtoon <- webtoon_id대신 Webtoon인스턴스를 받도록 함
            title
            url

        EpisodeImage
            episode
            url
            file_path

crawler.py
    사용자 입력을 받아 처리해줌

python crawler.py로 실행
-----

안내) Ctrl+C로 종료합니다.
검색할 웹툰명을 입력해주세요: 대학
 1. 대학일기
 2. 안녕, 대학생
선택: 1

현재 "대학일기" 웹툰이 선택되어 있습니다
 1. 웹툰 정보 보기
 2. 웹툰 저장하기 (extra)
 3. 다른 웹툰 검색해서 선택하기
선택: 1

 대학일기
    작가명: 자까
    설명: 로망이 꽃피는 캠퍼스는 없다. 극사실주의에 기반한 너무나 현실적인 우리의 대학일기
    총 연재회수:
    등등...

-> extra1)
현재 "대학일기" 웹툰이 선택되어 있습니다
 1. 웹툰 정보 보기
 2. 웹툰 저장하기
 3. 다른 웹툰 검색해서 선택하기
선택: 2

웹툰 저장 시작 (총 210화)
 1화 저장완료
 2화 저장완료
 3화 저장완료
 ....
-> extra2) 맨 처음 페이지부터 끝 페이지까지 저장해보기
-> extra3) 저장 이후 해당 내용을 볼 수 있는 HTML도 생성하기
    open('webtoon1.html', 'wt').write()

git clone <저장소>
cd <저장소>
(가상환경만들어서 적용하고)
pip install -r requirements.txt
python crawler.py


.gitignore에 파일을 저장한 폴더는 제외하도록 설정

'''



#대략적인 전체 구조

#   webtoon > Episode > EpisodeImage
#file_path, url 여러번 선언 안하고 위에서 받아서 잘 쓰고싶다.

#개별 웹툰에 대한 정보가 담긴 클래스.
#Episdoe객체들이 담긴 리스트 보유.
import os
from urllib import parse

import requests
from bs4 import BeautifulSoup


class Webtoon:

    def __init__(self,webtoon_id):
        self.webtoon_id=webtoon_id
        self._title = None           #접근하면 알아서 정보 저장 하도록 property 로 만든다.
        self._author = None
        self._description = None
        self.url_thumnail = None
        self.episode_list=list() # 여기에 에피소드 객체들을 담아 놓는다.
        self._html= ''

        self.every_page_html_list=list()
        self.max_page_num=None

        #default-setting
        self.base_dir_path = os.getcwd() #현재 디렉토리경로 알아내는 함수.
        self.base_url_path ='http://comic.naver.com/webtoon/list.nhn?'

    def set_attr_if_not_exist(self,attr_name):
        if not getattr(self,attr_name):
            self.get_Webtoon_info()
        return getattr(self, attr_name)


    @property
    def title(self):
        return self.set_attr_if_not_exist('_title')

    @property
    def author(self):
        return self.set_attr_if_not_exist('_author')
    @property
    def description(self):
        return self.set_attr_if_not_exist('_description')


    @property
    def html(self):
        if not self._html:
            #해당 웹툰 id로된 디렉토리 없으면 생성
            this_webtoon_dir_path=f'{self.base_dir_path}/data/{self.webtoon_id}'
            if not os.path.exists(this_webtoon_dir_path):
                os.makedirs(this_webtoon_dir_path)

            #html 파일 없으면 생성, 저장
            #있으면 open해서 self.html 에 저장.
            this_webtoon_html_path=f'{this_webtoon_dir_path}/{self.webtoon_id}.html'
            if not os.path.exists(this_webtoon_html_path):
                response=requests.get(self.base_url_path,params={'titleId':self.webtoon_id})
                html = response.text
                open(this_webtoon_html_path,'wt').write(html)
            else:
                html = open(this_webtoon_html_path,'rt').read()

            self._html = html

        return self._html

    #해당 웹툰의 기본정보 가져오는 크롤러.
    def get_Webtoon_info(self):
        soup = BeautifulSoup(self.html,'lxml')
        div_detail=soup.select_one('div.detail')

        h2_title = div_detail.select_one('h2')
        self._title = h2_title.contents[0].lstrip()
        self._author = h2_title.contents[1].get_text(strip=True)
        self._description = div_detail.select_one('p').text
        self.url_thumnail =soup.select_one('div.thumb img').get('src')

        #tips
        #.contents 는 테그 형에게만 써서 [0]원소 단위로 접근 가능해짐. 리스트로 받아도 원소 1개일때 유용.
        #get_text(strip =True) 함수는 str 아닌것이사용 가능.
        #str 은  ' ' .strip()     사용


    #웹툰의 여분 페이지의 html을 다 가져다가 저장하는 함수.
    def get_every_page_html(self):
        # 페이지가 총 몇개인지 살펴볼 필요가 있다.--->이미 저장된 html 페이지 맨및의 숫자를기준으로하자. select 해서 len해보자.
        soup = BeautifulSoup(self.html,'lxml')
        self.max_page_num =soup.select_one('div.page_wrap').contents[-4].text#끝에서 네번째가 마지막 페이지다.

        if not self.every_page_html_list:
            for i in range(int(self.max_page_num)):
                this_webtoon_dir_path = f'{self.base_dir_path}/data/{self.webtoon_id}'
                this_page_html_path = f'{this_webtoon_dir_path}/{self.webtoon_id}-{(i+1)}.html'
                print(this_page_html_path)
                if not os.path.exists(this_page_html_path):
                    response=requests.get(self.base_url_path,params={'titleId':self.webtoon_id, 'page':i+1})
                    html = response.text
                    open(this_page_html_path,'wt').write(html)
                else:
                    html =open(this_page_html_path,'rt').read()

                self.every_page_html_list.append(html)


    #    def __init__(self,webtoon_inst,no,title,rating , created_date, url_thumnail,episdoe_url):
    #해당 웹툰의 모든 에피소드에 대해 객체를 생성해서 episode_list에 저장하는 함수(크롤러)
    def get_every_ep_list(self):
        num = 1
        for page in self.every_page_html_list:
            soup = BeautifulSoup(page,'lxml')
            ep_table = soup.select('table.viewList > tr')
            for tr in ep_table:

                if tr.get('class'):
                    continue
                print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
                #print (tr)
                print(num)
                num=num+1

                url_thumbnail = tr.select_one('td:nth-of-type(1) img').get('src')
                # 현재 tr의 첫 번째 td요소의 자식   a태그의 'href'속성값
                from urllib import parse
                url_detail = tr.select_one('td:nth-of-type(1) > a').get('href')
                query_string = parse.urlsplit(url_detail).query
                query_dict = parse.parse_qs(query_string)
                # print(query_dict)
                no = query_dict['no'][0]

                # 현재 tr의 두 번째 td요소의 자식 a요소의 내용
                title = tr.select_one('td:nth-of-type(2) > a').get_text(strip=True)
                # 현재 tr의 세 번째 td요소의 하위 strong태그의 내용
                rating = tr.select_one('td:nth-of-type(3) strong').get_text(strip=True)
                # 현재 tr의 네 번째 td요소의 내용
                created_date = tr.select_one('td:nth-of-type(4)').get_text(strip=True)




                new_ep=Episode(
                    webtoon_inst=self,
                    no=no,
                    title=title,
                    rating=rating,
                    created_date=created_date,
                    url_thumnail=url_thumbnail,
                )

                self.episode_list.append(new_ep)








# 각 에피소드에 대한 정보가 담긴 클래스.
# 각 EpisdoeImage 객체가 담긴 리스트 보유.
class Episode:
    # 웹툰 클래스에서 어떤 함수 실행하면 init 실행될 것이다.
    def __init__(self,webtoon_inst,no,title,rating , created_date, url_thumnail):
        self.webtoon_inst = webtoon_inst # 이 객체의 상위 소속 객체.
        self.no = no
        self.title = title#여기서 왜 오류 뜨는지 모르겠다.
        self.created_date = created_date
        self.url_thumnail = url_thumnail
        self.image_url_list=list()

    @property
    def url(self):
        """
        self.webtoon_id, self.no 요소를 사용하여
        실제 에피소드 페이지 URL을 리턴
        :return:
        """
        url = 'http://comic.naver.com/webtoon/detail.nhn?'
        params = {
            'titleId': self.webtoon_inst.webtoon_id,
            'no': self.no,
        }

        episode_url = url + parse.urlencode(params)
        return episode_url

    def get_image_url_list(self):

        # 각 웹툰 id번호로된 폴더 없으면 만들어 주겠슴.
        dir_path = 'data/{webtoon_id}/episode_lsit'.format(webtoon_id=self.webtoon_inst.webtoon_id)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        # 에피소드별 페이지로 가는 src파일 경로 만들어줌.
        ep_path = f'{dir_path}/episode-{self.no}'

        # 리퀘스트로 html얻어와서 숲갹체에 넣어서 파스 함.
        if not os.path.exists(ep_path):
            response = requests.get(self.url)
            html = response.text
            open(ep_path, 'wt').write(response.text)
        else:
            html = open(ep_path, 'rt').read()

        soup = BeautifulSoup(html, 'lxml')
        images = soup.select('div.wt_viewer img')  # 여기에 해당 ep 의 이미지들 태그가 들어있다.

        for image in images:  # 각각의 이미지들의 src 주소를 ep 객체의 image_url_list에 담는다.
            self.image_url_list.append(image.get('src'))

    # ep 객체의 image_url_list의 src 받아서 이미지 저장하는 함수.(이것을 여러번 호출해서 이미지 리스트의 이미지를 전부 저장하자.)
    def download_image(self, one_img_url):
        # ep별로 디렉토리 폴더 만들어 준다.
        dir_path = 'data/{webtoon_id}/{ep_no}'.format(webtoon_id=self.webtoon_inst.webtoon_id, ep_no=self.no)

        # 디렉토리 경로 확인후 없으면 이 ep에 대한 img들의 디렉토리 만들기
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        # one_img_url='http://imgcomic.naver.net/webtoon/679519/210/20180530171703_f5b34a423122c136d4016797bbb1b092_IMAG01_1.jpg'

        # 이미지 이름 지정하기 위해 각 src에서 따옴.
        one_img_name = one_img_url.rsplit('/')[-1]
        print(one_img_name)

        # reuqests 해서 다운로드 할때 해더에 Referer 포햄해야 안튐김. 만들어주자.
        url = 'http://comic.naver.com/webtoon/detail.nhn?'

        params = {
            'titleId': self.webtoon_inst.webtoon_id,
        }

        Referer_url = url + parse.urlencode(params)

        file_path = f'{dir_path}/{one_img_name}'
        if not os.path.exists(file_path):
            response_img = requests.get(one_img_url, headers={'Referer': Referer_url})
            open(file_path, 'wb').write(response_img.content)

        # showmewhat=open(file_path, 'rt').read()
        # print(showmewhat)

    def download_all_images(self):
        for image_url in self.image_url_list:
            self.download_image(image_url)



#이미지 리스트의 url 얻고 그것을 각각 저장하는 함수 필요.


# 각 에피소드 내부의 이미지에 대한 정보가 담긴 클래스(정보만 담아놓자.)
class EpisodeImage:

    def __init__(self,episode_inst,one_img_url,file_path):
        self.episode_inst=episode_inst
        self.one_img_url



#708427 만 화 고
#705328 환상적인 소년

if __name__ == '__main__':

#일단 Webtoon 객체에 각 웹툰의 정보를 크롤해서 담아보자.
    man_wha_go = Webtoon(708427)

    print(man_wha_go.title)
    print(man_wha_go.author)
    print(man_wha_go.description)
    man_wha_go.get_every_page_html()
    man_wha_go.get_every_ep_list()
    print(man_wha_go.episode_list)

    man_wha_go.episode_list[0].get_image_url_list()

    man_wha_go.episode_list[0].download_all_images()





















