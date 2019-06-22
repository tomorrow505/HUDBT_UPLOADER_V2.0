# -*- coding: utf-8 -*-
# Author:tomorrow505

import re
import gen


def get_douban_descr(url):

    if type(url) == str:
        if url.find('imdb') >= 0:
            imdb_link = re.search('.*imdb.com/title/(tt\d{5,9})', url)
            url = {'site': 'douban', 'sid': imdb_link.group(1)}
    gen_ = gen.Gen(url).gen(_debug=True)
    if gen_["success"]:
        descr = gen_["format"]

        old_str = 'https://img3.doubanio.com/view/photo/l_ratio_poster/public/'
        new_str = 'https://img1.doubanio.com/view/photo/l_ratio_poster/public/'

        descr = re.sub(old_str, new_str, descr)
        # print(descr)
        return descr
    else:
        return 'error'


def get_douban_link(url):
    try:
        douban_id = re.search('.*douban.com/subject/(\d{7,8})', url)
        douban_link = 'https://movie.douban.com/subject/' + douban_id.group(1) + '/'
        flag = 1
    except AttributeError:
        flag = 0
    if flag == 0:
        try:
            douban_id = re.search('.*imdb.com/title/(tt\d{7,8})', url)
            douban_link = 'https://www.imdb.com/title/' + douban_id.group(1) + '/'
        except AttributeError:
            douban_link = ''
    return douban_link


# if __name__ == "__main__":
#     print(get_douban_descr('https://movie.douban.com/subject/30474718/'))
