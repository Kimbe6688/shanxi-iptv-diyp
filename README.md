# 山西联通 DIYP 频道列表

把 [sheriffcheng-gif/my-iptv](https://github.com/sheriffcheng-gif/my-iptv) 的山西联通组播源，自动整理成 **DIYP 影音 / 电视端可直接订阅的分类频道列表**。

- 全自动：GitHub Actions 定时构建，不需要电脑或 NAS 常开
- 自动分类、自动编号；保留同一频道的全部清晰度 / 多路源，左右键可逐路切换
- 「本省」和「卫视」两个分类都把 山西卫视 置顶（上游没有该频道时自动跳过）

## 📺 订阅地址

**在播放器里只需要填这一个地址**（下面两种写法等价，任选其一）：

```
https://cdn.jsdelivr.net/gh/Kimbe6688/shanxi-iptv-diyp@main/山西联通DIYP.txt
```

```
https://cdn.jsdelivr.net/gh/Kimbe6688/shanxi-iptv-diyp@main/%E5%B1%B1%E8%A5%BF%E8%81%94%E9%80%9ADIYP.txt
```

第二种是中文路径的 URL 编码版，个别播放器不认中文路径时用它。

**备用地址**（jsDelivr 缓存未刷新或访问慢时）：

```
https://raw.githubusercontent.com/Kimbe6688/shanxi-iptv-diyp/main/%E5%B1%B1%E8%A5%BF%E8%81%94%E9%80%9ADIYP.txt
```

GitHub 访问慢可加代理前缀：

```
https://gh-proxy.com/https://raw.githubusercontent.com/Kimbe6688/shanxi-iptv-diyp/main/%E5%B1%B1%E8%A5%BF%E8%81%94%E9%80%9ADIYP.txt
```

> ⚠️ **只需要填上面的 TXT 订阅地址，不需要再填 M3U，也不需要填上游项目地址。**
> 本仓库的 TXT 本身就是完整节目源：每行 `001 频道名,http://地址`，逗号后就是该频道的实际播放地址。
> 播放器读这一个 URL 就会同时拿到频道列表和直播源；分类只是把这些行重新排序、编号。

## 📂 文件格式

```
本省,#genre#
001 山西卫视HD,http://61.134.254.2:9003/rtp/226.0.2.152:9128
002 山西卫视SD,http://61.134.254.2:9003/rtp/...
003 山西卫视SD,http://61.134.254.2:9003/rtp/...

卫视,#genre#
001 山西卫视HD,http://...
...
```

- 输出顺序固定：**本省 → 央视 → 影院 → 4K → 卫视 → 其他**
- 频道名带三位序号，同分类内从 `001` 自动编号
- 地址按 URL 去重；同一频道的 HD / SD 多路源**全部保留**，在电视上是彼此独立的条目，方便左右切换

## 🔄 更新机制

- 上游 `my-iptv` 每天 UTC 00:00 / 12:00 各更新一次
- 本仓库在**其后 5 分钟**（UTC 00:05 / 12:05，北京时间 08:05 / 20:05）自动构建
- 流程：拉取上游 M3U（raw → gh-proxy → ghfast 三重兜底）→ 按规则分类 → 写出 TXT → 提交回本仓库
- TXT 内容没变化时不产生提交；`concurrency` 保证同一时间只跑一个构建

> ⚠️ 上游的 GitHub Actions 定时任务实际常有数小时延迟，因此偶尔会取到上一轮数据，下一次构建会自动追上。

## 🗂️ 分类规则

匹配优先级（先匹配先生效）：

| 顺序 | 分类 | 关键词 |
| --- | --- | --- |
| 1 | 4K | 4K / 2160 / 超清 / 8K |
| 2 | 影院 | CHC / 电影 / 剧场 / HBO / 风云 … |
| 3 | 央视 | CCTV / 央视 / CGTN / 中国教育 … |
| 4 | 本省 | 山西 / 黄河 / 太原、大同、临汾等各地市县名 … |
| 5 | 卫视 | 卫视 |
| 6 | 其他 | 以上都不匹配 |

「本省」按 山西卫视 → 山西黄河 → 山西经济与科技 → 山西影视 → 山西社会与法治 → 山西文体生活 优先排序，其余按名称顺序。

当前共 **185** 个频道条目：本省 30 / 央视 35 / 影院 15 / 4K 9 / 卫视 57 / 其他 39（数量随上游变化）。

## 🔧 手动触发更新

仓库页面 → `Actions` → `build-diyp-txt` → `Run workflow` → `Run workflow`

## 📝 说明

- 播放地址来自上游的运营商组播源（经 HTTP 代理转出），**一般需要在山西联通宽带网络内使用**；其他运营商或外网环境可能无法播放。
- 本仓库只做频道整理，不托管、不提供任何直播流，也不保证源的可用性。
- jsDelivr 有缓存，刚更新完可能稍等才刷新；想立刻拿最新可改用 raw 地址。

## 🙏 致谢

- 直播源：[sheriffcheng-gif/my-iptv](https://github.com/sheriffcheng-gif/my-iptv)
- 组播源抓取思路：[cqshushu](https://blog.cqshushu.com/multicast-iptv)、[jia070310/4K-IPTV-M3U](https://github.com/jia070310/4K-IPTV-M3U)
