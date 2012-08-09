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
		print "2 - X11（画面を直接キャプチャする場合。録画開始後に範囲や位置の変更はできません）"
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
	とりあえずこれで動く
	"""
	return "-f video4linux2 -i /dev/video0"

def capture_x11():
	"""
	通常の画面出力からキャプチャする
	"""
	print "キャプチャする横幅を入力してください"
	width = raw_input(">>")
	print "キャプチャする縦幅を入力してください"
	height = raw_input(">>")

	print "x方向（右方向への）オフセットを入力してください"
	offset_x = raw_input(">>")
	print "y方向（下方向への）オフセットを入力してください"
	offset_y = raw_input(">>")
	
	try:
		width = int(width)
		height = int(height)
		offset_x = int(offset_x)
		offset_y = int(offset_y)
	except ValueError:
		print "入力が不正です。再入力してください"
		return capture_x11()
		
	return "-f x11grab -s {0}x{1} -i :0.0+{2},{3}".format(width,height,offset_x,offset_y)

def get_sound_source():
	"""
	入力するサウンドのソースを選択
	"""
	print "再生中のサウンドを録音しますか？\ny - 録音する\nそれ以外 - 録音しない"
	rec_playing = 1 if raw_input(">>")=="y" else 0
	
	print "マイクからの音を録音しますか？\ny - 録音する/nそれ以外 - 録音しない"
	rec_mic = 1 if raw_input(">>")=="y" else 0
	
	if rec_mic and rec_playing:
		return get_rec_playing + " \\\n" + get_rec_mic()
	else:
		return get_rec_playing() * rec_playing + get_rec_mic() * rec_mic

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

def get_rec_mic():
    with open("/proc/asound/devices") as devices:
        devices_list = devices.readlines()
        for i in devices_list:
            print i
        print "入力デバイスを選択してください\n不明な場合は-1を入力"
        device_numbers = map((lambda x:x[0:x.index(":")].lstrip()),devices_list)
        print device_numbers
        selection = raw_input(">>")
        if selection == "-1":
            return get_rec_card()
        elif selection in device_numbers:
            device_name = filter((lambda x:selection in x),devices_list)[0]
            device_id = device_name[device_name.index("[")+1:device_name.index("]")].translate(None," ").replace("-",",")
            return get_rec_card() +","+ device_id
        else:
            print "番号が不正です。もう一度入力してください"
            return get_rec_mic()

def get_output_video_codec:
    """
    配信に使うことからlibx264をデフォルトで。
    後で選択できるようにするかも。
    ffmpeg -codecsで一覧が表示できる
    """
    
