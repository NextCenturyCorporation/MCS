import unittest

import machine_common_sense as mcs


class TestAction(unittest.TestCase):

    def test_repr(self):
        repr_result1 = (
            "<Action.CLOSE_OBJECT: " +
            mcs.Action.CLOSE_OBJECT.value + ", " +
            mcs.Action.CLOSE_OBJECT.key + ", " +
            mcs.Action.CLOSE_OBJECT.desc +
            ">"
        )
        repr_result2 = (
            "<Action.PUT_OBJECT: " +
            mcs.Action.PUT_OBJECT.value + ", " +
            mcs.Action.PUT_OBJECT.key + ", " +
            mcs.Action.PUT_OBJECT.desc +
            ">"
        )
        self.assertEqual(repr(mcs.Action.CLOSE_OBJECT), repr_result1)
        self.assertEqual(repr(mcs.Action.PUT_OBJECT), repr_result2)

    def test_close_object(self):
        self.assertEqual(mcs.Action.CLOSE_OBJECT.value, "CloseObject")
        self.assertEqual(mcs.Action.CLOSE_OBJECT.key, "1")
        self.assertEqual(
            mcs.Action.CLOSE_OBJECT.desc,
            "Close a nearby object. (objectId=string, amount=float "
            "(default:1), objectImageCoordsX=float, objectImageCoordsY=float)"
        )
        self.assertEqual(mcs.Action("CloseObject"), mcs.Action.CLOSE_OBJECT)
        self.assertEqual(mcs.Action("1"), mcs.Action.CLOSE_OBJECT)

    def test_drop_object(self):
        self.assertEqual(mcs.Action.DROP_OBJECT.value, "DropObject")
        self.assertEqual(mcs.Action.DROP_OBJECT.key, "2")
        self.assertEqual(
            mcs.Action.DROP_OBJECT.desc,
            "Drop an object you are holding. (objectId=string)"
        )
        self.assertEqual(mcs.Action("DropObject"), mcs.Action.DROP_OBJECT)
        self.assertEqual(mcs.Action("2"), mcs.Action.DROP_OBJECT)

    def test_move_ahead(self):
        self.assertEqual(mcs.Action.MOVE_AHEAD.value, "MoveAhead")
        self.assertEqual(mcs.Action.MOVE_AHEAD.key, "w")
        self.assertEqual(
            mcs.Action.MOVE_AHEAD.desc,
            "Move yourself ahead based on your current view."
        )
        self.assertEqual(mcs.Action("MoveAhead"), mcs.Action.MOVE_AHEAD)
        self.assertEqual(mcs.Action("w"), mcs.Action.MOVE_AHEAD)

    def test_move_back(self):
        self.assertEqual(mcs.Action.MOVE_BACK.value, "MoveBack")
        self.assertEqual(mcs.Action.MOVE_BACK.key, "s")
        self.assertEqual(
            mcs.Action.MOVE_BACK.desc,
            "Move yourself back based on your current view."
        )
        self.assertEqual(mcs.Action("MoveBack"), mcs.Action.MOVE_BACK)
        self.assertEqual(mcs.Action("s"), mcs.Action.MOVE_BACK)

    def test_move_left(self):
        self.assertEqual(mcs.Action.MOVE_LEFT.value, "MoveLeft")
        self.assertEqual(mcs.Action.MOVE_LEFT.key, "a")
        self.assertEqual(
            mcs.Action.MOVE_LEFT.desc,
            "Move yourself to your left based on your current view."
        )
        self.assertEqual(mcs.Action("MoveLeft"), mcs.Action.MOVE_LEFT)
        self.assertEqual(mcs.Action("a"), mcs.Action.MOVE_LEFT)

    def test_move_right(self):
        self.assertEqual(mcs.Action.MOVE_RIGHT.value, "MoveRight")
        self.assertEqual(mcs.Action.MOVE_RIGHT.key, "d")
        self.assertEqual(
            mcs.Action.MOVE_RIGHT.desc,
            "Move yourself to your right based on your current view."
        )
        self.assertEqual(mcs.Action("MoveRight"), mcs.Action.MOVE_RIGHT)
        self.assertEqual(mcs.Action("d"), mcs.Action.MOVE_RIGHT)

    def test_open_object(self):
        self.assertEqual(mcs.Action.OPEN_OBJECT.value, "OpenObject")
        self.assertEqual(mcs.Action.OPEN_OBJECT.key, "3")
        self.assertEqual(
            mcs.Action.OPEN_OBJECT.desc,
            "Open a nearby object. (objectId=string, "
            "amount=float (default:1), objectImageCoordsX=float, "
            "objectImageCoordsY=float)"
        )
        self.assertEqual(mcs.Action("OpenObject"), mcs.Action.OPEN_OBJECT)
        self.assertEqual(mcs.Action("3"), mcs.Action.OPEN_OBJECT)

    def test_pickup_object(self):
        self.assertEqual(mcs.Action.PICKUP_OBJECT.value, "PickupObject")
        self.assertEqual(mcs.Action.PICKUP_OBJECT.key, "4")
        self.assertEqual(
            mcs.Action.PICKUP_OBJECT.desc,
            "Pickup a nearby object and hold it in your hand. "
            "(objectId=string, objectImageCoordsX=float, "
            "objectImageCoordsY=float)"
        )
        self.assertEqual(mcs.Action("PickupObject"), mcs.Action.PICKUP_OBJECT)
        self.assertEqual(mcs.Action("4"), mcs.Action.PICKUP_OBJECT)

    def test_pull_object(self):
        self.assertEqual(mcs.Action.PULL_OBJECT.value, "PullObject")
        self.assertEqual(mcs.Action.PULL_OBJECT.key, "5")
        self.assertEqual(
            mcs.Action.PULL_OBJECT.desc,
            "Pull a nearby object. (objectId=string, "
            "force=float (default:0.5), "
            "objectImageCoordsX=float, objectImageCoordsY=float)"
        )
        self.assertEqual(mcs.Action("PullObject"), mcs.Action.PULL_OBJECT)
        self.assertEqual(mcs.Action("5"), mcs.Action.PULL_OBJECT)

    def test_push_object(self):
        self.assertEqual(mcs.Action.PUSH_OBJECT.value, "PushObject")
        self.assertEqual(mcs.Action.PUSH_OBJECT.key, "6")
        self.assertEqual(
            mcs.Action.PUSH_OBJECT.desc,
            "Push a nearby object. (objectId=string, "
            "force=float (default:0.5), "
            "objectImageCoordsX=float, objectImageCoordsY=float)"
        )
        self.assertEqual(mcs.Action("PushObject"), mcs.Action.PUSH_OBJECT)
        self.assertEqual(mcs.Action("6"), mcs.Action.PUSH_OBJECT)

    def test_torque_object(self):
        self.assertEqual(mcs.Action.TORQUE_OBJECT.value, "TorqueObject")
        self.assertEqual(mcs.Action.TORQUE_OBJECT.key, "8")
        self.assertEqual(
            mcs.Action.TORQUE_OBJECT.desc,
            "Apply torque to a nearby object. (objectId=string, "
            "force=float(default:0.5), objectImageCoordsX=float, "
            "objectImageCoordsY=float)"
        )
        self.assertEqual(mcs.Action("TorqueObject"), mcs.Action.TORQUE_OBJECT)
        self.assertEqual(mcs.Action("8"), mcs.Action.TORQUE_OBJECT)

    def test_rotate_object(self):
        self.assertEqual(mcs.Action.ROTATE_OBJECT.value, "RotateObject")
        self.assertEqual(mcs.Action.ROTATE_OBJECT.key, "9")
        self.assertEqual(
            mcs.Action.ROTATE_OBJECT.desc,
            "Apply a rotation of 5 degrees to a nearby object. "
            "(objectId=string, "
            "clockwise=bool(default:True), objectImageCoordsX=float, "
            "objectImageCoordsY=float)"
        )
        self.assertEqual(mcs.Action("RotateObject"), mcs.Action.ROTATE_OBJECT)
        self.assertEqual(mcs.Action("9"), mcs.Action.ROTATE_OBJECT)

    def test_move_object(self):
        self.assertEqual(mcs.Action.MOVE_OBJECT.value, "MoveObject")
        self.assertEqual(mcs.Action.MOVE_OBJECT.key, "0")
        self.assertEqual(
            mcs.Action.MOVE_OBJECT.desc,
            "Apply a movement of 0.1 meters to a nearby object. "
            "(objectId=string, "
            "lateral=int(default:0), "
            "straight=int(default:1), "
            "objectImageCoordsX=float, "
            "objectImageCoordsY=float)"
        )
        self.assertEqual(mcs.Action("MoveObject"), mcs.Action.MOVE_OBJECT)
        self.assertEqual(mcs.Action("0"), mcs.Action.MOVE_OBJECT)

    def test_interact_with_agent(self):
        self.assertEqual(
            mcs.Action.INTERACT_WITH_AGENT.value,
            "InteractWithAgent")
        self.assertEqual(mcs.Action.INTERACT_WITH_AGENT.key, "T")
        self.assertEqual(
            mcs.Action.INTERACT_WITH_AGENT.desc,
            "Interact with an agent. If that agent has an object, "
            "it will hold out the object for you to pickup; "
            "otherwise, the agent will look sad."
            "(objectId=string, "
            "objectImageCoordsX=float, "
            "objectImageCoordsY=float)"
        )
        self.assertEqual(
            mcs.Action("InteractWithAgent"),
            mcs.Action.INTERACT_WITH_AGENT)
        self.assertEqual(mcs.Action("T"), mcs.Action.INTERACT_WITH_AGENT)

    def test_put_object(self):
        self.assertEqual(mcs.Action.PUT_OBJECT.value, "PutObject")
        self.assertEqual(mcs.Action.PUT_OBJECT.key, "7")
        self.assertEqual(
            mcs.Action.PUT_OBJECT.desc,
            "Place an object you are holding into/onto a nearby "
            "receptacle object. (objectId=string, "
            "receptacleObjectId=string, "
            "receptacleObjectImageCoordsX=float, "
            "receptacleObjectImageCoordsY=float)"
        )
        self.assertEqual(mcs.Action("PutObject"), mcs.Action.PUT_OBJECT)
        self.assertEqual(mcs.Action("7"), mcs.Action.PUT_OBJECT)

    def test_rotate_left(self):
        self.assertEqual(mcs.Action.ROTATE_LEFT.value, "RotateLeft")
        self.assertEqual(mcs.Action.ROTATE_LEFT.key, "j")
        self.assertEqual(
            mcs.Action.ROTATE_LEFT.desc,
            "Rotate your view left by 10 degrees."
        )
        self.assertEqual(mcs.Action("RotateLeft"), mcs.Action.ROTATE_LEFT)
        self.assertEqual(mcs.Action("j"), mcs.Action.ROTATE_LEFT)

    def test_rotate_right(self):
        self.assertEqual(mcs.Action.ROTATE_RIGHT.value, "RotateRight")
        self.assertEqual(mcs.Action.ROTATE_RIGHT.key, "l")
        self.assertEqual(
            mcs.Action.ROTATE_RIGHT.desc,
            "Rotate your view right by 10 degrees."
        )
        self.assertEqual(mcs.Action("RotateRight"), mcs.Action.ROTATE_RIGHT)
        self.assertEqual(mcs.Action("l"), mcs.Action.ROTATE_RIGHT)

    def test_look_up(self):
        self.assertEqual(mcs.Action.LOOK_UP.value, "LookUp")
        self.assertEqual(mcs.Action.LOOK_UP.key, "i")
        self.assertEqual(
            mcs.Action.LOOK_UP.desc,
            "Rotate your view up (subtract 10 degrees from head tilt)."
        )
        self.assertEqual(mcs.Action("LookUp"), mcs.Action.LOOK_UP)
        self.assertEqual(mcs.Action("i"), mcs.Action.LOOK_UP)

    def test_look_down(self):
        self.assertEqual(mcs.Action.LOOK_DOWN.value, "LookDown")
        self.assertEqual(mcs.Action.LOOK_DOWN.key, "k")
        self.assertEqual(
            mcs.Action.LOOK_DOWN.desc,
            "Rotate your view down (add 10 degrees to head tilt)."
        )
        self.assertEqual(mcs.Action("LookDown"), mcs.Action.LOOK_DOWN)
        self.assertEqual(mcs.Action("k"), mcs.Action.LOOK_DOWN)

    def test_pass(self):
        self.assertEqual(mcs.Action.PASS.value, "Pass")
        self.assertEqual(mcs.Action.PASS.key, " ")
        self.assertEqual(
            mcs.Action.PASS.desc,
            "Do nothing. (no params)"
        )
        self.assertEqual(mcs.Action("Pass"), mcs.Action.PASS)
        self.assertEqual(mcs.Action(" "), mcs.Action.PASS)

    def test_input_to_action_and_params(self):
        self.assertEqual(mcs.Action.input_to_action_and_params(
            'MoveBack'), ('MoveBack', {}))
        self.assertEqual(mcs.Action.input_to_action_and_params(
            'RotateRight'), ('RotateRight', {}))
        self.assertEqual(
            mcs.Action.input_to_action_and_params(
                'PickupObject,objectId=testId'
            ),
            ('PickupObject', {'objectId': 'testId'})
        )
        self.assertEqual(
            mcs.Action.input_to_action_and_params(
                'PushObject,objectId=testId,force=12.34'
            ),
            ('PushObject', {'objectId': 'testId', 'force': 12.34})
        )
        self.assertEqual(
            mcs.Action.input_to_action_and_params('Foobar'), (None, {}))
        self.assertEqual(mcs.Action.input_to_action_and_params(
            'MoveBack,key:value'), ('MoveBack', None))


if __name__ == '__main__':
    unittest.main()
