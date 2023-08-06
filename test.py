def main():
    url = 'https://kin.naver.com/qna/detail.naver?d1id=3&dirId=31303&docId=448086400'
    url_start = url.split('naver?')
    url1 = url_start[0] + 'naver?'
    url_end = url.split('dirId')
    url2 = 'dirId' + url_end[1]
    print(url1+url2)





if __name__ == '__main__':
    main()