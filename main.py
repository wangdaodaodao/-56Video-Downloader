#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 
# 56视频下载器 
# 作者：WangDaodao
# 版本：v2.0.0
# 时间：2024-12-10 12:31:04
# 

import requests # type: ignore
import json
import time
import os
import re
from urllib3.exceptions import InsecureRequestWarning # type: ignore
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def get_quality_name(quality_type):
    """获取清晰度名称"""

    quality_map = {
        '': '540P',
        '_1': '720P',
        '_21': '1080P'
    }
    return quality_map.get(quality_type, '540P')

def get_video_info(url, quality_type=''):
    """
    获取视频信息
    quality_type: 清晰度类型
        ''   - 540P (默认)
        '_1' - 720P
        '_21' - 1080P
    """
    try:
        print(f"\nSetup 1 [{time.strftime('%Y-%m-%d %H:%M:%S')}] - 开始获取页面内容...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15',
            'Referer': 'https://www.56.com/',
        }
        response = requests.get(url, headers=headers, verify=False)
        
        print(f"Setup 2 [{time.strftime('%Y-%m-%d %H:%M:%S')}] - 正在解析页面获取视频ID...")
        vid_match = re.search(r'vid\s*:\s*[\'"]?(\d+)[\'"]?', response.text)
        if not vid_match:
            raise Exception("无法从页面中获取视频ID")
        vid = vid_match.group(1) + quality_type
        print(f"获取到视频ID: {vid} ({get_quality_name(quality_type)})")
        
        print(f"Setup 3 [{time.strftime('%Y-%m-%d %H:%M:%S')}] - 构造API请求...")
        api_url = "https://my.tv.sohu.com/play/videonew.do"
        params = {
            'vid': vid,
            'uid': str(int(time.time() * 1000)),
            'ver': '1',
            'ssl': '1',
            'referer': url,
            't': str(int(time.time() * 1000))
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15',
            'Referer': url,
            'Origin': 'https://www.56.com'
        }
        
        print(f"Setup 4 [{time.strftime('%Y-%m-%d %H:%M:%S')}] - 发送API请求获取视频信息...")
        response = requests.get(api_url, params=params, headers=headers, verify=False)
        response.raise_for_status()
        return response.json()
        
    except Exception as e:
        print(f"\nSetup Error [{time.strftime('%Y-%m-%d %H:%M:%S')}] - 获取视频信息失败: {str(e)}")
        return None

def get_real_video_url(video_url):
    """获取真实视频地址"""
    try:
        print(f"\nSetup 5 [{time.strftime('%Y-%m-%d %H:%M:%S')}] - 开始获取真实视频地址...")
        print(f"请求地址: {video_url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': 'https://www.56.com/',
        }
        
        response = requests.get(video_url, headers=headers, verify=False)
        data = response.json()
        # print("\nJSON响应:", json.dumps(data, indent=2, ensure_ascii=False))
        
        if 'servers' in data and len(data['servers']) > 0:
            real_url = data['servers'][0]['url']
            print(f"Setup 5.1 [{time.strftime('%Y-%m-%d %H:%M:%S')}] - 成功获取真实下载地址")
            print(f"下载地址: {real_url}")
            return real_url
            
        raise Exception("无法从响应中获取视频URL")
        
    except Exception as e:
        print(f"\nSetup Error [{time.strftime('%Y-%m-%d %H:%M:%S')}] - 获取真实视频地址失败: {str(e)}")
        return None

def download_video(video_url, save_path='video.mp4'):
    """下载视频"""
    try:
        real_url = get_real_video_url(video_url)
        if not real_url:
            return False
            
        print(f"\nSetup 6 [{time.strftime('%Y-%m-%d %H:%M:%S')}] - 准备下载参数...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Range': 'bytes=0-',
            'Referer': 'https://www.56.com/',
        }
        
        print(f"\nSetup 7 [{time.strftime('%Y-%m-%d %H:%M:%S')}] - 开始下载文件...")
        with requests.get(real_url, headers=headers, stream=True, verify=False, timeout=30) as response:
            response.raise_for_status()
            
            file_size = int(response.headers.get('content-length', 0))
            print(f"文件大小: {file_size/1024/1024:.2f}MB")
            print(f"Content-Type: {response.headers.get('Content-Type', 'unknown')}")
            
            if file_size == 0:
                print(f"\nSetup Error [{time.strftime('%Y-%m-%d %H:%M:%S')}] - 文件大小为0，可能下载失败")
                return False
                
            print(f"\nSetup 8 [{time.strftime('%Y-%m-%d %H:%M:%S')}] - 开始写入文件...")
            with open(save_path, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        percent = (downloaded / file_size) * 100 if file_size else 0
                        print(f"\r下载进度: {percent:.2f}%", end='')
            
            print(f"\n\nSetup 9 [{time.strftime('%Y-%m-%d %H:%M:%S')}] - 下载完成!")
            return True
            
    except Exception as e:
        print(f"\nSetup Error [{time.strftime('%Y-%m-%d %H:%M:%S')}] - 下载失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("56视频下载器 v1.0.0")
    print("=" * 50)
    
    while True:
        url = input("\n请输入56视频地址(直接回车退出)：").strip()
        if not url:
            break
            
        if not url.startswith("https://www.56.com/"):
            print("错误：请输入有效的56视频地址！")
            continue
        
        # 先获取视频基本信息
        video_info = get_video_info(url)
        if not video_info:
            print("获取视频信息失败，请检查网址是否正确")
            continue
        
        try:
            # 显示视频信息
            print("\n视频信息:")
            print(f"标题: {video_info['data']['tvName']}")
            print(f"时长: {video_info['data']['totalDuration']}秒")
            
            # 显示清晰度选项
            quality_options = [
                ('1', '540P', ''),
                ('2', '720P', '_1'),
                ('3', '1080P', '_21')
            ]
            
            print("\n可用清晰度:")
            for num, name, _ in quality_options:
                print(f"{num}. {name}")
            
            # 用户选择清晰度
            choice = input("\n请选择清晰度(1-3，直接回车使用最高清晰度): ").strip()
            if choice and choice in ['1','2','3']:
                idx = int(choice)-1
                quality_type = quality_options[idx][2]
                selected_quality = quality_options[idx][1]
                # 获取指定清晰度的视频信息
                video_info = get_video_info(url, quality_type)
                if not video_info:
                    print("获取所选清晰度失败，将使用默认清晰度")
                    video_info = get_video_info(url)
                    selected_quality = '540P'
            else:
                # 默认尝试获取最高清晰度
                print("\n尝试获取1080P视频...")
                video_info = get_video_info(url, '_21')
                if video_info:
                    selected_quality = '1080P'
                else:
                    print("获取1080P失败，尝试720P...")
                    video_info = get_video_info(url, '_1')
                    if video_info:
                        selected_quality = '720P'
                    else:
                        print("获取720P失败，使用540P...")
                        video_info = get_video_info(url)
                        selected_quality = '540P'
            
            # 设置保存文件名
            title = re.sub(r'[\\/:*?"<>|]', '_', video_info['data']['tvName'])
            save_path = f"{title}_{selected_quality}.mp4"
            print(f"\n当前清晰度: {selected_quality}")
            print(f"保存路径: {os.path.abspath(save_path)}")
            
            # 下载视频
            video_url = video_info['data']['mp4PlayUrl'][0]
            success = download_video(video_url, save_path)
            
            if success:
                print(f"视频已保存到: {os.path.abspath(save_path)}")
            else:
                print("下载失败，请重试")
                
        except Exception as e:
            print(f"处理失败: {str(e)}")
            print("视频信息:", json.dumps(video_info, indent=2, ensure_ascii=False))
        
        # 询问是否继续下载
        choice = input("\n是否继续下载其他视频？(y/n): ").strip().lower()
        if choice != 'y':
            break
    
    print("\n感谢使用！再见！")

if __name__ == '__main__':
    main()