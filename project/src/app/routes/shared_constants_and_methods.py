from enum import Enum

SUCCESSFUL_DELETION_MESSAGE_KEY = "message"
SUCCESSFUL_DELETION_MESSAGE_VALUE_FOR_TAG = "The tag has been successfully deleted!"
SUCCESSFUL_DELETION_MESSAGE_VALUE_FOR_POST = "The post has been successfully deleted!"

OBJECT_CANNOT_BE_FOUND_STATUS_CODE = 404
OBJECT_CANNOT_BE_DELETED_STATUS_CODE = 400
TAG_ALREADY_EXISTS_STATUS_CODE = 400
VALUE_LENGTH_ERROR_STATUS_CODE = 422

REQUEST_IS_OK_STATUS_CODE = 200

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
            return f"Tag {value} already registered"
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


def get_search_characters_length_must_be_greater_than_three(length: int):
    message = [
        {
            "loc": [
                "body",
                "name"
            ],
            "msg": f"ensure this value has at least { length } characters",
            "type": "value_error.any_str.min_length",
            "ctx": {
                "limit_value": length
            }
        }
    ]
    return message
