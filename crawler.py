import os
import re
import requests
from bs4 import BeautifulSoup

from utils import Webtoon
from utils import Episode


def title_crawler(title_input):

    output_tuple_lists=list()

    # HTML파일을 저장하거나 불러올 경로
    file_path = f'data/episode_list.html'
    # HTTP요청을 보낼 주소
    url_episode_list = 'http://comic.naver.com/webtoon/weekday.nhn'

    # HTML파일이 로컬에 저장되어 있는지 검사
    if os.path.exists(file_path):
        # 저장되어 있다면, 해당 파일을 읽어서 html변수에 할당
        html = open(file_path, 'rt').read()
    else:
        # 저장되어 있지 않다면, requests를 사용해 HTTP GET요청
        response = requests.get(url_episode_list)
        # 요청 응답객체의 text속성값을 html변수에 할당
        html = response.text
        # 받은 텍스트 데이터를 HTML파일로 저장
        open(file_path, 'wt').write(html)

    # BeautifulSoup클래스형 객체 생성 및 soup변수에 할당
    soup = BeautifulSoup(html, 'lxml')

    cols= soup.select('div.col_inner  a.title')

    for titles in cols:
        if title_input in titles.text.strip():
            id_num=re.findall(r'titleId=(\d+)',titles.get('href'))

            output_tuple_lists.append((id_num[0],titles.text.strip()))

    return list(set(output_tuple_lists))
            #'/webtoon/list.nhn?titleId=679519&weekday=thu',



if __name__=='__main__':
    while(True):
        print('Ctrl=c 로 종료합니다.')
        webtoon_name =input('검색할 웹툰명을 입력해주세요:')
        result_list=title_crawler(str(webtoon_name))
        #print(result_list)

        for i, name in enumerate(result_list):
            print(f'{i}. {name[1]}')
        choosed_num=input('선택:')

        webtoon=Webtoon((result_list[int(choosed_num)])[0])
        print(webtoon.title)
        print('     작가명: ',webtoon.author)
        print('     설명: ', webtoon.description)


        print(f'현재 "{webtoon.title}" 웹툰이 선택되어 있습니다.' )
        print(f'0. 웹툰 정보 보기')
        print(f'1. 웹툰 저장하기 ')
        print(f'2. 다른 웹툰 검색해서 선택하기')
        choosed_op = input('선택: ')

        print(type(choosed_op))
        if choosed_op == '0':
            print(webtoon.title)
            print('     작가명: ', webtoon.author)
            print('     설명: ', webtoon.description)

        elif choosed_op == '1':
            webtoon.get_every_page_html()
            webtoon.get_every_ep_list()

            print(f'웹툰 저장 시작 총{len(webtoon.episode_list)+1}화')

            for i in webtoon.episode_list:
                i.get_image_url_list()
                i.download_all_images()
                print(f'{i.no}화 저장 완료')


        elif choosed_op == '2':
            continue


