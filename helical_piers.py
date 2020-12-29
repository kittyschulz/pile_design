import numpy as np
import math 
from soil import Soil
       
class HelicalPier():
    """
    A class used represent a Helical Pier and calculate the required
    design specifications based on the material properties of the pier and soil.

    Please see README documentation for an in-depth discussion of the calculations
    performed to obtain the pile design parameters. 

    Attributes
    ----------
    required_capacity : (flt)
        required axial bearing capacity of the helical pier.

    pier_diam : (flt)
        OD of pier shaft.
        
    plate_config : (tuple)
        tuple containing the diameter of each plate in the design plate configuration.

    plate_area : (flt)
        total bearing area of plate(s). 

    pier_lateral_capacity : (flt)
        allowable lateral capacity of the helical pier shaft.

    pier_axial_capacity : (flt)
        allowable axial capacity of the helical pier. 

    allowable_bearing_depth : (flt)
        minimum allowable bearing depth of bottom plate. 

    allowable_bearing_strata : (flt)
        soil type and properties of strata at allowable bearing depth.

    Methods
    -------



    """

    
    def __init__(self, required_capacity):
        self.required_capacity = required_capacity

        # none of these have been defined through any function.
        # the shaft capacity is a function of pier diameter.
        self._pier_structural_specs = {2.375: [100, 6], 2.875: [140, 13], 3.500: [210, 18], 4.500: [260, 30]}
        
        self.pier_diam = None
        self.plate_config = []
        self.plate_area = None
        self.pier_lateral_capacity = None 
        self.pier_axial_capacity = None

        self.allowable_bearing_depth = None
        self.allowable_bearing_strata = None


    
    def _calculate_bearing_capacity(self, soil, safety_factor):
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
                _calculate_bearing_capacity(soil.underlying_layer, safety_factor)
            else:
                print("WARNING: The required bearing capacity can not be achieved "
                      "at any depth within the soil profile as described.")
        
        else:
            possible_bearing_depths = np.where(total_capacities > self.required_capacity)
            for depth in possible_bearing_depths:
                if np.all(total_capacities[depth:] == True):
                    self.allowable_bearing_depth = depth
                    self.allowable_bearing_strata = soil

    def _check_hazard(self, soil_profile):
        """
        traverses a soil profile to identify the first (most shallow) strata that
        is neither a hazard condition (i.e., weak, organic) nor underlain by a hazard
        condition. The layer identified by _check_hazard should serve as the starting 
        point in identifying a suitable bearing medium for piers. 

        Args:
            soil_profile : (Soil)
                a graph representing a simplified soil profile
        
        Returns:
            first_suitable_layer : (flt)
                a float representing the depth in the soil_profile
                graph to get to the first soil layer that may possibly
                serve as a suitable bearing medium, or provide any meaningful
                capacity. 
        """
        hazards = []
        while soil.underlying_layer is not None:
            if soil.harzard == True:
                hazards.append(True)
            else:
                hazards.append(False)

        if np.all(hazards == True):
            print("HAZARD WARNING: The soil profile as described contains no "
                  "suitable bearing medium. Please review the boring logs carefully.")
            first_suitable_layer = -1
        elif np.all(hazards == False):
            first_suitable_layer = 0
        else:
            first_suitable_layer = len(hazards) - 1 - hazards[::-1].index(True)
        return first_suitable_layer

    def capacity(self, soil_profile, safety_factor=2):
        soil_layer = soil_profile
        layer_number = 0

        hazards = self._check_hazard(soil_profile)
        if hazards >= 0:
        while layer_number < hazards: 
            soil_layer = soil.underlying_layer
            layer_number += 1
            
        _calculate_bearing_capacity(soil_layer, safety_factor)

    def torque(self):
        pass

    # def spacing(self, FS=3):
    #     # capacity/P/FS
    #     pass

    def lateral_capacity(self, soils, batter=10):

        for soil in soils:
            if soil.hazard == True:
                print("HAZARD WARNING: Sensitive soils provide no lateral capacity. "
                      "Function will check for buckling of structural member though this stratum "
                      "instead of lateral capacity.")

                # Nope, but need to give it a dummy until I remember how to calculate it.
                k_h = 10
                r_value = ((29000000*0.851)/(k_h*self.pier_diam))**0.25
                i_max = soil.layer_thickness/r_value

                ultimate_capacity = 3*(29000000*i_max/r_value**2)
                allowable_capacity = ultimate_capacity/2
                if allowable_capacity < self.pier_lateral_capacity:
                # need to add a function to get the approximated lower bound of the shaft capacity given a pier shaft of diameter d
                    print("BUCKLING WARNING: Lack of adequate lateral capacity from "
                          "{} to {} feet below ground surface. Allowable capacity "
                          "does not exceed {} pounds. Required capacity is {} pounds. "
                          "Increase pier diameter or number of piers in group.".format(soil.top_depth, soil.top_depth+soil.layer_thickness, allowable_capacity, self.required_capacity))

            else: 
                
                # ultimate capacity needs to be defined!
                ultimate_capacity = False 
                horizontal_component = np.tan(batter)*ultimate_capacity
                return horizontal_component

    def _plate_area(self):
        if self.pier_diam > 5 and np.any(self.plate_config) < 12:
            print("WARNING: Plates smaller than 12-inches diameter will "
                  "provide little bearing capacity. The provided configuration 
                  " is not recommended.")

        inner_diameter = math.pi*(self.pier_diam/12**2)/4
        plate_area = np.array([math.pi*(plate/12**2)/4 for plate in self.plate_config])
        plate_area -= inner_diameter

        self.plate_area = sum(plate_area)
        
    def override_pier_specs(self,pier_diam, ultimate_axial, ultimate_lateral):
        self._pier_structural_specs[pier_diam] = [ultimate_axial, ultimate_lateral]

    def print_pier_specs(self, pier_diam=None):
        if pier_diam is not None and pier_diam in self._pier_structural_specs:
            print('{}" OD Pier: \n '
                  '   Ultimate Structural Axial Capacity: {}\n'
                  '   Ultimate Structural Lateral Capacity: {}\n'.format(self._pier_structural_specs[pier_diam], self._pier_structural_specs[pier_diam][0], self._pier_structural_specs[pier_diam][1])
        else:
            for pier in self._pier_structural_specs.keys():
                print('{}" OD Pier: \n '
                  '   Ultimate Structural Axial Capacity: {}\n'
                  '   Ultimate Structural Lateral Capacity: {}\n'.format(self._pier_structural_specs[pier], self._pier_structural_specs[pier][0], self._pier_structural_specs[pier][1])

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
