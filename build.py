# -*- coding: utf-8 -*-
"""
拉取山西联通组播源 -> 按 DIYP 分类写成 TXT
输出: 山西联通DIYP.txt  (格式: 分类,#genre#  +  序号 频道名,地址)
"""
import re
import urllib.request

SRC = "https://raw.githubusercontent.com/sheriffcheng-gif/my-iptv/main/m3u/%E5%B1%B1%E8%A5%BF%E8%81%94%E9%80%9A.m3u"
OUT = "山西联通DIYP.txt"

# ============ 分类规则（按你机顶盒截图：本省/央视/影院/4K/卫视/其他）============
# 顺序即优先级，先匹配到的先生效
RULES = [
    # 4K：先挑出来，避免被“卫视/央视”抢走
    (r"4K|4k|2160|超清",                              "4K"),

    # 影院：电影/付费轮播/剧场/专题
    (r"CHC|家庭影院|影迷|动作电影|剧场|电影|院线|HBO",      "影院"),

    # 央视：CCTV 全系 + CGTN + 中国教育
    (r"CCTV|央视|CGTN|中国教育|央广",                    "央视"),

    # 卫视：省级卫视（含 4K 卫视已在上面被挑走）
    (r"卫视",                                          "卫视"),

    # 本省：山西本地 + 地市 + 矿区企业台
    (r"山西|黄河|太原|大同|临汾|运城|晋中|忻州|阳泉|长治|晋城|朔州|吕梁|"
     r"清徐|古交|阳曲|娄烦|平定|盂县|潞州|襄垣|屯留|黎城|武乡|长钢|晋能|霍州|"
     r"昔阳|寿阳|灵石|稷山|孝义|汾阳|介休|河津|永济|高平|怀仁|山阴|应县|"
     r"优购物|购物",                                    "本省"),
]

# 序号缩进：让 DIYP 显示成 001 002 003 的样子
def classify(name):
    for pat, grp in RULES:
        if re.search(pat, name):
            return grp
    return "其他"

def clean(name):
    """清掉名字里的多余标记，避免分类错乱"""
    name = re.sub(r"[（(]\s*(vip|VIP|标清|高清|HD|SD)\s*[)）]", "", name)
    return name.strip()

def main():
    req = urllib.request.Request(SRC, headers={"User-Agent": "Mozilla/5.0"})
    text = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")

    lines = text.splitlines()
    groups = {}          # 分类 -> [(序号, 频道名, 地址)]
    seen = set()
    idx = 0

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF"):
            disp = line.split(",", 1)[1] if "," in line else "未知"
            # 下一行是地址
            url = ""
            if i + 1 < len(lines) and not lines[i + 1].startswith("#"):
                url = lines[i + 1].strip()
                i += 1
            disp = clean(disp)
            if not url or url in seen:
                i += 1
                continue
            seen.add(url)
            idx += 1
            groups.setdefault(classify(disp), []).append((idx, disp, url))
        i += 1

    # 按你机顶盒的顺序输出
    order = ["本省", "央视", "影院", "4K", "卫视", "其他"]
    out = []
    for g in order:
        items = groups.get(g)
        if not items:
            continue
        out.append(f"{g},#genre#")
        for num, name, url in items:
            out.append(f"{num:03d} {name},{url}")
        out.append("")   # 分类之间空一行，DIYP 更稳

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(out))

    total = sum(len(v) for v in groups.values())
    print(f"OK 共 {total} 个频道")
    for g in order:
        if g in groups:
            print(f"  {g}: {len(groups[g])}")

if __name__ == "__main__":
    main()
