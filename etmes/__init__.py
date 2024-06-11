__author__ = "MH Wang"
import importlib.util
from .instruments.ins import SM, waitFlag, ins
from .exp import exp
from .meas import meas
if importlib.util.find_spec("matplotlib"):
    from .show import show
from .instruments.Keithley2400 import Keithley2400
from .instruments.InstecMK2000B import CH, InstecMK2000B
from .instruments.LakeShore340 import LakeShore340
from .instruments.Keithley2182A import Keithley2182A
from .instruments.EastChangingP7050 import EastChangingP7050
if importlib.util.find_spec("clr"):
    from .instruments.QuantumDesign import QuantumDesignDynaCool, QuantumDesignPPMS, QuantumDesignSVSM, QuantumDesignVersaLab
