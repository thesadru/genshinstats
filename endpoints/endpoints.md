
# hoyolab
## officialRecommendedPosts
https://api-os-community.hoyolab.comcommunityos/forum/home/officialRecommendedPosts?gids=2
Hoyolab reommended offical posts
## hotTopicList
https://api-os-community.hoyolab.com/communityos/forum/topic/hotTopicList?gids=2&page_size=17
Hoyolab hot topics
page_size: int <=17
## getUserGameRolesByCookie
https://api-os-takumi.hoyolab.com/binding/api/getUserGameRolesByCookie?game_biz=hk4e_global&region=os_euro
User uids with the cookie
## forumMain
https://bbs-api-os.hoyolab.com/community/apihub/api/forumMain?forum_id=1&gids=2&lang=en-us
main page of forum
forum_id: int 1-4
## querySignInStatus
https://bbs-api-os.hoyolab.com/community/apihub/api/querySignInStatus?gids=2
???
## webHome
https://bbs-api-os.hoyolab.com/community/apihub/wapi/webHome?gids=2
???
## emoticon_set
https://bbs-api-os.hoyolab.com/community/misc/api/emoticon_set
list of emoticons
## langs
https://bbs-api-os.hoyolab.com/community/misc/wapi/langs
list of languages
## getUserGameUnreadCount
https://bbs-api-os.hoyolab.com/community/notification/wapi/getUserGameUnreadCount
User's unread messages
## getNewsList
https://bbs-api-os.hoyolab.com/community/post/wapi/getNewsList?gids=2&page_size=20&type=3
list of news
page_size: int <=20
type: int 1-3
## posts
https://bbs-api-os.hoyolab.com/community/post/wapi/homepage/posts?page_size=20
new posts
page_size: int <=20
## allTops
https://bbs-api-os.hoyolab.com/community/post/wapi/mainpage/allTops?gids=2&page_size=2000
all new top posts
page_size: int <=20
## getUnreadInfo
https://bbs-api-os.hoyolab.com/community/timeline/wapi/getUnreadInfo
amount of unread messages
## getUserFullInfo
https://bbs-api-os.hoyolab.com/community/user/wapi/getUserFullInfo?uid=8366222
Gets community info about a user
uid: int: community uid
## recommendActive
https://bbs-api-os.hoyolab.com/community/user/wapi/recommendActive?page_size=195
Recommended active users
page_size: int <=195
## getContentList
https://genshin.mihoyo.com/content/yuanshen/getContentList?pageSize=4&pageNum=1&channelId=96
some content list
pageSize: int
pageNum: int
channelId: int: ???

# battle chronicle
needs ds
## existsGameRecordCard
https://bbs-api-os.hoyolab.com/game_record/card/wapi/existsGameRecordCard
whether a game record card exists
## getGameRecordCard
https://bbs-api-os.hoyolab.com/game_record/card/wapi/getGameRecordCard&uid=8366222
game record card
uid: int: user's community uid
## character
https://bbs-api-os.hoyolab.com/game_record/genshin/api/character
Gets a list of user's characters
POST
character_ids; int[]: list of character ids
role_id: int: user's uid
server: server
## index
https://bbs-api-os.hoyolab.com/game_record/genshin/api/index?server=os_euro&role_id=710785423
user info
role_id: int: user's uid
server: server
## spiralAbyss
https://bbs-api-os.hoyolab.com/game_record/genshin/api/spiralAbyss?server=os_euro&role_id=710785423&schedule_type=1
spiral abyss runs
role_id: int: user's uid
server: server
schedule_type: int 1/2: current or previous
## tool
https://bbs-api-os.hoyolab.com/game_record/genshin/api/tool
some tool ???

# hoyolab events
## sol/info
https://hk4e-api-os.hoyolab.com/event/sol/info?act_id=e202102251931481&lang=en
info about the login event
act_id: str: event id (e202102251931481 = login event)
## sol/award
https://hk4e-api-os.mihoyo.com/event/sol/award?current_page=1&page_size=10&act_id=e202102251931481&lang=en
awards gotten from the login event
current_page: int
page_size: int
act_id: str: event id (e202102251931481 = login event)
## getRoleByAidAndRegion
https://hk4e-api-os.mihoyo.com/common/apicdkey/api/getRoleByAidAndRegion?lang=en&region=os_euro&game_biz=hk4e_global
game uid gotten with region and game_biz

# mihoyo stuff
## webExchangeCdkey
https://hk4e-api-os.mihoyo.com/common/apicdkey/api/webExchangeCdkey?uid=710785423&region=os_euro&lang=en&cdkey=a&game_biz=hk4e_global
gift code redeem
uid: int: game uid
cdkey: str: code
## fetch_cookie_accountinfo
https://webapi-os.account.mihoyo.com/Api/fetch_cookie_accountinfo
info about account logged in

# gacha
## getConfigList
https://hk4e-api.mihoyo.com/event/gacha_info/api/getConfigList?authkey_ver=1&lang=en&authkey=...
Gets a list of gachas
## getGachaLog
https://hk4e-api.mihoyo.com/event/gacha_info/api/getGachaLog?authkey_ver=1&lang=en&authkey=...&gacha_type=301&page=1&size=20
gets a gacha log
## gacha_info
https://webstatic-sea.mihoyo.com/hk4e/gacha_info/os_asia/d610857102f9256ba143ccf2e03b964c76a6ed/en-us.json
server: str: server
gacha_id: str: gacha id
lang: str: language
