# TODO: move the GRAPH and DEBUG stuff to here
import gc
from tinygrad.helpers import prod
from tinygrad.tensor import Tensor
from tinygrad.lazy import LazyBuffer
from tinygrad.llops.ops_gpu import GPUBuffer
from tinygrad.ops import GlobalCounters

def print_objects():
  #gc.collect()
  tensors = [x for x in gc.get_objects() if isinstance(x, Tensor)]
  tensor_ram_used = sum([prod(x.shape)*4 for x in tensors])
  lazybuffers = [x for x in gc.get_objects() if isinstance(x, LazyBuffer)]
  gpubuffers = [x for x in gc.get_objects() if isinstance(x, GPUBuffer)]
  realized_buffers = [x.realized for x in lazybuffers if x.realized]
  gpubuffers_orphaned = [x for x in gpubuffers if x not in realized_buffers]

  print(f"{len(tensors)} tensors allocated in {tensor_ram_used/1e9:.2f} GB, GPU using {GlobalCounters.mem_used/1e9:.2f} GB")
  print(f"{len(lazybuffers)} lazybuffers {len(realized_buffers)} realized, {len(gpubuffers)} GPU buffers")
  print(f"{len(gpubuffers_orphaned)} GPU buffers are orphaned")

  cnt = 0
  for tb in gpubuffers_orphaned:
    bb = gc.get_referrers(tb)
    for b in bb:
      if b is not gpubuffers and b is not gpubuffers_orphaned:
        print(tb, "\nreference", type(b), len(b), str(b)[0:150])
        for x in gc.get_referrers(b):
          print("double reference", str(x)[0:100])
        print("\n")
    if cnt == 10:
      break
    cnt += 1

  for x in gpubuffers_orphaned:
    if getattr(x, '_buf', None): del x._buf
    if getattr(x, '_image', None): del x._image

  return len(gpubuffers_orphaned)

"""
import gc

def print_ram():
  print(GlobalCounters.mem_used/1e9, sum([prod(x.shape)*4 for x in gc.get_objects() if isinstance(x, Tensor)])/1e9)
  img_count = sum([x.is_image() for x in gc.get_objects() if isinstance(x, OpenCLBuffer)])
  print("img_count", img_count)
  buffer_bytes = sum([x.cl.size for x in gc.get_objects() if isinstance(x, CLBuffer)])
  image_bytes = sum([x.cl.row_pitch*x.cl.height for x in gc.get_objects() if isinstance(x, CLImage)])
  print("buffer bytes", buffer_bytes/1e9, "image bytes", image_bytes/1e9, "sum", (buffer_bytes+image_bytes)/1e9)
"""
