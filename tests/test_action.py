import unittest

import machine_common_sense as mcs


class Test_Action(unittest.TestCase):

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
            "Close a nearby object. (objectId=string, amount=float " +
            "(default:1), objectDirectionX=float, objectDirectionY=float," +
            " objectDirectionZ=float)"
        )
        self.assertEqual(mcs.Action("CloseObject"), mcs.Action.CLOSE_OBJECT)
        self.assertEqual(mcs.Action("1"), mcs.Action.CLOSE_OBJECT)

    def test_crawl(self):
        self.assertEqual(mcs.Action.CRAWL.value, "Crawl")
        self.assertEqual(mcs.Action.CRAWL.key, "c")
        self.assertEqual(
            mcs.Action.CRAWL.desc,
            "Change pose to 'CRAWLING' (no params)"
        )
        self.assertEqual(mcs.Action("Crawl"), mcs.Action.CRAWL)
        self.assertEqual(mcs.Action("c"), mcs.Action.CRAWL)

    def test_drop_object(self):
        self.assertEqual(mcs.Action.DROP_OBJECT.value, "DropObject")
        self.assertEqual(mcs.Action.DROP_OBJECT.key, "2")
        self.assertEqual(
            mcs.Action.DROP_OBJECT.desc,
            "Drop an object you are holding. (objectId=string)"
        )
        self.assertEqual(mcs.Action("DropObject"), mcs.Action.DROP_OBJECT)
        self.assertEqual(mcs.Action("2"), mcs.Action.DROP_OBJECT)

    def test_lie_down(self):
        self.assertEqual(mcs.Action.LIE_DOWN.value, "LieDown")
        self.assertEqual(mcs.Action.LIE_DOWN.key, "l")
        self.assertEqual(
            mcs.Action.LIE_DOWN.desc,
            "Change pose to 'LYING' (rotation=float)"
        )
        self.assertEqual(mcs.Action("LieDown"), mcs.Action.LIE_DOWN)
        self.assertEqual(mcs.Action("l"), mcs.Action.LIE_DOWN)

    def test_move_ahead(self):
        self.assertEqual(mcs.Action.MOVE_AHEAD.value, "MoveAhead")
        self.assertEqual(mcs.Action.MOVE_AHEAD.key, "w")
        self.assertEqual(
            mcs.Action.MOVE_AHEAD.desc,
            "Move yourself ahead based on your current view. " +
            "(amount=float (default:0.5))"
        )
        self.assertEqual(mcs.Action("MoveAhead"), mcs.Action.MOVE_AHEAD)
        self.assertEqual(mcs.Action("w"), mcs.Action.MOVE_AHEAD)

    def test_move_back(self):
        self.assertEqual(mcs.Action.MOVE_BACK.value, "MoveBack")
        self.assertEqual(mcs.Action.MOVE_BACK.key, "s")
        self.assertEqual(
            mcs.Action.MOVE_BACK.desc,
            "Move yourself back based on your current view. " +
            "(amount=float (default:0.5))"
        )
        self.assertEqual(mcs.Action("MoveBack"), mcs.Action.MOVE_BACK)
        self.assertEqual(mcs.Action("s"), mcs.Action.MOVE_BACK)

    def test_move_left(self):
        self.assertEqual(mcs.Action.MOVE_LEFT.value, "MoveLeft")
        self.assertEqual(mcs.Action.MOVE_LEFT.key, "a")
        self.assertEqual(
            mcs.Action.MOVE_LEFT.desc,
            "Move yourself to your left based on your current view. " +
            "(amount=float (default:0.5))"
        )
        self.assertEqual(mcs.Action("MoveLeft"), mcs.Action.MOVE_LEFT)
        self.assertEqual(mcs.Action("a"), mcs.Action.MOVE_LEFT)

    def test_move_right(self):
        self.assertEqual(mcs.Action.MOVE_RIGHT.value, "MoveRight")
        self.assertEqual(mcs.Action.MOVE_RIGHT.key, "d")
        self.assertEqual(
            mcs.Action.MOVE_RIGHT.desc,
            "Move yourself to your right based on your current view. " +
            "(amount=float (default:0.5))"
        )
        self.assertEqual(mcs.Action("MoveRight"), mcs.Action.MOVE_RIGHT)
        self.assertEqual(mcs.Action("d"), mcs.Action.MOVE_RIGHT)

    def test_open_object(self):
        self.assertEqual(mcs.Action.OPEN_OBJECT.value, "OpenObject")
        self.assertEqual(mcs.Action.OPEN_OBJECT.key, "3")
        self.assertEqual(
            mcs.Action.OPEN_OBJECT.desc,
            "Open a nearby object. (objectId=string, " +
            "amount=float (default:1), objectDirectionX=float, " +
            "objectDirectionY=float, objectDirectionZ=float)"
        )
        self.assertEqual(mcs.Action("OpenObject"), mcs.Action.OPEN_OBJECT)
        self.assertEqual(mcs.Action("3"), mcs.Action.OPEN_OBJECT)

    def test_pickup_object(self):
        self.assertEqual(mcs.Action.PICKUP_OBJECT.value, "PickupObject")
        self.assertEqual(mcs.Action.PICKUP_OBJECT.key, "4")
        self.assertEqual(
            mcs.Action.PICKUP_OBJECT.desc,
            "Pickup a nearby object and hold it in your hand. " +
            "(objectId=string, objectDirectionX=float, " +
            "objectDirectionY=float, objectDirectionZ=float)"
        )
        self.assertEqual(mcs.Action("PickupObject"), mcs.Action.PICKUP_OBJECT)
        self.assertEqual(mcs.Action("4"), mcs.Action.PICKUP_OBJECT)

    def test_pull_object(self):
        self.assertEqual(mcs.Action.PULL_OBJECT.value, "PullObject")
        self.assertEqual(mcs.Action.PULL_OBJECT.key, "5")
        self.assertEqual(
            mcs.Action.PULL_OBJECT.desc,
            "Pull a nearby object. (objectId=string, rotation=float, " +
            "horizon=float, force=float (default:0.5), " +
            "objectDirectionX=float, objectDirectionY=float, " +
            "objectDirectionZ=float)"
        )
        self.assertEqual(mcs.Action("PullObject"), mcs.Action.PULL_OBJECT)
        self.assertEqual(mcs.Action("5"), mcs.Action.PULL_OBJECT)

    def test_push_object(self):
        self.assertEqual(mcs.Action.PUSH_OBJECT.value, "PushObject")
        self.assertEqual(mcs.Action.PUSH_OBJECT.key, "6")
        self.assertEqual(
            mcs.Action.PUSH_OBJECT.desc,
            "Push a nearby object. (objectId=string, rotation=float, " +
            "horizon=float, force=float (default:0.5), " +
            "objectDirectionX=float, objectDirectionY=float, " +
            "objectDirectionZ=float)"
        )
        self.assertEqual(mcs.Action("PushObject"), mcs.Action.PUSH_OBJECT)
        self.assertEqual(mcs.Action("6"), mcs.Action.PUSH_OBJECT)

    def test_put_object(self):
        self.assertEqual(mcs.Action.PUT_OBJECT.value, "PutObject")
        self.assertEqual(mcs.Action.PUT_OBJECT.key, "7")
        self.assertEqual(
            mcs.Action.PUT_OBJECT.desc,
            "Place an object you are holding into/onto a nearby " +
            "receptacle object. (objectId=string, " +
            "receptacleObjectId=string, " +
            "receptacleObjectDirectionX=float, " +
            "receptacleObjectDirectionY=float, " +
            "receptacleObjectDirectionZ=float)"
        )
        self.assertEqual(mcs.Action("PutObject"), mcs.Action.PUT_OBJECT)
        self.assertEqual(mcs.Action("7"), mcs.Action.PUT_OBJECT)

    def test_rotate_look(self):
        self.assertEqual(mcs.Action.ROTATE_LOOK.value, "RotateLook")
        self.assertEqual(mcs.Action.ROTATE_LOOK.key, "r")
        self.assertEqual(
            mcs.Action.ROTATE_LOOK.desc,
            "Rotate your view left/right and/or up/down based on your " +
            "current view. (rotation=float, horizon=float)"
        )
        self.assertEqual(mcs.Action("RotateLook"), mcs.Action.ROTATE_LOOK)
        self.assertEqual(mcs.Action("r"), mcs.Action.ROTATE_LOOK)

    def test_stand(self):
        self.assertEqual(mcs.Action.STAND.value, "Stand")
        self.assertEqual(mcs.Action.STAND.key, "u")
        self.assertEqual(
            mcs.Action.STAND.desc,
            "Change pose to 'STANDING' (no params)"
        )
        self.assertEqual(mcs.Action("Stand"), mcs.Action.STAND)
        self.assertEqual(mcs.Action("u"), mcs.Action.STAND)

    def test_throw_object(self):
        self.assertEqual(mcs.Action.THROW_OBJECT.value, "ThrowObject")
        self.assertEqual(mcs.Action.THROW_OBJECT.key, "q")
        self.assertEqual(
            mcs.Action.THROW_OBJECT.desc,
            "Throw an object you are holding. (objectId=string, " +
            "objectDirectionX=float, objectDirectionY=float, " +
            "objectDirectionZ=float, force=float (default:0.5))"
        )
        self.assertEqual(mcs.Action("ThrowObject"), mcs.Action.THROW_OBJECT)
        self.assertEqual(mcs.Action("q"), mcs.Action.THROW_OBJECT)

    def test_pass(self):
        self.assertEqual(mcs.Action.PASS.value, "Pass")
        self.assertEqual(mcs.Action.PASS.key, " ")
        self.assertEqual(
            mcs.Action.PASS.desc,
            "Do nothing. (no params)"
        )
        self.assertEqual(mcs.Action("Pass"), mcs.Action.PASS)
        self.assertEqual(mcs.Action(" "), mcs.Action.PASS)
