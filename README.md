# 山西联通 IPTV 订阅源

把 [sheriffcheng-gif/my-iptv](https://github.com/sheriffcheng-gif/my-iptv) 的山西联通组播源，整理成**带分类的 M3U 主文件**与 **DIYP TXT 备选**。两个文件由同一次 GitHub Actions 构建生成，无需本地设备常开。

## 订阅地址

VsTV、DIYP 影音等播放器是「空壳 APP」，本身不带频道，需在设置里填一个订阅地址。**以下二选一，不要同时填。**

### M3U（推荐：带分类、台标与 EPG）

本仓库生成，按「本省 / 央视 / 影院 / 4K / 卫视 / 其他」用 `group-title` 分组，保留上游的台标与 EPG 节目单。标准 M3U，支持 M3U 的播放器都能订阅。

```
https://cdn.jsdelivr.net/gh/Kimbe6688/shanxi-iptv-diyp@main/山西联通DIYP.m3u
```

### TXT（备选：DIYP 分类列表）

同一份频道列表的 DIYP 版本，`分类名,#genre#` 分组、三位序号，逗号后就是播放地址，**不需要再另填 M3U**。

```
https://cdn.jsdelivr.net/gh/Kimbe6688/shanxi-iptv-diyp@main/山西联通DIYP.txt
```

### 等价地址（编码 / 加速 / 备用）

内容完全相同，按需替换。GitHub Proxy 的规则是在原地址前加 `https://gh-proxy.com/` 前缀，**M3U 和 TXT 都适用**。

**M3U**

- 编码版（播放器不认中文路径）：

```
https://cdn.jsdelivr.net/gh/Kimbe6688/shanxi-iptv-diyp@main/%E5%B1%B1%E8%A5%BF%E8%81%94%E9%80%9ADIYP.m3u
```

- GitHub Proxy 加速 / raw 备用（jsDelivr 缓存未刷新时用 raw）：

```
https://gh-proxy.com/https://raw.githubusercontent.com/Kimbe6688/shanxi-iptv-diyp/main/%E5%B1%B1%E8%A5%BF%E8%81%94%E9%80%9ADIYP.m3u
```

```
https://raw.githubusercontent.com/Kimbe6688/shanxi-iptv-diyp/main/%E5%B1%B1%E8%A5%BF%E8%81%94%E9%80%9ADIYP.m3u
```

**TXT**

- 编码版（播放器不认中文路径）：

```
https://cdn.jsdelivr.net/gh/Kimbe6688/shanxi-iptv-diyp@main/%E5%B1%B1%E8%A5%BF%E8%81%94%E9%80%9ADIYP.txt
```

- GitHub Proxy 加速 / raw 备用：

```
https://gh-proxy.com/https://raw.githubusercontent.com/Kimbe6688/shanxi-iptv-diyp/main/%E5%B1%B1%E8%A5%BF%E8%81%94%E9%80%9ADIYP.txt
```

```
https://raw.githubusercontent.com/Kimbe6688/shanxi-iptv-diyp/main/%E5%B1%B1%E8%A5%BF%E8%81%94%E9%80%9ADIYP.txt
```

## 节目列表格式

订阅地址返回的真实片段（TXT 版；M3U 版用 `group-title="分类名"` 表达同样的分组）：

```
本省,#genre#
001 山西卫视HD,http://61.134.254.2:9003/rtp/226.0.2.152:9128
002 山西卫视SD,http://61.134.254.2:9003/rtp/226.0.2.11:8000
003 山西卫视SD,http://61.134.254.2:9003/rtp/226.0.2.189:9424
004 山西黄河HD,http://61.134.254.2:9003/rtp/226.0.2.235:9792

卫视,#genre#
001 山西卫视HD,http://61.134.254.2:9003/rtp/226.0.2.152:9128
002 重庆卫视HD,http://61.134.254.2:9003/rtp/226.0.2.174:9304
```

- `分类名,#genre#` 是分组标题，输出顺序固定：**本省 → 央视 → 影院 → 4K → 卫视 → 其他**
- `001 频道名,http://地址`：三位序号在分类内自动编号，逗号后即实际直播源

### 为什么有多个「山西卫视」

上游同一频道常有多路地址与 HD/SD 清晰度，本仓库按 URL 去重后**全部保留为独立条目**，不合并成播放器内部的隐藏备用源。这是为老人操作考虑：DIYP 通常把备用源藏在同一频道名下，要按左右键或进菜单才能切换——年轻人会这么找，老人不会；做成列表里看得见、点得到的独立频道，卡顿时按一下下一条就是另一路，不用记操作。名称保持原样，不编号、不合并。「本省」和「卫视」两处都把山西卫视置顶同理；上游无此频道时自动跳过。

## 更新机制

**Q：上游源更新了，我填的地址会跟着更新吗？** 会。填的是订阅 URL，播放器每次刷新都会重新拉取，不用换地址、不用重新导入。M3U 和 TXT 由本仓库**同一次构建一起生成**，因此都要等下一次构建（每 12 小时）才拿到新一轮的频道与播放地址。

GitHub Actions 的 `cron` **一律按 UTC**。上游声明每天 UTC 00:00 / 12:00 更新，本仓库延后 5 分钟构建：

| 上游更新（UTC） | = 北京时间 | 本仓库构建（UTC） | = 北京时间 |
| --- | --- | --- | --- |
| 00:00 | 早上 08:00 | 00:05 | 早上 08:05 |
| 12:00 | 晚上 20:00 | 12:05 | 晚上 20:05 |

即「12 点」是 UTC 的中午，对应北京**晚上 8 点**，不是北京时间的中午 12 点。

- 构建流程：拉取上游 M3U（raw → gh-proxy → ghfast 兜底）→ 分类 → 同时写出 TXT 与 M3U → 提交回仓库；内容无变化不提交，`concurrency` 防止并发冲突
- 上游定时任务实际常延迟数小时，因此「+5 分钟」只是配置对齐，可能取到上一轮的源，下一次构建补上
- jsDelivr 有缓存，刚更新完可能稍晚才刷出，急用可取 raw 地址

手动触发：仓库 → `Actions` → `build-diyp-txt` → `Run workflow`

## 分类规则

匹配优先级（先匹配先生效，与输出顺序是两回事）：

| 优先级 | 分类 | 关键词 |
| --- | --- | --- |
| 1 | 4K | 4K / 2160 / 超清 / 8K |
| 2 | 影院 | CHC / 电影 / 剧场 / HBO / 风云 … |
| 3 | 央视 | CCTV / 央视 / CGTN / 中国教育 … |
| 4 | 本省 | 山西 / 黄河 / 太原、大同、临汾等各地市县名 … |
| 5 | 卫视 | 卫视 |
| 6 | 其他 | 以上都不匹配 |

- 「本省」按 山西卫视 → 山西黄河 → 山西经济与科技 → 山西影视 → 山西社会与法治 → 山西文体生活 优先排序，其余按名称
- 「卫视」同样置顶山西卫视；播放地址按 URL 去重，唯一例外是该频道在两个分类各放一次（同一路高清源）

## 使用条件

- 组播源经 HTTP 代理转出，**一般需在山西联通宽带网络内使用**，其他网络可能无法播放
- 本仓库只整理频道列表，不托管直播流，不保证源的可用性；频道数量随上游变化，以订阅地址返回的内容为准

## 致谢

直播源来自 [sheriffcheng-gif/my-iptv](https://github.com/sheriffcheng-gif/my-iptv)，本仓库仅做分类整理。
