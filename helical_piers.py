import numpy as np
import math 
from soil import Soil
       
class pier():
    """

    """
    def __init__(self, required_capacity):
        self.required_capacity = required_capacity

        # none of these have been defined through any function.
        # the shaft capacity is a function of pier diameter.
        self.pier_diam = None
        self.plate_config = []
        self.pier_depth = None
        self.shaft_capacity = None 

        self.allowable_bearing_depth = None
        self.allowable_bearing_strata = None
    
    def calculate_bearing_capacity(soil, safety_factor):
        soil.Nq = (0.3359)*np.exp(0.1247*self.phi)
        
        depths = np.arange(soil.layer_depth, (soil.layer_thickness+soil.layer_depth), 0.5)

        cohesive = self.plate_area*soil.cohesion*9
        cohesionless = (self.plate_area*soil.Nq*soil.gamma)*depths
        total_capacities = (cohesionless+cohesive)/safety_factor

        if np.all(total_capacities > self.required_capacity):
            self.allowable_bearing_depth = depths[0]
            self.allowable_bearing_strata = soil

        elif np.all(total_capacities < self.required_capacity):
            if soil.underlying_layer is not None:
                calculate_bearing_capacity(soil.underlying_layer, safety_factor)
            else:
                print("WARNING: The required bearing capacity can not be achieved
                " at any depth within the soil profile as described.")
        
        else:
            possible_bearing_depths = np.where(total_capacities > self.required_capacity)
            for depth in possible_bearing_depths:
                if np.all(total_capacities[depth:] == True):
                    self.allowable_bearing_depth = depth
                    self.allowable_bearing_strata = soil

    def check_hazard(self, soil_profile):
        hazards = []
        while soil.underlying_layer is not None:
            if soil.harzard == True:
                hazards.append(True)
            else:
                hazards.append(False)

        if np.all(hazards == True):
            print("HAZARD WARNING: The soil profile as described contains no
            " suitable bearing medium. Please review the boring logs carefully.")
            hazards = -1
        elif np.all(hazards == False):
            hazards = 0
        else:
            hazards = len(hazards) - 1 - hazards[::-1].index(True)
        return hazards

    def capacity(self, soil_profile, safety_factor=2):
        soil_layer = soil_profile
        layer_number = 0

        hazards = self.check_hazard(soil_profile)
        if hazards >= 0:
        while layer_number < hazards: 
            soil_layer = soil.underlying_layer
            layer_number += 1
            
        calculate_bearing_capacity(soil_layer, safety_factor)

    def torque(self):
        pass

    # def spacing(self, FS=3):
    #     # capacity/P/FS
    #     pass

    def lateral_capacity(self, soils, batter=10):

        for soil in soils:
            if soil.hazard == True:
                print("HAZARD WARNING: Sensitive soils provide no lateral capacity."
                      "Function will check for buckling of structural member though this stratum"
                      "instead of lateral capacity.")

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
                
                # ultimate capacity needs to be defined!
                ultimate_capacity = False 
                horizontal_component = np.tan(batter)*ultimate_capacity
                return horizontal_component

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
# 4,500     350.000     48.000
