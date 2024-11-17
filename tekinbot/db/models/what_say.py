from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from tekinbot.db.models import TekinTableBase


class WhatSay(TekinTableBase):

    __tablename__ = 'what_say'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    subject = Column(String(512), unique=True)
    description = Column(String(8192))
