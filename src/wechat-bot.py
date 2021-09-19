#!/usr/local/bin python3
import logging
import os

from wechaty import Wechaty, ScanStatus, RoomQueryFilter
from typing import Optional
from wechaty import Contact
from wechaty import Message
from wechaty import Friendship
from wechaty import Room
from wechaty import RoomInvitation
from wechaty import FriendshipType
from typing import List, Union, Tuple
from datetime import datetime
from wechaty_puppet import EventReadyPayload, get_logger
from wechaty_puppet import EventHeartbeatPayload
from wechaty_puppet import EventErrorPayload
from wechaty_puppet import FileBox, ScanStatus  # type: ignore
from wechaty_puppet import MessageType
import asyncio

logging.basicConfig(level=logging.INFO)
log = get_logger('Cortana')


class MyBot(Wechaty):

    def __init__(self):
        super().__init__()
        self.busy = False
        self.auto_reply_comment = '''      
        Welcome CertificateDAO!
        
        Website: http://certificatedao.com,http://certificatedao.eth
        Docs: http://docs.certificatedao.co 
        Github: https://github.com/CertficateDAO/
          
        区块链革命带来最重要的不是匿名性，而是透明性
        绝大多数产品都进入了误区，聚焦在「隐蔽」「躲藏」中
        而忽略了最根本的目的 —— 节约资源的交换成本
  
        '''
        self.__admin_group: Optional[Tuple] = ()
        self.__admin_room_name = "CertificateDAO 管理者们"
        self.__admin_room = None
        self.__white_paper = None
        self.__administrator: Optional[Contact] = None

    # System Event
    async def on_ready(self, payload: EventReadyPayload):
        """Any initialization work can be put in here

        Args:
            payload (EventReadyPayload): ready data
        """
        log.info(f'receive ready event<{payload}>')

        self.__administrator = bot.Contact.load('haruki-shubin')
        await self.__administrator.ready()
        log.info(f"{self.__administrator.name} has logged in")
        # find my python-wechaty related friends
        # friends = [friend for friend in friends if str(friend.alias()).startswith('python-wechaty')]
        # room: Room = await self.Room.create(friends, topic='Python❤Wechaty')
        # if room:
        #     await room.say('hello, python-wechaty is ready for you.')
        room: Optional[Room] = await self.Room.find(query=RoomQueryFilter(topic=self.__admin_room_name))

        if not room:
            log.error(f"{self.__admin_room_name} not existed! please check")
            return
        self.__admin_room = room

    # 心跳检测
    async def on_heartbeat(self, payload: EventHeartbeatPayload):
        log.info(f'receive heartbeat event from server <{payload}>')

    async def on_error(self, payload: EventErrorPayload):
        log.info(f'receive error event<{payload}> from sever')

    async def on_scan(self, qr_code: str, status: ScanStatus, data: Optional[str] = None):
        """listen scan event"""
        log.info('Scan QR Code to login: {}\n'.format(status))
        log.info('https://wechaty.js.org/qrcode/{}'.format(qr_code))

    async def on_login(self, contact: Contact):
        log.info(f'User {contact} logged in\n')

    async def on_logout(self, contact: Contact):
        log.info(f'User <{contact}> logout')

    async def on_message(self, msg: Message):
        #
        log.info(f'receive message <{msg}>')
       
        # 如果消息发送者是admin
        if self.__is_admin(msg.talker()):
            # 更新白皮书
            if msg.type() == MessageType.MESSAGE_TYPE_ATTACHMENT:
                self.__white_paper = await msg.to_file_box()
                # save the image as local file
                await self.__white_paper.to_file(f'./docs/{self.__white_paper.name}')
                # send image file to the room
                await self.__admin_room.say(self.__white_paper)
            # 邀请某人加入群
            elif msg.type() == MessageType.MESSAGE_TYPE_TEXT:
                msg_text = msg.text()
                command, arg = msg_text.split()
                if command == "invite":
                    log.info(f"{self.__administrator.name} invite {arg} to group")
                    # todo 主动加人
                else:
                    await msg.talker().say(f"未配置的相关命令: {command} {arg}")

        else:
            if msg.type() == MessageType.MESSAGE_TYPE_TEXT and msg.text() in ["白皮书", "white paper", "White Paper"]:
                talker = msg.talker()
                if talker and self.__white_paper:
                    await talker.say(self.__white_paper)
                    log.info(f"{talker.name} has received white paper")

    def __is_admin(self, talker: Contact):
        """
        检测消息发送者是否是管理员
        :param talker:消息发送者
        :return: True/False
        """
        return talker.contact_id == self.__administrator.contact_id

    async def on_friendship(self, friendship: Friendship):
        # 根据微信号码找到管理员
        # todo 可以替换为管理员组、群
        administrator = bot.Contact.load('admin-id')
        await administrator.ready()

        contact = friendship.contact()
        await contact.ready()

        log_msg = f'receive "friendship" message from {contact.name}'
        await administrator.say(log_msg)

        # 判断是否是好友请求
        if friendship.type() == FriendshipType.FRIENDSHIP_TYPE_RECEIVE:
            # 校验好友请求信息
            if friendship.hello() == 'certificate-dao':
                log_msg = 'accepted automatically because verify messsage is "certificate-dao"'
                log.info('before accept ...')
                await friendship.accept()
                # if want to send msg, you need to delay sometimes
                log.info('waiting to send message ...')
                await asyncio.sleep(3)
                await contact.say(self.auto_reply_comment)
                log.info('after accept ...')
            else:
                log_msg = 'not auto accepted, because verify message is: ' + friendship.hello()

        # 主动添加他人好友得到确认时
        elif friendship.type() == FriendshipType.FRIENDSHIP_TYPE_CONFIRM:
            log_msg = 'friend ship confirmed with ' + contact.name

        # 通知管理员
        log.info(log_msg)
        await administrator.say(log_msg)

    async def on_room_topic(self, room: Room, new_topic: str, old_topic: str, changer: Contact, date: datetime):
        log.info(f'receive room topic changed event <from<{new_topic}> to <{old_topic}>> from room<{room}> ')

    async def on_room_invite(self, room_invitation: RoomInvitation):
        # 群聊邀请
        log.info(f'receive room invitation<{room_invitation}> event')

    async def on_room_join(self, room: Room, invitees: List[Contact], inviter: Contact, date: datetime):
        log.info(f'receive room join event from Room<{room}>')

    async def on_room_leave(self, room: Room, leavers: List[Contact], remover: Contact, date: datetime):
        log.info(f'receive room leave event from Room<{room}>')


bot: Optional[MyBot] = None


async def main():
    """Async Main Entry"""
    if 'WECHATY_PUPPET_SERVICE_TOKEN' not in os.environ:
        log.info('''
            Error: WECHATY_PUPPET_SERVICE_TOKEN is not found in the environment variables
            You need a TOKEN to run the Java Wechaty. Please goto our README for details
            https://github.com/wechaty/python-wechaty-getting-started/#wechaty_puppet_service_token
        ''')

    global bot
    bot = MyBot()
    await bot.start()


asyncio.run(main())
