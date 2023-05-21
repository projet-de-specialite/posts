from enum import Enum

SUCCESSFUL_DELETION_MESSAGE_KEY = "message"
SUCCESSFUL_DELETION_MESSAGE_VALUE_FOR_TAG = "The tag has been successfully deleted!"
SUCCESSFUL_DELETION_MESSAGE_VALUE_FOR_POST = "The post has been successfully deleted!"

# TODO - Tests actions, check user_id when editing and deleting, add image to directory


class ObjectType(int, Enum):
    POST = 0,
    TAG = 1


def get_object_cannot_be_found_detail_message(value, value_type: ObjectType):
    match value_type:
        case ObjectType.POST:
            return f"The post with id: {value} cannot be found!"
        case ObjectType.TAG:
            return f"The tag with slug: {value} cannot be found!"
        case _:
            pass


def get_tag_already_exists_detail_message(value, value_type: ObjectType):
    match value_type:
        case ObjectType.TAG:
            return f"Tag { value } already registered"
        case _:
            pass


def get_object_cannot_be_deleted_detail_message(value, value_type: ObjectType):
    match value_type:
        case ObjectType.POST:
            return f"Could not delete the post with id: {value} !"
        case ObjectType.TAG:
            return f"Could not delete the tag with slug: {value} !"
        case _:
            pass
