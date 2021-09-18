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
from wechaty_puppet import EventReadyPayload
from wechaty_puppet import EventHeartbeatPayload
from wechaty_puppet import EventErrorPayload
from wechaty_puppet import FileBox, ScanStatus  # type: ignore
from wechaty_puppet import MessageType
import asyncio

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class MyBot(Wechaty):

    def __init__(self):
        super().__init__()
        self.busy = False
        self.auto_reply_comment = '''        
        '''

        self.__bot_name = "Cortana"
        self.__admin_group: Optional[Tuple] = ()
        self.__admin_room_name = "CertificateDAO 管理者们"
        self.__admin_room = None
        self.__admin_tag = "admin"

        self.__white_paper = None

    def __check_admin(self, friend: Contact):

        return self.__admin_tag in [tag.tag_id for tag in friend.tags()]

    # System Event
    async def on_ready(self, payload: EventReadyPayload):
        """Any initialization work can be put in here

        Args:
            payload (EventReadyPayload): ready data
        """
        # print(f'receive ready event<{payload}>')
        # # 1. 获取所有联系人
        # friends: List[Contact] = await self.Contact.find_all()
        # # 2. 从联系人中找出管理员
        # self.__admin_group = (friend.contact_id for friend in friends if self.__check_admin(friend))
        #
        # # find my python-wechaty related friends
        # # friends = [friend for friend in friends if str(friend.alias()).startswith('python-wechaty')]
        # # room: Room = await self.Room.create(friends, topic='Python❤Wechaty')
        # # if room:
        # #     await room.say('hello, python-wechaty is ready for you.')
        #
        # room: Optional[Room] = await self.Room.find(query=RoomQueryFilter(topic=self.__admin_room_name))
        #
        # if not room:
        #     log.error(f"{self.__admin_room_name} not existed! please check")
        #     return
        #
        # self.__admin_room = room
        # await room.say(f'{self.__bot_name} has started')

    # 心跳检测
    async def on_heartbeat(self, payload: EventHeartbeatPayload):
        print(f'receive heartbeat event from server <{payload}>')

    async def on_error(self, payload: EventErrorPayload):
        print(f'receive error event<{payload}> from sever')

    async def on_scan(self, qr_code: str, status: ScanStatus, data: Optional[str] = None):
        """listen scan event"""
        print('Scan QR Code to login: {}\n'.format(status))
        print('https://wechaty.js.org/qrcode/{}'.format(qr_code))

    async def on_login(self, contact: Contact):
        print(f'User {contact} logged in\n')

    async def on_logout(self, contact: Contact):
        print(f'User <{contact}> logout')

    async def on_message(self, msg: Message):
        #
        print(f'receive message <{msg}>')
        if "hello" == msg.text():
            print(f"i find you ! {msg.talker().name}")

        # 群聊@
        # if await msg.mention_self():
        #     room = msg.room()
        #     if room:
        #         text = msg.mention_text()
        #         mention_list = msg.mention_list()
        #         print(f"receive @ ,@ list:{mention_list},text:{text}")
        #         talker = msg.talker()
        #         await talker.say("ssss")
        #
        #     else:
        #         raise ValueError("mention 必须在群聊中！")

        # 收到消息
        # elif msg.type() == MessageType.MESSAGE_TYPE_ATTACHMENT and msg.talker().contact_id in self.__admin_group:
        #     self.__white_paper = await msg.to_file_box()
        #     # save the image as local file
        #     await self.__white_paper.to_file(f'./docs/{self.__white_paper.name}')
        #     # send image file to the room
        #     await self.__admin_room.say(self.__white_paper)
        # elif msg.type() == MessageType.MESSAGE_TYPE_TEXT and msg.text() in ["白皮书", "white paper", "White Paper"]:
        #     talker = msg.talker()
        #     if talker and self.__white_paper:
        #         await talker.say(self.__white_paper)
        #         print(f"{talker.name} has received white paper")

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
            if friendship.hello() == 'ding':
                log_msg = 'accepted automatically because verify messsage is "ding"'
                print('before accept ...')
                await friendship.accept()
                # if want to send msg, you need to delay sometimes
                print('waiting to send message ...')
                await asyncio.sleep(3)
                await contact.say(self.auto_reply_comment)
                print('after accept ...')
            else:
                log_msg = 'not auto accepted, because verify message is: ' + friendship.hello()

        # 主动添加他人好友得到确认时
        elif friendship.type() == FriendshipType.FRIENDSHIP_TYPE_CONFIRM:
            log_msg = 'friend ship confirmed with ' + contact.name

        print(log_msg)
        await administrator.say(log_msg)
        for admin in self.__admin_group:
            await admin.say(log_msg)

    async def on_room_topic(self, room: Room, new_topic: str, old_topic: str, changer: Contact, date: datetime):
        print(f'receive room topic changed event <from<{new_topic}> to <{old_topic}>> from room<{room}> ')

    async def on_room_invite(self, room_invitation: RoomInvitation):
        # 群聊邀请
        print(f'receive room invitation<{room_invitation}> event')

    async def on_room_join(self, room: Room, invitees: List[Contact], inviter: Contact, date: datetime):
        print(f'receive room join event from Room<{room}>')

    async def on_room_leave(self, room: Room, leavers: List[Contact], remover: Contact, date: datetime):
        print(f'receive room leave event from Room<{room}>')


bot: Optional[MyBot] = None


async def main():
    """Async Main Entry"""
    if 'WECHATY_PUPPET_SERVICE_TOKEN' not in os.environ:
        print('''
            Error: WECHATY_PUPPET_SERVICE_TOKEN is not found in the environment variables
            You need a TOKEN to run the Java Wechaty. Please goto our README for details
            https://github.com/wechaty/python-wechaty-getting-started/#wechaty_puppet_service_token
        ''')

    global bot
    bot = MyBot()
    await bot.start()


asyncio.run(main())
