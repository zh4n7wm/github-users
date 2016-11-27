## 获取Github用户

根据 location, language 获取github用户信息，并用网页简单显示。

find-users.py使用:

  $ python find-users.py -p chengdu
  $ python find-users.py -p 成都 chengdu 北京 beijing -l Python PHP

merge-json.py使用:

  $ python merge-json.py -i chengdu.json 成都.json -o chengdu.json

## 问题

### 根据某项条件搜索后，只能从github上获取100页数据

这应该是github的限制。

### 不能边抓取边保存

不能边抓取边保存，一个json没有抓取完时出现网络问题会导致已经抓取的部分数据丢失；同时会浪费内存。

### 汉字、拼音要同时输入

本来希望只输入汉字，然后将汉字转换为拼音，然后自动搜索，减少手动输入拼音。
但，目前的pinyin module对多音字处理不理想。

### 前端没做分页

如题。

## 感谢

`index.html`是基于[@c9s/github-taiwan](http://github.com/c9s/github-taiwan)修改的。
