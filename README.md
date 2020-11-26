# 增强百科

## 项目介绍

​		本项目解决了百科无法搜索与搜索词条相关联词条的痛点，使用scrapy爬虫框架对百度百科进行爬取，使用elasticsearch搜索服务器实现了在大规模的文本数据中快速搜索相关词条，并且使用redis缓存数据库实现了历史搜索功能，使用NER命名实体识别技术完成了对词条类别的标注，最后使用django web框架完成了项目前端的展示。

![image-20201116215356886](https://github.com/vinsssss/EnhanceBaike/blob/master/pictures/image-20201116215356886.png)

![image-20201116215410937](https://github.com/vinsssss/EnhanceBaike/blob/master/pictures/image-20201116215410937.png)

![image-20201116215432648](https://github.com/vinsssss/EnhanceBaike/blob/master/pictures/image-20201116215432648.png)

## 功能介绍

### 1. 搜索功能

​		返回百科相关词条，并对相关文本进行高亮标注，**搜索服务器约几十万条数据，搜索时间<0.1s**， 搜索结果若有直接相关词条，则第一条返回直接相关词条，其余词条按关联程度排序

### 2.历史记录功能

​		redis实现历史记录，取前10条进行展示

### 3.切换类别搜索

​		词条使用百度NER命名实体识别LAC模型进行标注，共有四种类型，人物/组织/地点/其他，并实现切换类别搜索功能，选择对应类别可以搜索相关词条

## 运行要求

1. python
2. elasticsearch
3. redis
4. scrapy
5. mongodb

## 项目目录结构

> EnhanceBaike
> 	baike_spider
> 		baike_spider 
> 			esInit
> 			spiders
> 				__init__.py
> 				baike_spider.py	百科爬虫，数据获取
> 			__init__.py
> 			es_baike.py	elasticsearch服务器初始化
> 			items.py
> 			LACManager.py	LAC模型的管理类
> 			middlewares.py
> 			pipelines.py	数据存储，存储到elasticsearch和mongodb
> 			settings.py	爬虫配置文件
> 		scrapy.cfg
> BaikeDjango	django项目
> 	__init__.py
> 	asgi.py
> 	settings.py	django配置文件
> 	urls.py	django 路由
> 	wsgi.py
> show
> 	migrations
> 	static
> 	templates	网页模板
> 		index.html	首页
> 		result.html	搜索结果呈现页
> 	__init__.py
> 	apps.py	app注册
> 	ElasticsearchManager.py	es管理类
> 	models.py	mongodb模型类，django以mongodb为后端
> 	RedisManager.py	redis管理类
> 	views.py	视图类
> manage.py	django管理

## 项目实现介绍

### 1. 爬虫部分

![image-20201116221827672](https://github.com/vinsssss/EnhanceBaike/blob/master/pictures/image-20201116221827672.png)

​		使用scrapy框架对百科网页进行爬取，先指定开始爬取词条，检索当前词条内的所有链接词条，然后再爬取链接词条，依此进行实现递归的爬取，爬取效率约10w词条/h
​		**具体细节见baike_spider.py代码，已经写好详细注释**
​		通过scrapy 框架的pipeline实现存储与爬取的异步进行，从而提升爬取效率，将生成items存入elasticsearch搜索服务器与mongodb数据库中，以便后续的数据检索。

![image-20201116222749887](https://github.com/vinsssss/EnhanceBaike/blob/master/pictures/image-20201116222749887.png)

baike_id为百科对应唯一Id，title为百科标题， name为百科词条名，type为LAC预测的词条类型，text为词条文本，page_url为百科url

### 2.搜索部分

![image-20201116223006162](https://github.com/vinsssss/EnhanceBaike/blob/master/pictures/image-20201116223006162.png)

​		搜索服务器共两个index，triples为百科信息三元组，本项目暂时用不到，baike为百科信息索引，里面维护了百科name与百科text等，搜索功能的实现依托于elasticsearch搜索服务器。

![image-20201116223220122](https://github.com/vinsssss/EnhanceBaike/blob/master/pictures/image-20201116223220122.png)

​		搜索功能实现了数十万级数据文本查询时间小于0.1s，可以按照LAC预测类别进行检索，搜索结果中有直接相关词条则第一条为直接相关词条，其余词条按照关联度进行排序。
​		**具体实现细节见ElasticsearchManager.py**

### 3.LAC标签预测部分

**本部分摘录自**  [LAC GitHub](https://github.com/baidu/lac)

LAC全称Lexical Analysis of Chinese，是百度自然语言处理部研发的一款联合的词法分析工具，实现中文分词、词性标注、专名识别等功能。该工具具有以下特点与优势：

- **效果好**：通过深度学习模型联合学习分词、词性标注、专名识别任务，整体效果F1值超过0.91，词性标注F1值超过0.94，专名识别F1值超过0.85，效果业内领先。

- **效率高**：精简模型参数，结合Paddle预测库的性能优化，CPU单线程性能达800QPS，效率业内领先。

- **可定制**：实现简单可控的干预机制，精准匹配用户词典对模型进行干预。词典支持长片段形式，使得干预更为精准。

- **调用便捷**：**支持一键安装**，同时提供了Python、Java和C++调用接口与调用示例，实现快速调用和集成。

- **支持移动端**: 定制超轻量级模型，体积仅为2M，主流千元手机单线程性能达200QPS，满足大多数移动端应用的需求，同等体积量级效果业内领先。

  ![image-20201116223812646](https://github.com/vinsssss/EnhanceBaike/blob/master/pictures/image-20201116223812646.png)

  ​														LAC模型采用双层双向GRU+CRF网络结构

GRU是LSTM网络的一种效果很好的变体，它较LSTM网络的结构更加简单，而且效果也很好，因此也是当前非常流形的一种网络。GRU既然是LSTM的变体，因此也是可以解决RNN网络中的长依赖问题。
本项目使用百度开源LAC模型，无需额外训练模型，该预测速度快，预测准确率高。

### 4.Django部分

**略**

Django 页面参考自 [mtianSearch](https://github.com/mtianyan/mtianyanSearch)

## 项目难点

### 1.搜素精准性问题

问题描述：

​		elasticsearch的原理是将文本先分词后建立倒排索引，刚开始使用的是常见的ik分词器，由于百科文本数量较多，其中涉及到的词汇也比较多，导致ik分词器无法很好的对百科的大量文本进行很恰当的分词，并且ik分词器无法实现文本的通配，即关键字匹配，从而导致索引中有许多与预期不符的词汇，在搜索展示中，会出现很多与相关搜索词汇不一致的词被高亮标注，无法达到预期的搜索准确性。

解决方案：

​		查阅各种解决方案后，决定使用自定义分词器Ngram，该分词器会对文本进行多种形式的分词，例如【123】会返回分词结果【1,2,3,12,23,123】，这样在查询时即能用123准确查到123，也可以使用12模糊查询到123，是符合项目预期的分词结果。在Ngram分词器的配置中，将min_gram设置为1，将max_gram也设置为1，从而使得中文文本按照字来进行分词，这样增加了分词结果的组合数量，从而可以更好地实现精准的搜索。

### 2.搜索速度问题

问题描述：

​		elasticsearch默认采用from+size的方式进行搜索的分页，但是这种分页方式有一种弊端，每次搜索都会查询前from+size页的数据，但是只返回了size大小的页面，也就是说浪费了from大小的页面，项目刚开始采用这种分页方式，这种方式十分浪费机器的性能，从而使得搜索速度不是很快，做过相关测试，越往后的分页，执行的效率越低。总体上会随着from的增加，消耗时间也会增加。而且数据量越大，时间增加的也就越明显。

解决方案：

​		采用scroll深分页的方式解决该问题，scroll为elasticsearch提供的一种滚动分页的方式，类似于sql中的cursor，使用是scroll每次取一页内容，然后返回一个scroll_id，然后根据这个scroll_id不断地获取下一页的内容，从而杜绝了页面读取的浪费，加快了搜索的性能。进过相关测试，使用scroll深分页方式，搜索速度较from+size搜索方式时间上快了一个数量级。

