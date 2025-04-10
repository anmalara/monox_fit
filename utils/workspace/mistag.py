

def determine_region_wp(region):
  if 'tight' in region:
    return 'tight'
  elif 'loose' in region:
    return 'loose'
  else:
    return 'monojet'

def mistag_scale_and_flip(sf_wp, region_wp):
    if sf_wp == region_wp:
      scale = 1.0
      flip = False
    elif sf_wp == 'loose' and region_wp =='monojet':
        scale = 0.05
        flip = True
    elif sf_wp == 'tight' and region_wp == 'loose':
        scale = 0.1
        flip = True
    else:
      scale = 0
      flip = False
    return scale, flip

