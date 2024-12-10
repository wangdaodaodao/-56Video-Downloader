# 56Video Downloader



## 实现原理

通过9个主要步骤实现视频下载：

1. Setup 1: 获取页面内容
2. Setup 2: 解析视频ID
3. Setup 3: 构造API请求
4. Setup 4: 获取视频信息
5. Setup 5: 获取真实地址
   - Setup 5.1: 解析真实下载地址
6. Setup 6: 准备下载参数
7. Setup 7: 开始下载文件
8. Setup 8: 写入文件
9. Setup 9: 完成下载

## 注意事项

- 仅供学习研究使用
- 请勿用于商业用途
- 遵守相关网站的使用条款
- 建议使用稳定的网络环境

## 版本历史

- v2.0.0 (2024-12-10)
  - 首次发布
  - 实现基本下载功能
  - 添加进度显示
  - 支持自定义保存路径

## 作者信息

- 作者：WangDaodao
- 创建时间：2024-12-10

## 许可证

MIT License




## 原理分析


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
