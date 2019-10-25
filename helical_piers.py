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
        self.plate_config = []
        self.pier_depth = None
        self.shaft_capacity = None
    
    def capacity(self, soils):
        allowable_bearing_depth = {}
        for i, soil in enumerate(soils):
            depths = np.linspace(soil.top_depth, soil.layer_thickness, 10)
            if soil.hazard == True:
                print("HAZARD WARNING: Soil {} is a sensitive organic soil. This soil"
                      "layer is not a suitable bearing medium for the helical pier."
                      "Piers extended through this strata are at risk of buckling.".format(i))
            else:
                if np.any([soil.hazard == True for soil in soils[i+1:]]):
                    print("HAZARD WARNING: Soils below this strata are designated as sensitive"
                      "fine grained or organic soil. These soil layers are not capable"
                      "of resisting the compressive forces of the piers. Installing a"
                      "helical pier in bearing stratum above a sensitive layer may lead"
                      "to excessive settlement or loss of capacity. \n Please carefully"
                      "review the boring logs.")

                cohesive = self.plate_area*soil.cohesion*9
                cohesionless = (self.plate_area*soil.Nq*soil.gamma)*depths
                # Applying a FS=2; need to check if this is redundant. 
                total_capacities = (cohesionless+cohesive)/2

                for d, total_capacity in enumerate(total_capacities):
                    if total_capacity > self.required_capacity:
                        allowable_bearing_depth[depths[d]] = total_capacity
        return allowable_bearing_depth

    def torque(self):
        pass

    # def spacing(self, FS=3):
    #     # capacity/P/FS
    #     pass

    def lateral_capacity(self, soils, batter=10):

        for soil in soils:
            if soil.hazard == True:
                print("HAZARD WARNING: Sensitive soils provide no lateral capacity."
                      "Function will check for potential buckling though this stratum"
                      "instead.")

                # Nope, but need to give it a dummy until I remember how to calculate it.
                k_h = 10
                r_value = ((29000000*0.851)/(k_h*self.pier_diam))**0.25
                i_max = soil.layer_thickness/r_value

                ultimate_capacity = 3*(29000000*i_max/r_value**2)
                allowable_capacity = ultimate_capacity/2
                if allowable_capacity < self.shaft_capacity:
                # need to add a function to get the approximated lower bround of the shaft capacity given a pier shaft of diameter d
                    print("BUCKLING WARNING: Lack of adequate lateral capacity from"
                          "{} to {} feet below ground surface. Allowable capacity"
                          "does not exceed {} pounds. Required capacity is {} pounds."
                          "Increase pier diameter or number of piers in group.".format(soil.top_depth, soil.top_depth+soil.layer_thickness, allowable_capacity, self.required_capacity))

            else: 
                pass
                # return a calculation of the horizontal component of the ultimate capacity.


    def _plate_area(self):
        if self.pier_diam > 5 and np.any(self.plate_config) < 12:
            print("WARNING: Plates smaller than 12-inches diameter will"
                  "provide little bearing capacity.")

        inner_diameter = math.pi*(self.pier_diam/12**2)/4
        plate_area = np.array([math.pi*(plate/12**2)/4 for plate in self.plate_config])
        plate_area -= inner_diameter

        self.plate_area = sum(plate_area)
        

def required_pier_capacity(load, FS=2, piers_in_group=1):
    return load/(FS*piers_in_group)



# for reference:
# SHAFT STRUCTURAL CAPACITIES
# 2,375     100.000     6.000
# 2,375     135.000     9.000
# 2,875     140.000     13.000
# 2,875     180.000     16.000
# 3,500     210.000     18.000
# 3,500     290.000     27.000
# 4,500     260.000     30.000
# 4.500     350.000     48.000
