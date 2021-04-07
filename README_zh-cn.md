[English](./README.md) | 简体中文

# genshinstats
该项目旨在成为原神的[bbs.mihoyo.com](https://bbs.mihoyo.com/ys/) api的包装。
此项目中使用的api端点尚未公开，但可以免费用于第三方工具，因此，我决定通过为它们进行包装来使其更加公开。

您可以使用[PyPI](https://pypi.org/project/genshinstats/)进行pip安装

# 如何使用
导入`genshinstats`模块，并将cookie设置为登录。
要设置cookie，请使用`set_cookie(account_id=..., cookie_token=...)`。
在此字段中传递您自己的Cookie值。（[如何获取您的cookie](#如何获取您的cookie)）
Cookie是必填项，如果缺少，则会引发错误。

所有功能均已记录在案，并提示了类型。

[API文档 (english!)](https://thesadru.github.io/pdoc/genshinstats/)
# 例子
用法的简单示例：
```py
import genshinstats as gs # 导入模块
gs.set_cookie(account_id=119480035, cookie_token="hEIIh08ghAIlHY1QQZBnsngVWXzaEMQtrSV0Bowu") # 登录

uid = 710785423
user_info = gs.get_user_info(uid) # 使用uid获取用户信息
total_characters = len(user_info['characters']) # 获取字符数
print('user "sadru" has a total of',total_characters,'characters')
```
> Cookies应该是您自己的。这些只是帐户中可以随时删除的一些示例Cookie。
```py
stats = gs.get_user_info(uid)['stats']
for field,value in stats.items():
    print(f"{field.replace('_',' ')}: {value}")
# achievements: 210
# active days: 121
# characters: 19
# ...
```

```py
characters = gs.get_all_characters(uid)
for char in characters:
    print(f"{char['rarity']}* {char['name']:10} | lvl {char['level']:2} C{char['constellation']}")
# 4* Beidou     | lvl 80 C1
# 4* Fischl     | lvl 80 C1
# 4* Bennett    | lvl 80 C2
# 5* Mona       | lvl 80 C0
# ...
```

```py
spiral_abyss = gs.get_spiral_abyss(uid,previous=True)
stats = spiral_abyss['stats']
for field,value in stats.items():
    print(f"{field.replace('_',' ')}: {value}")
# total battles: 14
# total wins: 7
# max floor: 9-1
# total stars: 18
```

可以设置带有标题的cookie
```py
gs.set_cookie_header("""
_MHYUUID=0110a95f-fbe9-41a3-a26a-5ed1d9e3a8f1; account_id=119480035; cookie_token=hEIIh08ghAIlHY1QQZBnsngVWXzaEMQtrSV0Bowu; ltoken=cnF7TiZqHAAvYqgCBoSPx5EjwezOh1ZHoqSHf7dT; ltuid=119480035; mi18nLang=en-us
""")
```
或通过从浏览器获取它们来自动设置它们
```py
gs.set_cookie_auto() # 搜索所有浏览器
gs.set_cookie_auto('chrome') # 搜索特定的浏览器
```
>需要`cookie-browser3`，最多可能需要10s
##子模块
### gacha日志
获取您的gacha拉日志。
为此，您必须先在原神中打开历史记录/详细信息页面，
然后，脚本将自己获取所有必需的数据。
```py
types = gs.get_gacha_types() # 获取所有可能的类型
key = types[2]['key'] # name == "Character Event Wish", key == '301'
for i in gs.get_gacha_log(key): # 获取gacha日志
    print(f"{i['time']} - {i['name']} ({i['rarity']}* {i['type']})")
# 2021-03-22 09:50:12 - Razor (4* Character)
# 2021-03-22 09:50:12 - Harbinger of Dawn (3* Weapon)
# 2021-03-22 09:50:12 - Cool Steel (3* Weapon)
# 2021-03-22 09:50:12 - Emerald Orb (3* Weapon)
# ...
```
```py
# 一次获取所有gacha拉动
for i in gs.get_entire_gacha_log():
    print(f"{i['time']} - {i['name']} ({i['rarity']}* {i['type']}) [{i['gacha_type']['name']}]")
```
```py
ids = gs.get_all_gacha_ids() # 获取所有可能的gacha ID（仅统计打开的详细信息页面）
for i in ids:
    details = gs.get_gacha_details(i) 
    print(f"{details['gacha_type']} - {details['banner']}")
    print('5 stars:', ', '.join(i['name'] for i in details['r5_up_items']))
    print('4 stars:', ', '.join(i['name'] for i in details['r4_up_items']))
    print()
# Weapon Event Wish - Event Wish "Epitome Invocation"
# 5 stars: Elegy for the End, Skyward Blade
# 4 stars: The Alley Flash, Wine and Song, Favonius Greatsword, Favonius Warbow, Dragon's Bane
# ...
```
您可以通过自己设置authkey来查看其他人的历史记录：
```py
# 直接使用令牌：
gs.set_authkey("D3ZYe49SUzpDgzrt/l00n2673Zg8N/Yd9OSc7NulRHhp8EhzlEnz2ISBtKBR0fZ/DGs8...")
# 从网址获取：
gs.set_authkey(url="https://webstatic-sea.mihoyo.com/ys/event/im-service/index.html?...")
# 从自定义文件中读取：
gs.set_authkey(logfile='other_output_log.txt')
```
>由于authkey仅持续一天，因此更像是导出而不是实际使用。
### 登入
自动获得当前登录用户的每日登录奖励。
```py
info = gs.get_daily_reward_info()
print('total rewards claimed:',info['total_sign_day'])
gs.sign_in()
```

## 改变语言
某些api端点支持更改语言，您可以在此处列出它们：
```py
genshinstats.get_all_characters(...,lang='fr-fr')

gachalog.get_gacha_types(lang='fr')
gachalog.get_gacha_log(...,lang='fr')
gachalog.get_gacha_items(lang='fr-fr')
gachalog.get_gacha_details(...,lang='fr-fr')
```
>端点可以使用两种类型的值，长和短。长是`gs.get_langs()`中的默认值，短的只是`lang`的第一部分（`en-us`->`en`）。
>中文有简体和繁体选项，因此如果您使用中文，则短版本与长版本相同（`zh-cn`->`zh-cn`）

# 如何获取您的cookie
1. 转到[bbs.mihoyo.com](https://bbs.mihoyo.com/ys/)
2. 登录到您的帐户
3. 打开检查模式（开发人员工具）
4. 转到`应用程序`，`Cookies`，`https://bbs.mihoyo.com`。
5. 复制`account_id`和`cookie_token`
6. 在代码中使用`set_cookie(account_id=..., cookie_token=...)`

# 个错误
genshinstats使用自己在`genshinstats.errors`中定义的错误。

您可能会看到的最常见的是`DataNotPublic`。对于中文帐户，只有所有者才能查看自己的统计信息。

# 项目布局
```
genshinstats.py     用户统计信息和字符
hoyolab.py          用户hoyolab社区信息
gachalog.py         历史gacha
signin.py           自动登录hoyolabs
errors.py           错误genshinstats使用的
```

# 关于这个项目
## 贡献
只要是干净的PR形式，我们都欢迎所有贡献。
当前正在寻找拥有中文genshin帐户的人，以帮助我使该项目适用于所有中文端点（目前主要是猜测）。
## 记入
该项目可以免费下载和分发。
功劳受到赞赏。