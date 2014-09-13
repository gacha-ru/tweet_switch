#!/usr/bin/python
# -*- coding: utf-8 -*-
import boto
import boto.sqs
import time
from requests_oauthlib import OAuth1Session
import sys
import os
import ConfigParser

config = ConfigParser.SafeConfigParser()
base = os.path.dirname(os.path.abspath(__file__))
config.read(os.path.join(base, 'keys.conf'))

# raspberry pi switch
pi_switch = "False"


# botoでsqsに接続
def sqs_connect():
    # AWS accesskey
    aws_access_key = config.get('aws_keys', 'AWS_ACCESS_KEY')
    aws_secret_access_key = config.get('aws_keys', 'AWS_SECRET_ACCESS_KEY')
    region = config.get('aws_keys', 'REGION')

    # boto.ec2への認証
    sqs_session = boto.sqs.connect_to_region(region,
                                             aws_access_key_id=aws_access_key,
                                             aws_secret_access_key=aws_secret_access_key)

    return sqs_session


# キュー情報設定
def sqs_setting_queue(sqs_session):
    # SQS queue_name
    queue_name = "evil_tweet"
    # Create or Get queue
    queue = sqs_session.create_queue(queue_name)
    return queue


# キューからメッセージを取得
def sqs_get_queue(queue, sqs_session):
    try:
        # 1秒間キュー取得を行う
        queue.set_attribute('ReceiveMessageWaitTimeSeconds', 1)
        # キューのメッセージを返す
        return queue.get_messages(1)
    except:
        sys.exit(1)


# tweetする
def tweet(sqs_session, queue, message):
    # twitter token
    CK = config.get('twitter_keys', 'ConsumerKey')
    CS = config.get('twitter_keys', 'ConsumerSecret')
    AT = config.get('twitter_keys', 'AccessToken')
    AS = config.get('twitter_keys', 'AccesssTokenSecert')

    # ツイート投稿用のURL
    url = "https://api.twitter.com/1.1/statuses/update.json"

    for msg in message:
        tweet_message = msg.get_body()

    # ツイート本文
    params = {"status": tweet_message}

    # yes or noをキーボードから入力
    print ("%s をtweetしますか？" % tweet_message)
    input_data = raw_input('Enter or yesでtweetします')

    if input_data in "yes":
        # OAuth認証で POST method で投稿
        twitter = OAuth1Session(CK, CS, AT, AS)
        req = twitter.post(url, params=params)
        return_message = req.json()

        # レスポンスを確認
        if req.status_code == 200:
            print ("%s をtweetしました\n" % tweet_message)
            queue.delete_message(msg)
        else:
            # status codeが200以外だった場合はErrorの内容を返す
            print ("Error: %d" % req.status_code)
            print ("message: %s" % tweet_message)
            return_value_analysis(return_message)
            queue.delete_message(msg)
    else:
        queue.delete_message(msg)
        print ("%s を闇に葬り去りました\n" % tweet_message)


# エラーメッセージの内容を返す
def return_value_analysis(return_message):
    error_value = return_message["errors"]
    yutai = error_value[0]
    if yutai["message"] in "Status is a duplicate.":
        duplicate_message = ('同じこといっとるでー!かえなかえな〜(^o^)/\n'
                             '消しとくねー(^-^)それなー(^_<)=★')
        print duplicate_message


if __name__ == '__main__':
    try:
        # botoでSQS情報を取得
        sqs_session = sqs_connect()

        while True:
            time.sleep(0.01)

            # yes or noをキーボードから入力
            print ("今日もqueueとってきましょう！")
            input_data = raw_input('yes or no? ')

            if input_data in "yes":
                # queue情報取得
                queue = sqs_setting_queue(sqs_session)
                # メッセージを取得
                queue_message = sqs_get_queue(queue, sqs_session)

                # queue_messageが空のリストでなければtweetへ
                if queue_message:
                    tweet(sqs_session, queue, queue_message)
                else:
                    # 取ってこれるキューがない場合は下記メッセージを出して終了
                    exit_message = (
                        'あれ、なんもないでキュー!\n'
                        '全ての闇は払われましたね。\n'
                        '明日も頑張りましょう!!!'
                    )

                    print exit_message
                    sys.exit(0)

            # no が入力されたら終了
            elif input_data in "no":
                print ("スッキリしましたね。明日も頑張りましょう!!!")
                sys.exit(0)

            else:
                print("%s ってなに？" % input_data)
                print("YesかNoってゅったぢゃん!\n")

    # Ctrl + cで抜ける時
    except KeyboardInterrupt:
        sys.exit(1)
