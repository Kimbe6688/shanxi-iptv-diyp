# -*- coding: utf-8 -*-
"""
拉取山西联通组播源 -> 按分类写成 DIYP TXT 与 M3U
输出: 山西联通DIYP.txt（DIYP 分类列表）
      山西联通DIYP.m3u（同一份列表的 M3U 版，group-title 即分类）
TXT 格式:
    分类,#genre#
    001 频道名,地址

说明:
    - 保留同一频道的全部清晰度 / 多地址（按 URL 去重），电视端可自行选择。
    - 同一分类内同名频道用罗马数字后缀区分：SD → SDⅠ、SDⅡ，比阿拉伯数字好看。
    - 「本省」「卫视」两个分类都把 山西卫视 置顶；源里没有则不强制。
"""

import re
import os
import io
import json
import base64
import urllib.request
import urllib.error
import urllib.parse

SRC = "https://raw.githubusercontent.com/sheriffcheng-gif/my-iptv/main/m3u/%E5%B1%B1%E8%A5%BF%E8%81%94%E9%80%9A.m3u"
OUT_TXT = "山西联通DIYP.txt"
OUT_M3U = "山西联通DIYP.m3u"

# 同名多源的区分后缀（罗马数字，比 1/2 好看；超过 12 路回落为数字）
ROMAN = ["Ⅰ", "Ⅱ", "Ⅲ", "Ⅳ", "Ⅴ", "Ⅵ", "Ⅶ", "Ⅷ", "Ⅸ", "Ⅹ", "Ⅺ", "Ⅻ"]

def roman(n):
    return ROMAN[n - 1] if 1 <= n <= len(ROMAN) else str(n)

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
     r"高平|右玉|左云|浑源|阳高|天镇|广灵|灵丘|大同县",             "本省"),

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

def epg_id(name):
    """生成用于匹配 EPG 的台名：去掉罗马数字与 HD/SD/4K 等清晰度后缀。
    上游 EPG 的台名形如 CCTV1、山西卫视，带后缀会一条都匹配不上。"""
    name = re.sub(r"[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫ]$", "", name)
    return re.sub(r"(2160|超清|高清|标清|8K|4K|HD|SD)+$", "", name, flags=re.I).strip() or name

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

def numbered_names(items):
    """同名多源加罗马数字后缀：山西卫视SD → 山西卫视SDⅠ、山西卫视SDⅡ。
    只有一条的保持原名；超过 12 路时后缀回落成数字。"""
    counts = {}
    for name, _ in items:
        base = re.sub(r"[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫ]$", "", name)
        counts[base] = counts.get(base, 0) + 1
    seen = {}
    out = []
    for name, _ in items:
        base = re.sub(r"[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫ]$", "", name)
        seen[base] = seen.get(base, 0) + 1
        out.append(f"{base}{roman(seen[base])}" if counts[base] > 1 else base)
    return out

# ==================== 主流程 ====================
def main():
    text = fetch_source()
    lines = text.splitlines()

    groups = {}
    seen = set()
    attrs_by_url = {}
    header = lines[0].strip() if lines and lines[0].startswith("#EXTM3U") else "#EXTM3U"

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF"):
            head, _, disp = line.partition(",")
            attrs = re.sub(r'\s*group-title="[^"]*"', "", head[len("#EXTINF:"):].strip())
            attrs = re.sub(r"^-1\s*", "", attrs).strip()
            url = ""
            if i + 1 < len(lines) and not lines[i + 1].startswith("#"):
                url = lines[i + 1].strip()
                i += 1
            disp = clean_name(disp if disp else "未知")
            if url and url not in seen:
                seen.add(url)
                attrs_by_url[url] = attrs
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

    m3u = [header]
    txt = []
    total = 0
    for g in ORDER:
        items = groups.get(g)
        if not items:
            continue
        if g == "本省":
            items.sort(key=lambda x: bensheng_key(x[0]))
        names = numbered_names(items)
        txt.append(f"{g},#genre#")
        for idx, ((name, url), disp) in enumerate(zip(items, names), start=1):
            txt.append(f"{idx:03d} {disp},{url}")
            eid = epg_id(disp)
            attrs = attrs_by_url.get(url, "")
            attrs = re.sub(r'tvg-id="[^"]*"', f'tvg-id="{eid}"', attrs).strip()
            if "tvg-id=" not in attrs:
                attrs = f'tvg-id="{eid}"'
            m3u.append(f'#EXTINF:-1 {attrs} group-title="{g}",{disp}')
            m3u.append(url)
            total += 1
        txt.append("")

    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("\n".join(txt))
    with open(OUT_M3U, "w", encoding="utf-8") as f:
        f.write("\n".join(m3u) + "\n")

    # ★ 每次更新源后同步台标（按 tvg-id）
    tvg_ids = set(re.findall(r'tvg-id="([^"]*)"', "\n".join(m3u)))
    sync_icons(tvg_ids)

    print(f"OK 共 {total} 个频道 -> {OUT_TXT} / {OUT_M3U}")
    for g in ORDER:
        if g in groups:
            print(f"  {g}: {len(groups[g])}")

# ==================== 台标同步（每次更新源后自动同步到仓库 icons/） ====================
ICONS_DIR = "icons"
MANIFEST = "icons/manifest.json"
GITHUB_API = "https://api.github.com/repos/Kimbe6688/shanxi-iptv-diyp/contents/"

def make_icon(tvg_id):
    """按 tvg-id 生成统一风格文字台标（深灰底+蓝框+白字）。"""
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new("RGB", (200, 120), (20, 23, 28))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((4, 4, 196, 116), radius=16, outline=(76, 141, 255), width=3)
    fp = None
    for p in ["C:/Windows/Fonts/msyhbd.ttc", "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
              "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"]:
        if os.path.exists(p):
            fp = p
            break
    try:
        f = ImageFont.truetype(fp, 56 if len(tvg_id) <= 4 else 40) if fp else ImageFont.load_default()
    except Exception:
        f = ImageFont.load_default()
    txt = tvg_id if len(tvg_id) <= 5 else tvg_id[:5]
    bb = d.textbbox((0, 0), txt, font=f)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    d.text(((200 - w) // 2, (120 - h) // 2 - 6), txt, font=f, fill=(255, 255, 255))
    buf = io.BytesIO()
    im.save(buf, "PNG")
    return buf.getvalue()

def gh_put(path, content_bytes, message, token):
    """通过 GitHub Contents API 写文件（存在则带 sha 更新）。"""
    url = GITHUB_API + urllib.parse.quote(path)
    payload = {"message": message, "branch": "main",
               "content": base64.b64encode(content_bytes).decode()}
    try:
        req = urllib.request.Request(url, headers={"Authorization": f"token {token}",
                                                   "Accept": "application/vnd.github+json"})
        old = json.loads(urllib.request.urlopen(req, timeout=20).read().decode())
        payload["sha"] = old["sha"]
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, method="PUT",
                                 headers={"Authorization": f"token {token}",
                                          "Accept": "application/vnd.github+json",
                                          "Content-Type": "application/json"})
    return urllib.request.urlopen(req, timeout=30).read().decode()

def sync_icons(tvg_ids):
    """每次更新源后：缺的图标生成并上传，manifest 记录 tvg-id -> 文件名。"""
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print("[warn] 未配置 GITHUB_TOKEN，跳过台标同步")
        return
    import pathlib
    pathlib.Path(ICONS_DIR).mkdir(exist_ok=True)
    manifest = {}
    try:
        req = urllib.request.Request(GITHUB_API + urllib.parse.quote(MANIFEST),
                                     headers={"Authorization": f"token {token}",
                                              "Accept": "application/vnd.github+json"})
        old = json.loads(urllib.request.urlopen(req, timeout=20).read().decode())
        manifest = json.loads(base64.b64decode(old["content"]).decode("utf-8"))
    except Exception:
        pass
    added = 0
    for tid in sorted(tvg_ids):
        if not tid:
            continue
        fn = re.sub(r'[\\/:*?"<>|]', "_", tid) + ".png"
        if fn in manifest.values():
            continue
        try:
            gh_put(f"{ICONS_DIR}/{fn}", make_icon(tid), f"icon: {tid}", token)
            manifest[tid] = fn
            added += 1
        except Exception as e:
            print(f"[warn] 图标上传失败 {tid}: {e}")
    if added or not manifest:
        gh_put(MANIFEST, json.dumps(manifest, ensure_ascii=False, indent=1).encode("utf-8"),
               f"icons manifest: {len(manifest)}", token)
    print(f"[icons] 台标同步完成：新增 {added}，共 {len(manifest)}")

if __name__ == "__main__":
    main()
