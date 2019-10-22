import numpy as np
import math 

class soil():
    def __init__(self, uscs, unit_weight, friction_angle, cohesion, layer_thickness, top_depth, hazard=False):
        self.uscs = uscs
        self.gamma = unit_weight
        self.phi = friction_angle
        self.cohesion = cohesion
        self.layer_thickness = layer_thickness
        self.top_depth = top_depth
        
        self.hazard = hazard
        if self.uscs == "OL":
            self.hazard = True

        self.Nq = (0.3359)*np.exp(0.1247*self.phi)
       
class pier():
    def __init__(self, required_capacity):
        self.required_capacity = required_capacity

        self.pier_diam = None
        self.plate_config = None
        self.plate_area = None
        self.pier_depth = None
    
    def capacity(self, soils):
        capacities = {}
        for i, soil in enumerate(soils):
            depths = np.linspace(soil.top_depth, soil.layer_thickness, 10)
            if soil.hazard == True:
                capacities[soil] = 0 
                print("WARNING: Soil {} is a sensitive organic soil. This soil"
                      "layer is not a suitable bearing medium for the helical pier."
                      "Piers extended through this strata are at risk of buckling.".format(i))
            else:
                cohesive = self.plate_area*soil.cohesion*9
                cohesionless = (self.plate_area*soil.Nq*soil.gamma)*depths
                capacities[soil] = dict(zip(depths, cohesionless+cohesive))

    def torque(self):
        pass

    def spacing(self, FS=3):
        # capacity/P/FS
        pass

    def lateral_resistance(self, batter=10):
        pass

    def bucking(self, soils):
        for i, soil in enumerate(soils):
            if soil.hazard == True:
                # calculate buckling
                pass
        pass

    def plate_area(self):
        if self.pier_diam > 5 and np.any(self.plate_config) < 12:
            print("WARNING: Plates smaller than 12-inches diameter will"
                  "provide little bearing capacity.")

        inner_diameter = (math.pi()*(self.pier_diam/12)**2)/4
        plate_area = np.array([(math.pi()*plate/12)**2)/4 for plate in self.plate_config])
        plate_area -= inner_diameter

        self.plate_area = sum(plate_area)

# 2,375     100.000     6.000
# 2,375     135.000     9.000
# 2,875     140.000     13.000
# 2,875     180.000     16.000
# 3,500     210.000     18.000
# 3,500     290.000     27.000
# 4,500     260.000     30.000
# 4.500     350.000     48.000

def required_pier_capacity(load, FS=2, piers_in_group=1):
    return load/(FS*piers_in_group)
