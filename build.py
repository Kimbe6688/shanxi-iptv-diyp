# -*- coding: utf-8 -*-
"""
拉取山西联通组播源 -> 按 DIYP 分类写成 TXT
输出: 山西联通DIYP.txt
格式:
    分类,#genre#
    001 频道名,地址

说明:
    - 保留同一频道的全部清晰度 / 多地址（按 URL 去重），电视端可自行选择。
    - 「本省」「卫视」两个分类都把 山西卫视 置顶；源里没有则不强制。
"""

import re
import urllib.request

SRC = "https://raw.githubusercontent.com/sheriffcheng-gif/my-iptv/main/m3u/%E5%B1%B1%E8%A5%BF%E8%81%94%E9%80%9A.m3u"
OUT = "山西联通DIYP.txt"

# ==================== 分类规则 ====================
# 顺序即优先级：先匹配到的先生效
RULES = [
    (r"4K|4k|2160|超清|8K",                                   "4K"),

    (r"CHC|家庭影院|影迷|动作电影|剧场|电影|院线|HBO|"
     r"风云|金鹰|动漫秀场|都市剧场|海外剧场|早期教育|第一剧场",        "影院"),

    (r"CCTV|央视|CGTN|中国教育|央广|中国气象|央视台球",              "央视"),

    (r"山西|黄河|太原|大同|临汾|运城|晋中|忻州|阳泉|长治|晋城|朔州|吕梁|"
     r"清徐|古交|阳曲|娄烦|平定|盂县|潞州|襄垣|屯留|黎城|武乡|长钢|晋能|霍州|"
     r"昔阳|寿阳|灵石|稷山|孝义|汾阳|介休|河津|永济|高平|怀仁|山阴|应县|"
     r"长子|壶关|平顺|沁县|沁源|左权|和顺|榆社|太谷|祁县|平遥|交城|文水|"
     r"岚县|兴县|临县|柳林|石楼|交口|中阳|方山|孝义|交口|蒲县|大宁|隰县|"
     r"永和|乡宁|吉县|襄汾|曲沃|翼城|浮山|洪洞|安泽|古县|汾西|侯马|霍州|"
     r"新绛|闻喜|夏县|绛县|平陆|芮城|万荣|河津|稷山|沁水|阳城|陵川|泽州|"
     r"高平|右玉|左云|浑源|阳高|天镇|广灵|灵丘|大同县|"
     r"优购物|购物|好享购|快乐购",                                "本省"),

    (r"卫视",                                                  "卫视"),
]

ORDER = ["本省", "央视", "影院", "4K", "卫视", "其他"]

# ==================== 本省排序 ====================
BENSHENG_PRIORITY = [
    ("山西卫视", 0),
    ("山西黄河", 1),
    ("山西经济与科技", 2),
    ("经济与科技", 2),
    ("山西影视", 3),
    ("山西社会与法治", 4),
    ("社会与法治", 4),
    ("山西文体生活", 5),
    ("文体生活", 5),
]

def bensheng_key(name):
    for kw, rank in BENSHENG_PRIORITY:
        if kw in name:
            return rank
    return 99

# ==================== 工具 ====================
def classify(name):
    for pat, grp in RULES:
        if re.search(pat, name):
            return grp
    return "其他"

def clean_name(name):
    name = re.sub(r"[（(]\s*(vip|VIP|标清|高清|HD|SD|超清)\s*[)）]", "", name)
    name = re.sub(r"\s+", " ", name)
    return name.strip()

def fetch_source():
    mirrors = [SRC, "https://gh-proxy.com/" + SRC, "https://ghfast.top/" + SRC]
    for url in mirrors:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
        except Exception as e:
            print(f"[warn] 失败: {url} -> {e}")
    raise RuntimeError("所有镜像都拉不通")

def pick_hd(items):
    """同一频道优先取高清 / 4K 的一条"""
    return next((x for x in items if re.search(r"4K|8K|2160|超清|HD|高清", x[0], re.I)), items[0])

# ==================== 主流程 ====================
def main():
    text = fetch_source()
    lines = text.splitlines()

    groups = {}
    seen = set()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF"):
            disp = line.split(",", 1)[1] if "," in line else "未知"
            url = ""
            if i + 1 < len(lines) and not lines[i + 1].startswith("#"):
                url = lines[i + 1].strip()
                i += 1
            disp = clean_name(disp)
            if url and url not in seen:
                seen.add(url)
                groups.setdefault(classify(disp), []).append((disp, url))
        i += 1

    # 「卫视」分类也把 山西卫视 置顶：从本省复制一条（优先高清）。
    # 源里没有山西卫视时自然跳过，不硬塞。
    wx = groups.get("卫视")
    bs = groups.get("本省")
    if wx is not None and bs:
        sx = [x for x in bs if "山西卫视" in x[0]]
        if sx:
            wx[:] = [x for x in wx if "山西卫视" not in x[0]]
            wx.insert(0, pick_hd(sx))

    out = []
    total = 0
    for g in ORDER:
        items = groups.get(g)
        if not items:
            continue
        if g == "本省":
            items.sort(key=lambda x: bensheng_key(x[0]))
        out.append(f"{g},#genre#")
        for idx, (name, url) in enumerate(items, start=1):
            out.append(f"{idx:03d} {name},{url}")
            total += 1
        out.append("")

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(out))

    print(f"OK 共 {total} 个频道")
    for g in ORDER:
        if g in groups:
            print(f"  {g}: {len(groups[g])}")

if __name__ == "__main__":
    main()
