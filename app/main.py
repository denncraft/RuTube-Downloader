import os.path
import sys
import shutil
import requests

print('sys.argv[0] = ', sys.argv[0])
pathname = os.path.dirname(sys.argv[0])
print('path = ', pathname)
print('full path =', os.path.abspath(pathname))
file_path = 'c:\\temp'

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.132 YaBrowser/22.3.1.892 Yowser/2.5 Safari/537.36',
    'accept': '*/*'
}


def get_m3u8_list(url):
    req = requests.get(url=url, headers=headers)
    video_data = req.json()
    video_author = video_data['author']['name']
    video_title = video_data['title']
    dict_repl = ["/", "[", "]", "?", "'", '"', ":", "*"]
    for repl in dict_repl:
        if repl in video_title:
            video_title = video_title.replace(repl, "")
        if repl in video_author:
            video_author = video_author.replace(repl, "")
    video_title = video_title.replace(" ", "_")
    video_author = video_author.replace(" ", "_")

    video_m3u8 = video_data['video_balancer']['m3u8']
    return video_author, video_title, video_m3u8


def get_m3u8_link(url):
    req = requests.get(url=url, headers=headers)
    data = req.text
    # print(data)
    # return data.split('#EXT-X-STREAM-INF:')[-1].split(' ')[-1]
    return data.split('\n')[-2]


def get_segment_list(url):
    req = requests.get(url=url, headers=headers)
    data = req.text.split('\n')
    seg_dict = []
    for seg in data:
        if '/segment-' in seg:
            seg_dict.append(seg.split('/')[-1])

    # return seg_dict[-1].split('/')[-1].split('-')[1]
    return seg_dict


def download_segments(link, segments):
    if not os.path.isdir(f'{file_path}\\seg'):
        os.mkdir(f'{file_path}\\seg')

    for file_name in segments:
        print(f'[+] - Загрузка {file_name}')
        # print(f'[+] - {link}{file_name}')
        req = requests.get(f'{link}{file_name}')

        with open(f'{file_path}\\seg\\{file_name}', 'wb') as file:
            file.write(req.content)

    print('[Info] - Все сегменты загружены')


def merge_ts(author, title, segments):
    print('[+] + Начинаем обхединение ts файлов')
    with open(f'{file_path}\\{title}.ts', 'wb') as merged:
        for segment in segments:
            with open(f'{file_path}\\seg\\{segment}', 'rb') as mergefile:
                shutil.copyfileobj(mergefile, merged)
    print('[+] + Начинаем конвертирование ts файла в mp4 файл')
    os.system(f"ffmpeg -i {file_path}\\{title}.ts {file_path}\\{author}-{title}.mp4")
    print('[+] + Конвертирование завершено')


def main():
    video_id = input('[+] - Введите ссылку на видео для загрузки >>> ').split("/")[-2]
    # print(video_id)
    m3u8_url = get_m3u8_list(
        f'https://rutube.ru/api/play/options/{video_id}/?no_404=true&referer=http%3A%2F%2Frutube.ru')
    # print(m3u8_url)
    m3u8_link = get_m3u8_link(m3u8_url[2])
    # print(m3u8_link)
    seg_list = get_segment_list(m3u8_link)
    dwnl_link = f'{m3u8_link.split(".m3u8")[0]}/'
    download_segments(dwnl_link, seg_list)
    merge_ts(m3u8_url[0], m3u8_url[1], seg_list)

    file_dir = os.listdir(f'{file_path}\\seg')
    for file in file_dir:
        os.remove(f'{file_path}\\seg\\{file}')
        os.removedirs(f'{file_path}\\seg')


if __name__ == "__main__":
    main()

# f'https://rutube.ru/api/play/options/c163a1553b2b3c4ba7162d51404893ff/?no_404=true&referer=http%3A%2F%2Frutube.ru'

# "  https://rutube.ru/video/e1b3d3326dbb6a5ba119efea52e6308d/  "

"   https://rutube.ru/video/7d73add104603eb3e21a58b5b80baa57/  "