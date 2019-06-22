# -*- coding: utf-8 -*-
# Author:tomorrow505


import os
import subprocess
import requests
import json
from pymediainfo import MediaInfo


def get_video_info(video_file):

    mediainfo = ''
    media_info = MediaInfo.parse(video_file)
    data = media_info.to_json()
    data = json.loads(data)['tracks']
    audio_num = 0
    for key in data:
        if key['track_type'] == 'General':
            general = get_general(key)
            mediainfo = general + '\n'
        elif key['track_type'] == 'Video':
            video = get_video(key)
            mediainfo = mediainfo + '\n' + video + '\n'
        elif key['track_type'] == 'Audio':
            audio_num = audio_num + 1
            if audio_num > 2:
                continue
            audio = get_audio(key)
            mediainfo = mediainfo + '\n' + audio + '\n'

    mediainfo = '[quote=iNFO][font=Courier New]'+mediainfo+'[/font][/quote]'

    return mediainfo


def get_general(key):

    general = []
    general.append(key['track_type'])
    general.append(check('UniqueID/String------------------: ', key, 'other_unique_id'))
    general.append(check('Format/String--------------------: ', key, 'format'))
    general.append(check('Format_Version-------------------: ', key, 'format_version'))
    general.append(check('FileSize/String------------------: ', key, 'other_file_size'))
    general.append(check('Duration/String------------------: ', key, 'other_duration'))
    general.append(check('OverallBitRate/String------------: ', key, 'other_overall_bit_rate'))
    general.append(check('Encoded_Date---------------------: ', key, 'encoded_date'))
    general.append(check('other_writing_application--------: ', key, 'other_writing_application'))
    general.append(check('Encoded_Application/String-------: ', key, 'writing_library'))

    general = '\n'.join(part for part in general if part)
    return general


def get_audio(key):

    general = []
    general.append(key['track_type'])
    general.append(check('ID/String------------------------: ', key, 'count_of_stream_of_this_kind'))
    general.append(check('Format/String--------------------: ', key, 'other_format'))
    general.append(check('Format/Info----------------------: ', key, 'format_info'))
    general.append(check('CodecID--------------------------: ', key, 'codec_id'))
    general.append(check('Duration/String------------------: ', key, 'other_duration'))
    general.append(check('BitRate/String-------------------: ', key, 'other_bit_rate'))
    general.append(check('Channel(s)/String----------------: ', key, 'other_channel_s'))
    general.append(check('ChannelLayout--------------------: ', key, 'channel_layout'))
    general.append(check('SamplingRate/String--------------: ', key, 'other_sampling_rate'))
    general.append(check('FrameRate/String-----------------: ', key, 'other_frame_rate'))
    general.append(check('Compression_Mode/String----------: ', key, 'compression_mode'))
    general.append(check('Video_Delay/String---------------: ', key, 'other_delay_relative_to_video'))
    general.append(check('StreamSize/String----------------: ', key, 'other_stream_size'))
    general.append(check('Title----------------------------: ', key, 'title'))
    general.append(check('Language/String------------------: ', key, 'other_language'))
    general.append(check('Default/String-------------------: ', key, 'default'))
    general.append(check('Forced/String--------------------: ', key, 'forced'))

    general = '\n'.join(part for part in general if part)
    return general


def get_video(key):

    general = []
    general.append(key['track_type'])

    general.append(check('ID/String------------------------: ', key, 'count_of_stream_of_this_kind'))
    general.append(check('Format/String--------------------: ', key, 'format'))
    general.append(check('Format/Info----------------------: ', key, 'format_info'))
    general.append(check('Format_Profile-------------------: ', key, 'format_profile'))
    general.append(check('Format_Settings------------------: ', key, 'format_settings'))
    general.append(check('Format_Settings_CABAC/String-----: ', key, 'format_settings__cabac'))
    general.append(check('Format_Settings_RefFrames/String-: ', key, 'other_format_settings__reframes'))
    general.append(check('CodecID--------------------------: ', key, 'codec_id'))
    general.append(check('Duration/String------------------: ', key, 'other_duration'))
    general.append(check('BitRate/String-------------------: ', key, 'other_bit_rate'))
    general.append(check('Width/String---------------------: ', key, 'other_width'))
    general.append(check('Height/String--------------------: ', key, 'other_height'))
    general.append(check('DisplayAspectRatio/String--------: ', key, 'other_display_aspect_ratio'))
    general.append(check('FrameRate_Mode/String------------: ', key, 'other_frame_rate_mode'))
    general.append(check('FrameRate/String-----------------: ', key, 'other_frame_rate'))
    general.append(check('ColorSpace-----------------------: ', key, 'color_space'))
    general.append(check('ChromaSubsampling/String---------: ', key, 'chroma_subsampling'))
    general.append(check('BitDepth/String------------------: ', key, 'other_bit_depth'))
    general.append(check('ScanType/String------------------: ', key, 'other_scan_type'))
    general.append(check('Bits-(Pixel*Frame)---------------: ', key, 'bits__pixel_frame'))
    general.append(check('StreamSize/String----------------: ', key, 'other_stream_size'))
    general.append(check('Default/String-------------------: ', key, 'default'))
    general.append(check('Forced/String--------------------: ', key, 'forced '))

    general = '\n'.join(part for part in general if part)
    return general


def check(str1, key, str2):
    if str2 in key.keys():
        if str2.find('other') >= 0:
            r_part = key[str2][0]
        else:
            r_part = key[str2]
        return str1 + r_part
    else:
        return ''


def get_frame(video_file):
    media_info = MediaInfo.parse(video_file)
    data = media_info.to_json()
    data = json.loads(data)['tracks']
    for key in data:
        # print(key)
        if key['track_type'] == 'Video':
            frame_rate = key['frame_rate']
            frame_count = key['frame_count']
            break
    return frame_rate, frame_count


def get_picture(file_loc, img_loc):
    time = []
    ratio, total = get_frame(file_loc)

    total_num = int(total) / (int(ratio.split('.')[0]))
    start = total_num * 0.1
    step = total_num * 0.8 / 11
    time.append(change_to_ss(start))
    for i in range(1, 12):
        midle = start + i * step
        time.append(change_to_ss(midle))
    # print('正在截图……')
    for i in range(12):
        base_command = 'ffmpeg -ss {time} -i "{file}" -vframes 1 -y -vf "scale=500:-1" "out-{i}".jpg 2> NUL'
        ffmpeg_sh = base_command.format(time=time[i], file=file_loc, i=i)
        subprocess.call(ffmpeg_sh, shell=True)
        # os.system(ffmpeg_sh)
    # print('正在合成图片……')
    set_par = 'tile=3x4:nb_frames=0:padding=5:margin=5:color=random'
    base_command = 'ffmpeg -i "out-%d.jpg" -y -filter_complex "{set}" "{img_loc}" 2> NUL'.format(
        set=set_par, img_loc=img_loc,)
    subprocess.call(base_command, shell=True)
    # os.system(base_command)

    for i in range(12):
        os.remove('out-{i}.jpg'.format(i=i))

    data = {
        'smfile': open(img_loc, "rb"),
        'file_id': ' '
    }
    # print('准备发送图片……')
    pic_url = send_picture(files=data)

    thanks = '[quote="截图"]自动随机截图，不喜勿看。——>该部分感谢@[url=https://hudbt.hust.edu.cn/userdetails.php?id=107055]' \
             '[color=Red]rach[/color][/url]的指导[/quote]\n'

    return thanks + '[img]' + pic_url + '[/img]'


def send_picture(files=None):

    des_url = 'https://sm.ms/api/upload'
    try:
        des_post = requests.post(
            url=des_url,
            files=files)
    except Exception as exc:
        pass
        # print('发送图片失败: %s' % exc)

    data = json.loads(des_post.content.decode())['data']

    url_to_descr = data['url']
    # print('获取图片链接成功。')
    return url_to_descr


def change_to_ss(number):
    hh = int(number / 3600)
    number_ = number - 3600 * hh
    mm = int(number_ / 60)
    ss = int(number_ - 60 * mm)
    hh = str(hh).zfill(2)
    mm = str(mm).zfill(2)
    ss = str(ss).zfill(2)
    time = '%s:%s:%s' % (hh, mm, ss)
    return time

