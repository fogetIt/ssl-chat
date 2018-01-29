# -*- coding: utf-8 -*-
# @Date:   2018-01-20 14:59:10
# @Last Modified time: 2018-01-25 18:41:23
import json
from functools import partial
from .app import App


app = App()


def create_message(sender=None, title=None, ext_data=None):
    if not sender or not title or not ext_data:
        return None
    message_dict = {"title": title, "sender": sender}
    message_dict.update(ext_data=ext_data)
    return json.dumps(message_dict)


group_message = partial(create_message, title="group")
private_message = partial(create_message, title="private")
error_message = partial(create_message, title="error", sender="system")
users_message = partial(create_message, title="users", sender="system", ext_data=app.users)


def close_client(client_socket):
    result = app.remove_client(client_socket=client_socket)
    if result:
        app.broadcast(users_message())


@app.route("login")
def login(message_dict, client_socket):
    user_name = message_dict.get("name")
    result = app.add_client(user_name=user_name, client_socket=client_socket)
    if result:
        app.logger.warning(result)
        app.send_message(
            error_message(ext_data=result), client_socket
        )
    else:
        app.broadcast(users_message())
        app.logger.info("{user_name} login successful".format(user_name=user_name))


@app.route("logout")
def logout(message_dict, client_socket):
    close_client(client_socket=client_socket)


@app.route("private")
def private(message_dict, client_socket):
    ext_data = message_dict.get("ext_data")
    app.send_message(
        private_message(sender=app.get_user(client_socket), ext_data=ext_data),
        app.get_socket(message_dict.get("receiver"))
    )


@app.route("group")
def group(message_dict, client_socket):
    ext_data = message_dict.get("ext_data")
    app.broadcast(
        group_message(sender=app.get_user(client_socket), ext_data=ext_data),
        app.get_user(client_socket),
        client_socket
    )
