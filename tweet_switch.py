#!/usr/bin/python
# -*- coding: utf-8 -*-
import boto
import boto.sqs
from RPi import GPIO
import time
from requests_oauthlib import OAuth1Session
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
        queue.set_attribute('ReceiveMessageWaitTimeSeconds', 1)
        return queue.get_messages(1)
    except:
        GPIO.cleanup()


def get_queue_message(message):
    try:
        for msg in message:
            tweet_message = msg.get_body()

        return tweet_message.encode('utf-8')
    except:
        GPIO.cleanup()


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

    # 日本語tweet用
    tweet = tweet_message.encode('utf-8')
    # ツイート本文
    params = {"status": tweet}

    print ("%s をtweetしますか？" % tweet)

    # tweetをするかしないかをスイッチで決める
    review = tweet_review()
    print review

    if review == "Yes":
        # OAuth認証で POST method で投稿
        twitter = OAuth1Session(CK, CS, AT, AS)
        req = twitter.post(url, params=params)

        # レスポンスを確認
        if req.status_code == 200:
            print ("%s をtweetしました" % tweet)
            queue.delete_message(msg)
        else:
            print ("Error: %d" % req.status_code)
            print ("message: %s" % tweet)
            queue.delete_message(msg)

    elif review == "No":
        print "tweetやんぴ"
        queue.delete_message(msg)


# tweetするか確認
def tweet_review():
    while True:
        time.sleep(0.01)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(15, GPIO.OUT)
        GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.output(15, False)
        no_input = GPIO.input(19)
        GPIO.output(15, not no_input)
        yes_input = GPIO.input(11)

        # メッセージ取得と同じスイッチ
        if yes_input == 0:
            GPIO.cleanup()
            return "Yes"

        #
        if no_input == 0:
            GPIO.cleanup()
            return "No"


if __name__ == '__main__':

    try:
        # botoでSQS情報を取得
        sqs_session = sqs_connect()

        while True:
            # raspberry pi GPIO init
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(7, GPIO.OUT)
            GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.output(7, False)
            input = GPIO.input(11)
            GPIO.output(7, not input)
            time.sleep(0.01)

            if input == 0 and pi_switch == "False":
                # 物理スイッチのフラグ(ON)
                pi_switch = "True"

                # queue情報取得
                queue = sqs_setting_queue(sqs_session)
                # メッセージを取得
                queue_message = sqs_get_queue(queue, sqs_session)

                # queue_messageが空のリストでなければtweetへ
                if queue_message:
                    tweet(sqs_session, queue, queue_message)
                else:
                    print "ないでキュー"

            elif input == 1:
                pi_switch = "False"

    except KeyboardInterrupt:
        GPIO.cleanup()
