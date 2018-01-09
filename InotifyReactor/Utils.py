def splitMask(mask, lookup, num_flags = 32):
  flags = filter(lambda bit: mask & bit, [1 << x for x in range(num_flags)])
  flag_names = [lookup[bit] for bit in flags]
  return flag_names
