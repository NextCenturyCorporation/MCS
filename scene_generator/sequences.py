from abc import ABC, abstractmethod
from typing import Any, Dict, List

import tags


class Sequence(ABC):
    """Creates a unique sequence of one or more scenes that each have the same
    goals, objects, and variables, except for specific differences."""

    def __init__(
        self,
        name: str,
        body_template: Dict[str, Any],
        goal_template: Dict[str, Any]
    ) -> None:
        self._name = name
        self._scenes = self._create_scenes(body_template, goal_template)

    @abstractmethod
    def _create_scenes(
        self,
        body_template: Dict[str, Any],
        goal_template: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Create and return this sequence's scenes."""
        pass

    def _update_list_with_object_info(
        self,
        tag: str,
        info_list: List[str],
        object_list: List[Dict[str, Any]]
    ) -> List[str]:
        """Update the given info list with the info from each object in the
        given object list using the given tag."""
        info_set = set(info_list)
        for instance in object_list:
            object_info_list = instance.get('info', []).copy()
            if 'goalString' in instance:
                object_info_list.append(instance['goalString'])
            info_set |= set([(tag + ' ' + info) for info in object_info_list])
        return list(info_set)

    def _update_scene_objects(
        self,
        scene: Dict[str, Any],
        tag_to_objects: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Update and return the given scene with the given objects."""
        for tag, object_list in tag_to_objects.items():
            for instance in object_list:
                instance['role'] = tag
        scene['objects'] = [
            instance for object_list in tag_to_objects.values()
            for instance in object_list
        ]
        scene['goal'] = scene.get('goal', {})
        scene['goal']['type_list'] = scene['goal'].get('type_list', [])
        scene['goal']['type_list'] = tags.append_object_tags(
            scene['goal']['type_list'],
            tag_to_objects
        )
        goal_info_list = []
        for tag, object_list in tag_to_objects.items():
            goal_info_list = self._update_list_with_object_info(
                tag,
                goal_info_list,
                object_list
            )
        scene['goal']['info_list'] = goal_info_list
        return scene

    def get_name(self) -> str:
        """Return this sequence's name."""
        return self._name

    def get_scenes(self) -> List[Dict[str, Any]]:
        """Return this sequence's list of scenes."""
        return self._scenes


class SequenceFactory(ABC):
    """Builds Sequences."""

    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def build(self, body_template: Dict[str, Any]) -> Sequence:
        """Create and return a new sequence built by this factory."""
        pass
