tweet switch
============================

Raspberry piとSQSでtweetスイッチ  
[Overview](http://qiita.com/gacha-ru/items/305c462ba5d6a3ed0a8a)


# Preparation
1. prepare the keys.conf. make from keys.conf_example.
    $ mv keys.conf_example keys.conf
2. describe the AWS access key / twitter token to keys.conf
    # AWS accesskey
    [aws_keys]
    AWS_ACCESS_KEY = access_key(Permissions:sqs only)
    AWS_SECRET_ACCESS_KEY = secret_access_key(Permissions:sqs only)
    REGION = ap-northeast-1

    # Twitter token
    [twitter_keys]
    ConsumerKey =    twitter_consumerkey
    ConsumerSecret = twitter_consumersecret
    AccessToken =    twitter_accesstoken
    AccesssTokenSecert = twitter_accessstokensecert


# Description

* sqs_send_queue.py
  storing your "tweet message" queue in evil_tweet
    $ python sqs_send_queue.py "tweet message"

* tweet_switch.py
  evil_tweet from Queuing, you choose to tweet
  works only with raspberry pi available (to use the GPIO)
    $ python tweet_switch.py

* local_tweet_script.py
  evil_tweet from Queuing, you choose to tweet
  The operation check here if there is no raspberry pi
    $ python local_tweet_script.py

