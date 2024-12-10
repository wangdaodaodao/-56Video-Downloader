#!/usr/bin/env python
# -*- coding: utf-8 -*-



# """
# 56视频下载器 - 基于日志分析下载56网站视频
# 作者: WangDaodao
# 版本: 1.0.0
# 创建时间: 22024-12-10 11:36:12
# """


"""
56视频下载器 - 基于日志分析

从日志分析得到的关键信息：
1. 视频基本信息:
   - vid: 568221730
   - 标题: "四川发现'白色石油'，是21世纪的战略资源，各国请求中国合作"
   - 分辨率: 1280x720
   - 文件大小: 3434089 bytes
   - 视频时长: 46秒

2. URL请求链路:
   第一层: https://my.tv.sohu.com/play/videonew.do (获取视频基本信息)
   第二层: https://data.vod.itc.cn/ip?k=xxx&a=xxx (获取CDN分发信息)
   第三层: https://696-18.vod.tv.itc.cn/sohu/v1/xxx.mp4 (最终的视频文件地址)

3. 关键请求参数:
   - uid: 17337985981841145515 (用户标识)
   - ver: 1 (接口版本)
   - ssl: 1 (使用HTTPS)
   - referer: https://www.56.com/u37/v_MTkxMDg4MjQy.html (防盗链)

4. CDN分发信息:
   - allot: data.vod.itc.cn (CDN域名)
   - nid: 696 (节点ID)
   - isp2p: 1 (是否支持P2P)

下载流程说明：
1. 通过搜狐视频API获取视频信息
2. 解析返回数据获取中间URL
3. 访问中间URL获取真实的CDN视频地址
4. 使用流式下载保存视频文件
"""

import requests
import json
import time
import os
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # 禁用SSL警告

def get_video_info():
    """
    获取视频信息
    通过搜狐视频API获取56视频的详细信息
    从日志分析可知56视频实际是托管在搜狐视频平台上
    """
    # 搜狐视频API地址
    api_url = "https://my.tv.sohu.com/play/videonew.do"
    # 56视频原始页面地址
    video_page_url = "https://www.56.com/u37/v_MTkxMDg4MjQy.html"
    
    # API请求参数
    params = {
        'vid': '568221730',  # 视频ID，从原始URL中提取
        'uid': '17337985981841145515',  # 用户ID，可以是随机值
        'ver': '1',  # API版本
        'ssl': '1',  # 使用HTTPS
        'referer': video_page_url,  # 来源页面
        't': str(int(time.time() * 1000))  # 时间戳，防止缓存
    }
    
    # 请求头，模拟浏览器行为
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1.1 Safari/605.1.15',
        'Referer': video_page_url,  # 防盗链
        'Origin': 'https://www.56.com'  # 来源域名
    }
    
    try:
        # 发送GET请求获取视频信息
        response = requests.get(api_url, params=params, headers=headers, verify=False)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"获取视频信息失败: {str(e)}")
        return None

def get_real_video_url(video_url):
    """
    获取真实视频地址
    从日志分析发现视频URL需要两次跳转：
    1. 第一次请求返回一个中间URL(data.vod.itc.cn域名)
    2. 访问中间URL获取真实的CDN视频地址(vod.tv.itc.cn域名)
    """
    # 请求头，模拟浏览器行为
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1.1 Safari/605.1.15',
        'Accept': '*/*',
        'Accept-Encoding': 'identity;q=1, *;q=0',  # 请求未压缩的内容
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer': 'https://www.56.com/',  # 防盗链
    }
    
    try:
        # 请求中间URL获取JSON响应
        response = requests.get(video_url, headers=headers, verify=False)
        data = response.json()
        print("JSON响应:", json.dumps(data, indent=2, ensure_ascii=False))
        
        # 从返回的JSON中获取真实的视频URL
        # 格式: {"servers":[{"url":"真实视频地址"}]}
        if 'servers' in data and len(data['servers']) > 0:
            return data['servers'][0]['url']
            
        raise Exception("无法从响应中获取视频URL")
        
    except Exception as e:
        print(f"获取真实视频地址失败: {str(e)}")
        return None

def download_video(video_url, save_path='video.mp4'):
    """
    下载视频
    使用流式下载，支持显示进度条
    """
    # 请求头，模拟浏览器行为
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1.1 Safari/605.1.15',
        'Accept': '*/*',
        'Accept-Encoding': 'identity;q=1, *;q=0',  # 请求未压缩的内容
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Range': 'bytes=0-',  # 支持断点续传
        'Referer': 'https://www.56.com/',  # 防盗链
    }
    
    try:
        print(f"开始获取视频地址: {video_url}")
        
        # 获取真实视频地址
        real_url = get_real_video_url(video_url)
        if not real_url:
            return False
            
        print(f"开始下载真实地址: {real_url}")
        
        # 使用流式请求下载视频
        with requests.get(real_url, headers=headers, stream=True, verify=False, timeout=30) as response:
            response.raise_for_status()
            
            # 获取文件大小
            file_size = int(response.headers.get('content-length', 0))
            print(f"文件大小: {file_size/1024/1024:.2f}MB")
            print(f"Content-Type: {response.headers.get('Content-Type', 'unknown')}")
            
            if file_size == 0:
                print("警告: 文件大小为0，可能下载失败")
                return False
                
            # 写入文件并显示进度
            with open(save_path, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):  # 8KB缓冲区
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        percent = (downloaded / file_size) * 100 if file_size else 0
                        print(f"\r下载进度: {percent:.2f}%", end='')
            
            print("\n下载完成!")
            return True
            
    except Exception as e:
        print(f"\n下载失败: {str(e)}")
        return False

def main():
    """
    主函数
    执行完整的视频下载流程：
    1. 获取视频信息
    2. 解析视频地址
    3. 下载视频
    """
    # 1. 获取视频信息
    video_info = get_video_info()
    if not video_info:
        print("无法获取视频信息")
        return
    
    try:
        # 2. 解析视频地址(从视频信息中获取中间URL)
        video_url = video_info['data']['mp4PlayUrl'][0]
        print(f"获取到初始视频地址: {video_url}")
        
        # 3. 下载视频
        success = download_video(video_url)
        if success:
            print("视频下载成功！")
            print(f"视频保存在: {os.path.abspath('video.mp4')}")
        else:
            print("视频下载失败，请重试。")
            
    except Exception as e:
        print(f"处理失败: {str(e)}")
        print("视频信息:", json.dumps(video_info, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
    input("按回车键退出...")