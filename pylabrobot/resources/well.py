import enum
import math
from typing import Any, Callable, Dict, Optional, Union

from pylabrobot.resources.container import Container


class WellBottomType(enum.Enum):
  """ Enum for the type of bottom of a well. """

  FLAT = "flat"
  U = "U"
  V = "V"
  UNKNOWN = "unknown"


class CrossSectionType(enum.Enum):
  """ Enum for the type of cross section of a well.

  A well with a circular cross section will be a cylinder, and a well with a square cross section
  will be a rectangular cuboid. Note that the bottom section of a well may be any of the
  :class:`WellBottomType` values.
  """

  CIRCLE = "circle"
  SQUARE = "square"


class Well(Container):
  """ Base class for Well resources.

  Note that in regular use these will be automatically generated by the
  :class:`pylabrobot.resources.Plate` class.
  """

  def __init__(self, name: str, size_x: float, size_y: float, size_z: float,
    bottom_type: Union[WellBottomType, str] = WellBottomType.UNKNOWN, category: str = "well",
    max_volume: Optional[float] = None, model: Optional[str] = None,
    compute_volume_from_height: Optional[Callable[[float], float]] = None,
    cross_section_type: Union[CrossSectionType, str] = CrossSectionType.CIRCLE):
    """ Create a new well.

    Args:
      name: Name of the well.
      size_x: Size of the well in the x direction.
      size_y: Size of the well in the y direction.
      size_z: Size of the well in the z direction.
      bottom_type: Type of the bottom of the well. If a string, must be the raw value of the
        :class:`WellBottomType` enum. This is used to deserialize and may be removed in the future.
      category: Category of the well.
      max_volume: Maximum volume of the well. If not specified, the well will be seen as a cylinder
        and the max volume will be computed based on size_x, size_y, and size_z.
      compute_volume_from_height: function to compute the volume from the height relative to the
        bottom
      cross_section_type: Type of the cross section of the well. If not specified, the well will be
        seen as a cylinder.
    """

    if isinstance(bottom_type, str):
      bottom_type = WellBottomType(bottom_type)
    if isinstance(cross_section_type, str):
      cross_section_type = CrossSectionType(cross_section_type)

    if max_volume is None:
      if compute_volume_from_height is None:
        # we assume flat bottom as a best guess, bottom types require additional information
        if cross_section_type == CrossSectionType.CIRCLE:
          assert size_x == size_y, "size_x and size_y must be equal for circular wells."
          max_volume = math.pi * (size_x / 2) ** 2 * size_z
        elif cross_section_type == CrossSectionType.SQUARE:
          assert size_x == size_y, "size_x and size_y must be equal for square wells."
          max_volume = size_x * size_y * size_z
      else:
        max_volume = compute_volume_from_height(size_z)

    super().__init__(name, size_x=size_x, size_y=size_y, size_z=size_z, category=category,
      max_volume=max_volume, model=model)
    self.bottom_type = bottom_type
    self._compute_volume_from_height = compute_volume_from_height
    self.cross_section_type = cross_section_type

    self.tracker.register_callback(self._state_updated)

  def serialize(self):
    return {
      **super().serialize(),
      "bottom_type": self.bottom_type.value,
      "cross_section_type": self.cross_section_type.value,
    }

  def compute_volume_from_height(self, height: float) -> float:
    """ Compute the volume of liquid in a well from the height of the liquid relative to the bottom
    of the well.

    Args:
      height: Height of the liquid in the well relative to the bottom.

    Returns:
      The volume of liquid in the well.

    Raises:
      NotImplementedError: If the plate does not have a volume computation function.
    """

    if self._compute_volume_from_height is None:
      raise NotImplementedError("compute_volume_from_height not implemented.")

    return self._compute_volume_from_height(height)

  def serialize_state(self) -> Dict[str, Any]:
    return self.tracker.serialize()

  def load_state(self, state: Dict[str, Any]):
    self.tracker.load_state(state)
