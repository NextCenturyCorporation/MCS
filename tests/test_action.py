import unittest

from machine_common_sense.action import Action


class Test_Action(unittest.TestCase):

    def test_repr(self):
        repr_result1 = (
            "<Action.CLOSE_OBJECT: " +
            Action.CLOSE_OBJECT.value + ", " +
            Action.CLOSE_OBJECT.key + ", " +
            Action.CLOSE_OBJECT.desc +
            ">"
        )
        repr_result2 = (
            "<Action.PUT_OBJECT: " +
            Action.PUT_OBJECT.value + ", " +
            Action.PUT_OBJECT.key + ", " +
            Action.PUT_OBJECT.desc +
            ">"
        )
        self.assertEqual(repr(Action.CLOSE_OBJECT), repr_result1)
        self.assertEqual(repr(Action.PUT_OBJECT), repr_result2)

    def test_close_object(self):
        self.assertEqual(Action.CLOSE_OBJECT.value, "CloseObject")
        self.assertEqual(Action.CLOSE_OBJECT.key, "1")
        self.assertEqual(
            Action.CLOSE_OBJECT.desc,
            "Close a nearby object. (objectId=string, amount=float " +
            "(default:1), objectDirectionX=float, objectDirectionY=float," +
            " objectDirectionZ=float)"
        )
        self.assertEqual(Action("CloseObject"), Action.CLOSE_OBJECT)
        self.assertEqual(Action("1"), Action.CLOSE_OBJECT)

    def test_crawl(self):
        self.assertEqual(Action.CRAWL.value, "Crawl")
        self.assertEqual(Action.CRAWL.key, "c")
        self.assertEqual(
            Action.CRAWL.desc,
            "Change pose to 'CRAWLING' (no params)"
        )
        self.assertEqual(Action("Crawl"), Action.CRAWL)
        self.assertEqual(Action("c"), Action.CRAWL)

    def test_drop_object(self):
        self.assertEqual(Action.DROP_OBJECT.value, "DropObject")
        self.assertEqual(Action.DROP_OBJECT.key, "2")
        self.assertEqual(
            Action.DROP_OBJECT.desc,
            "Drop an object you are holding. (objectId=string)"
        )
        self.assertEqual(Action("DropObject"), Action.DROP_OBJECT)
        self.assertEqual(Action("2"), Action.DROP_OBJECT)

    def test_lie_down(self):
        self.assertEqual(Action.LIE_DOWN.value, "LieDown")
        self.assertEqual(Action.LIE_DOWN.key, "l")
        self.assertEqual(
            Action.LIE_DOWN.desc,
            "Change pose to 'LYING' (rotation=float)"
        )
        self.assertEqual(Action("LieDown"), Action.LIE_DOWN)
        self.assertEqual(Action("l"), Action.LIE_DOWN)

    def test_move_ahead(self):
        self.assertEqual(Action.MOVE_AHEAD.value, "MoveAhead")
        self.assertEqual(Action.MOVE_AHEAD.key, "w")
        self.assertEqual(
            Action.MOVE_AHEAD.desc,
            "Move yourself ahead based on your current view. " +
            "(amount=float (default:0.5))"
        )
        self.assertEqual(Action("MoveAhead"), Action.MOVE_AHEAD)
        self.assertEqual(Action("w"), Action.MOVE_AHEAD)

    def test_move_back(self):
        self.assertEqual(Action.MOVE_BACK.value, "MoveBack")
        self.assertEqual(Action.MOVE_BACK.key, "s")
        self.assertEqual(
            Action.MOVE_BACK.desc,
            "Move yourself back based on your current view. " +
            "(amount=float (default:0.5))"
        )
        self.assertEqual(Action("MoveBack"), Action.MOVE_BACK)
        self.assertEqual(Action("s"), Action.MOVE_BACK)

    def test_move_left(self):
        self.assertEqual(Action.MOVE_LEFT.value, "MoveLeft")
        self.assertEqual(Action.MOVE_LEFT.key, "a")
        self.assertEqual(
            Action.MOVE_LEFT.desc,
            "Move yourself to your left based on your current view. " +
            "(amount=float (default:0.5))"
        )
        self.assertEqual(Action("MoveLeft"), Action.MOVE_LEFT)
        self.assertEqual(Action("a"), Action.MOVE_LEFT)

    def test_move_right(self):
        self.assertEqual(Action.MOVE_RIGHT.value, "MoveRight")
        self.assertEqual(Action.MOVE_RIGHT.key, "d")
        self.assertEqual(
            Action.MOVE_RIGHT.desc,
            "Move yourself to your right based on your current view. " +
            "(amount=float (default:0.5))"
        )
        self.assertEqual(Action("MoveRight"), Action.MOVE_RIGHT)
        self.assertEqual(Action("d"), Action.MOVE_RIGHT)

    def test_open_object(self):
        self.assertEqual(Action.OPEN_OBJECT.value, "OpenObject")
        self.assertEqual(Action.OPEN_OBJECT.key, "3")
        self.assertEqual(
            Action.OPEN_OBJECT.desc,
            "Open a nearby object. (objectId=string, " +
            "amount=float (default:1), objectDirectionX=float, " +
            "objectDirectionY=float, objectDirectionZ=float)"
        )
        self.assertEqual(Action("OpenObject"), Action.OPEN_OBJECT)
        self.assertEqual(Action("3"), Action.OPEN_OBJECT)

    def test_pickup_object(self):
        self.assertEqual(Action.PICKUP_OBJECT.value, "PickupObject")
        self.assertEqual(Action.PICKUP_OBJECT.key, "4")
        self.assertEqual(
            Action.PICKUP_OBJECT.desc,
            "Pickup a nearby object and hold it in your hand. " +
            "(objectId=string, objectDirectionX=float, " +
            "objectDirectionY=float, objectDirectionZ=float)"
        )
        self.assertEqual(Action("PickupObject"), Action.PICKUP_OBJECT)
        self.assertEqual(Action("4"), Action.PICKUP_OBJECT)

    def test_pull_object(self):
        self.assertEqual(Action.PULL_OBJECT.value, "PullObject")
        self.assertEqual(Action.PULL_OBJECT.key, "5")
        self.assertEqual(
            Action.PULL_OBJECT.desc,
            "Pull a nearby object. (objectId=string, rotation=float, " +
            "horizon=float, force=float (default:0.5), " +
            "objectDirectionX=float, objectDirectionY=float, " +
            "objectDirectionZ=float)"
        )
        self.assertEqual(Action("PullObject"), Action.PULL_OBJECT)
        self.assertEqual(Action("5"), Action.PULL_OBJECT)

    def test_push_object(self):
        self.assertEqual(Action.PUSH_OBJECT.value, "PushObject")
        self.assertEqual(Action.PUSH_OBJECT.key, "6")
        self.assertEqual(
            Action.PUSH_OBJECT.desc,
            "Push a nearby object. (objectId=string, rotation=float, " +
            "horizon=float, force=float (default:0.5), " +
            "objectDirectionX=float, objectDirectionY=float, " +
            "objectDirectionZ=float)"
        )
        self.assertEqual(Action("PushObject"), Action.PUSH_OBJECT)
        self.assertEqual(Action("6"), Action.PUSH_OBJECT)

    def test_put_object(self):
        self.assertEqual(Action.PUT_OBJECT.value, "PutObject")
        self.assertEqual(Action.PUT_OBJECT.key, "7")
        self.assertEqual(
            Action.PUT_OBJECT.desc,
            "Place an object you are holding into/onto a nearby " +
            "receptacle object. (objectId=string, " +
            "receptacleObjectId=string, " +
            "receptacleObjectDirectionX=float, " +
            "receptacleObjectDirectionY=float, " +
            "receptacleObjectDirectionZ=float)"
        )
        self.assertEqual(Action("PutObject"), Action.PUT_OBJECT)
        self.assertEqual(Action("7"), Action.PUT_OBJECT)

    def test_rotate_look(self):
        self.assertEqual(Action.ROTATE_LOOK.value, "RotateLook")
        self.assertEqual(Action.ROTATE_LOOK.key, "r")
        self.assertEqual(
            Action.ROTATE_LOOK.desc,
            "Rotate your view left/right and/or up/down based on your " +
            "current view. (rotation=float, horizon=float)"
        )
        self.assertEqual(Action("RotateLook"), Action.ROTATE_LOOK)
        self.assertEqual(Action("r"), Action.ROTATE_LOOK)

    def test_stand(self):
        self.assertEqual(Action.STAND.value, "Stand")
        self.assertEqual(Action.STAND.key, "u")
        self.assertEqual(
            Action.STAND.desc,
            "Change pose to 'STANDING' (no params)"
        )
        self.assertEqual(Action("Stand"), Action.STAND)
        self.assertEqual(Action("u"), Action.STAND)

    def test_throw_object(self):
        self.assertEqual(Action.THROW_OBJECT.value, "ThrowObject")
        self.assertEqual(Action.THROW_OBJECT.key, "q")
        self.assertEqual(
            Action.THROW_OBJECT.desc,
            "Throw an object you are holding. (objectId=string, " +
            "objectDirectionX=float, objectDirectionY=float, " +
            "objectDirectionZ=float, force=float (default:0.5))"
        )
        self.assertEqual(Action("ThrowObject"), Action.THROW_OBJECT)
        self.assertEqual(Action("q"), Action.THROW_OBJECT)

    def test_pass(self):
        self.assertEqual(Action.PASS.value, "Pass")
        self.assertEqual(Action.PASS.key, " ")
        self.assertEqual(
            Action.PASS.desc,
            "Do nothing. (no params)"
        )
        self.assertEqual(Action("Pass"), Action.PASS)
        self.assertEqual(Action(" "), Action.PASS)
