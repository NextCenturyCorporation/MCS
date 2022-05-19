import math

from runner_script import MultipleFileRunnerScript

from machine_common_sense.controller import Controller
from machine_common_sense.controller_events import (
    AbstractControllerSubscriber, ControllerEventPayload)

MAX_DISTANCE = 0.06
MAX_DELTA_ANGLE = 11


def get_waypoint_action(delta_angle, step_metadata):
    if len(step_metadata.action_list) == 1:
        return step_metadata.action_list[0]
    if step_metadata.return_status == 'OBSTRUCTED':
        return 'OpenObject', {
            'objectImageCoordsX': 160, 'objectImageCoordsY': 120}
    if abs(delta_angle) > MAX_DELTA_ANGLE:
        return ('RotateLeft' if delta_angle > 0 else 'RotateRight', {})
    else:
        return ('MoveAhead', {})


def get_deltas(previous_output, waypoint):
    pos = previous_output.position
    rot = previous_output.rotation
    delta_x = waypoint['x'] - pos['x']
    delta_z = waypoint['z'] - pos['z']
    square_distance = delta_x * delta_x + delta_z * delta_z
    target_angle = math.degrees(math.atan2(delta_x, delta_z))
    delta_angle = (rot - target_angle + 720) % 360
    delta_angle = delta_angle if delta_angle <= 180 else delta_angle - 360
    return square_distance, delta_angle


class PathFollower(AbstractControllerSubscriber):
    waypoint_index = 0

    scene_name = ""

    def on_start_scene(self, payload: ControllerEventPayload):
        self.previous_output = payload.step_output

    def on_after_step(self, payload: ControllerEventPayload):
        self.previous_output = payload.step_output

    def init_callback(self, controller: Controller):
        controller.subscribe(self)

    def action_callback(self, scene_data, step_metadata, runner_script):
        step_metadata = self.previous_output
        if scene_data['name'] != self.scene_name:
            self.scene_name = scene_data['name']
            self.waypoint_index = 0

        path = scene_data.get('debug', {}).get('path')
        if not path:
            print("Scene did not have 'debug.path' section")
            return None, None

        if not step_metadata.position:
            print("No position provided.")
            return None, None
        waypoint = path[self.waypoint_index]
        sq_dist, delta_angle = get_deltas(step_metadata, waypoint)
        while sq_dist < MAX_DISTANCE**2:
            self.waypoint_index += 1
            if self.waypoint_index >= len(path):
                return None, None
            waypoint = path[self.waypoint_index]
            sq_dist, delta_angle = get_deltas(step_metadata, waypoint)

        return get_waypoint_action(delta_angle, step_metadata)


follower = PathFollower()


def main():
    MultipleFileRunnerScript(
        'Interactive Scenes - Follow Path',
        follower.action_callback, follower.init_callback)


if __name__ == "__main__":
    main()
