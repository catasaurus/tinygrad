#!/usr/bin/env python
import unittest
from tinygrad.tensor import Tensor, Device
from tinygrad.nn import Conv2d
from tinygrad.ops import GlobalCounters

@unittest.skipUnless(Device.DEFAULT == "GPU", "Only GPU supports cache")
class TestConvShapetracker(unittest.TestCase):
  def test_conv_3x3_one_view(self):
    inp = Tensor.randn(1,16,10,10).realize()
    conv = Conv2d(16, 32, (3,3))
    conv(inp).realize()
    GlobalCounters.cache = []
    conv(inp).realize()
    test = GlobalCounters.cache
    GlobalCounters.cache = None
    assert len(test) == 1, f"conv should only have one kernel {[x[0].clprg.name for x in test]}"
    print(test[0][0].clprg.prg)
    for arg in test[0][1]:
      print(arg.st)
      assert len(arg.st.views) == 1

if __name__ == '__main__':
  unittest.main()
