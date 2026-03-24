"""Message service tests."""
from __future__ import annotations

from app.schemas.message import MessageCreate
from app.services.message_service import post_message, list_messages


def test_post_and_list(db):
    msg = post_message(db, MessageCreate(
        channel="common",
        author_type="human",
        author_name="tester",
        message="Hello world",
    ))
    assert msg.id
    assert msg.message == "Hello world"

    messages = list_messages(db)
    assert len(messages) >= 1


def test_channel_filter(db):
    post_message(db, MessageCreate(channel="common", author_name="a", message="msg1"))
    post_message(db, MessageCreate(channel="ticket/ABC-1", author_name="b", message="msg2"))

    common = list_messages(db, channel="common")
    assert all(m.channel == "common" for m in common)

    ticket = list_messages(db, channel="ticket/ABC-1")
    assert all(m.channel == "ticket/ABC-1" for m in ticket)
