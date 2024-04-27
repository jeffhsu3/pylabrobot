# TODO!
import textwrap
from typing import cast
import unittest

from pylabrobot.resources import Plate, TipRack, TubeRack
from pylabrobot.resources.coordinate import Coordinate
from pylabrobot.resources.opentrons import load_opentrons_resource


class OpentronsLoadTests(unittest.TestCase):
  """ Tests for the Opentrons load functions. """

  def test_load_opentrons_resource(self):
    name = 'PCR_plate'
    hm = cast(Plate, load_opentrons_resource(
      "opentrons_96_aluminumblock_nest_wellplate_100ul",
      name=name,
      version=1,
      ))