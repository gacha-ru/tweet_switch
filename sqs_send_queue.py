#!/usr/bin/python
# coding: utf8
import boto
import boto.sqs
from boto.sqs.message import Message

import sys
from sys import argv

import os
import ConfigParser

config = ConfigParser.SafeConfigParser()
base = os.path.dirname(os.path.abspath(__file__))
config.read(os.path.join(base, 'keys.conf'))


def sqs_send_queue(aws_access_key, aws_secret_access_key, region, queue_name, queue_message):
    # boto.sqsへの認証
    conn = boto.sqs.connect_to_region(region,
                                      aws_access_key_id=aws_access_key,
                                      aws_secret_access_key=aws_secret_access_key)

    # Create or Get queue info
    queue = conn.create_queue(queue_name)

    # send queue
    queue.write(Message(body=queue_message))
    print "%s へ %s をいれました" % (queue_name, queue_message)


'''
[main function]
'''
if __name__ == '__main__':
    argvs = sys.argv
    argc = len(argvs)

    if not argc == 2:
        print u'Usage: python %s message' % argv[0]
        quit()

    # queueに入れるメッセージ
    queue_message = argvs[1]

    # 文字数チェック
    tweet_limit = len(queue_message.decode("utf-8"))
    if 140 > tweet_limit:
        print "文字数：%s Check OK!!!" % tweet_limit
        # 作成するqueueの名前
        queue_name = "evil_tweet"

        # アカウント情報
        aws_access_key = config.get('aws_keys', 'AWS_ACCESS_KEY')
        aws_secret_access_key = config.get('aws_keys', 'AWS_SECRET_ACCESS_KEY')
        region = config.get('aws_keys', 'REGION')

        # queue_nameへqueue_messageを送信
        sqs_send_queue(aws_access_key,
                       aws_secret_access_key,
                       region,
                       queue_name,
                       queue_message)
    else:
        print "文字数：%s Check NG!!!" % tweet_limit
        print "140字まで!!こまめに吐き出してこう( ｰ`дｰ´)ｷﾘｯ"