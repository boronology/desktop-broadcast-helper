#!/usr/bin/env/ python
# -*-coding: utf-8 -*-

import os

def get_encoder():
    """
    エンコーダを取得する。
    見つかった場合にはavconvあるいはffmpegの文字列を返す。
    見つからなかった場合は0を返す
    """
    exist_ffmpeg=os.access("/usr/bin/ffmpeg",os.R_OK)
    exist_libav=os.access("/usr/bin/avconv",os.R_OK)
    if exist_libav and exist_ffmpeg:
        print "ffmpegとlibav両方が見つかりました。\nどちらを利用するか選択してください"
        print "1 - ffmpeg \n2 - libav（推奨）"
        selection = raw_input(">>")
        if selection=="1":
            return "ffmpeg"
        elif selection=="2":
            return "avconv"
        else:
            print "値が不正です\n"
            return get_encoder()
    elif (exist_libav or exist_ffmpeg)==0:
        print "利用できるエンコーダが存在しません。\nffmpegかlibavをインストールしてください"
        return 0
    else:
        return "ffmpeg"*exist_ffmpeg + "avconv"+exist_libav

def get_video_source():
    """
    動画のソースを取得する。
    /dev/video0あるいはX11のキャプチャ
    """
    exist_video0 = os.access("/dev/video0",os.R_OK)
    if(exist_video0):
        print "入力する画像のソースを選択してください"
        print "1 - /dev/video（webcam studioやカメラ等を利用する場合）"
        print "2 - X11（画面を直接キャプチャする場合）"
        selection = raw_input(">>")
        if selection == "1":
            return dev_video()
        elif selection == "2":
            return capture_x11()
        else:
            print "値が不正です"
            return get_video_source()
    else:
        return capture_x11()

def dev_video():
    """
    video1,video2……が存在する場合はあとで書く
    とりあえずvideo0に関してはこれで動く
    """
    return "-f video4linux2 -i /dev/video0"

def capture_x11():
    """
    通常の画面出力からキャプチャする
    """
    print "キャプチャする範囲を設定します。\nこれらは録画開始後には変更できません。"
    
    print "キャプチャする横幅を入力してください"
    width = raw_input(">>")
    print "キャプチャする縦幅を入力してください"
    height = raw_input(">>")
    
    print "x方向（右方向への）オフセットを入力してください"
    offset_x = raw_input(">>")
    print "y方向（下方向への）オフセットを入力してください"
    offset_y = raw_input(">>")
    
    if width.isdigit()==height.isdigit()==offset_x.isdigit()==offset_y.isdigit()==1:
        return "-f x11grab -s {0}x{1} -i :0.0+{2},{3}".format(width,height,offset_x,offset_y)
    else:
        print "入力が不正です。再入力してください"
        return capture_x11()

def get_sound_source():
    """
    入力するサウンドのソースを選択する
    どうやらffmpeg単体では複数の入力音声をひとつにまとめることはできないらしい
    """
    print ("利用するサウンドを選択してください\n" +
           "0 - サウンドなし\n1 - マイクから\n2 - 再生中のサウンド")
    selection = raw_input(">>")
    if selection == "0":
        return "-an"
    elif selection == "1":
        return get_rec_mic()
    elif selection == "2":
        return get_rec_playing()
    else:
        print "入力が不正です"
        return get_sound_source()

def get_rec_playing():
    return "-f alsa -ac 2 -i pulse"

def get_rec_card():
    with open("/proc/asound/cards") as cards:
        cards_list = cards.readlines()
        if len(cards_list)==2:
            print "1つのカードが見つかりました。{0}を選択します".format(cards_list[0])
            return "hw:0"
        else:
            print "複数のカードが見つかりました。\nマイクの接続されているカードを選んでください"
            cards_max = len(cards_list)/2-1
            for i in cards_list:
                print i
            print "0-{0}".format(cards_max)
            selection = raw_input(">>")
            if selection.isdigit() and 0 <= int(selection) <= cards_max:
                return "hw:" + selection
            else:
                print "入力が不正です。再入力してください"
                return get_rec_card()

def set_output_video():
    """
    配信に使うことからlibx264をデフォルトで。
    後で選択できるようにするかも。
    ffmpeg -codecsで一覧が表示できる
    """
    print "出力する解像度を設定します\n縦の幅を入力してください"
    resolution_x = raw_input(">>")
    print "横の幅を入力してください"
    resolution_y = raw_input(">>")
    print "ビットレートを指定してください(kbit/s)"
    bitrate = raw_input(">>")
    if resolution_x.isdigit() == resolution_y.isdigit() == bitrate.isdigit() == 1:
        return "-vcodec libx264 -s {0}x{1} -b {2}k -vsync 1".format(resolution_x,resolution_y,bitrate)
    else:
        print "入力が不正です。再入力してください。"
        return set_output_video()

def set_output_sound(rec_sound):
    if rec_sound:
        print "出力するサウンドのビットレートを入力してください(kbit/s)"
        bitrate = raw_input(">>")
        if bitrate.isdigit():
            return "-acodec libvo_aacenc -ar 44100 ab {0}k".format(bitrate)
        else:
            print "入力が不正です。再入力してください。"
            return set_output_sound(rec_sound)

def set_output_volume(rec_sound):
    print "録音する音量を調整しますか？(y/n)"
    selection = raw_input(">>")
    if selection == "y":
        print "音量を入力してください。デフォルトの音量は256です。"
        volume = raw_input(">>")
        if volume.isdigit():
            return "-vol {0}".format(volume)
        else:
            print "入力が不正です。再入力してください。"
            return set_output_volume(rec_sound)
    elif selection == "n":
        return "-vol 256"
    else:
        return set_output_volume(rec_sound)

def set_threads():
    with open("/proc/cpuinfo") as cpuinfo:
        processors = len(filter((lambda x:"processor" in x) ,cpuinfo.readlines()))
        print "スレッド数を設定します。デフォルトでは{0}です".format(processors)
        selection = raw_input(">>")
        if selection.isdigit() and selection != "0":
            return "-threads {0}".format(selection)
        else:
            return "-threads {}".format(processors)
        
