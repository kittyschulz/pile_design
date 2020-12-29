import numpy as np
import math 

class Soil():
    """
    A class used represent a soil strata and the soil properties.

    Please see README documentation for an in-depth discussion of appropriate
    methods to obtain the material properties from both in-situ and laboratory
    tests. 

    Attributes
    ----------
    gamma : (flt)
        approximate unit weight of the soil.
    phi : (flt)
        approximate friction angle of the soil.
    cohesion : (flt)
        approximate cohesion of the soil.
    layer_depth : (flt)
        the depth from the ground surface (z = 0) to the
        top of the soil strata (z > 0).

    underlying_layer : (Soil)
        the soil strata which underlies this layer of soil (if applicable).
    layer_thickness : (flt)

    Methods
    -------
    insert(unit_weight, friction_angle, cohesion, layer_depth):
        Adds a new soil layer to the subsurface profile.
    """

    def __init__(self, unit_weight, friction_angle, cohesion, layer_depth, hazard=False, uscs=None):
        self.gamma = unit_weight
        self.phi = friction_angle
        self.cohesion = cohesion
        self.layer_depth = layer_depth
        self.hazard = hazard

        self.layer_thickness = None
        self.underlying_layer = None

        self.uscs = uscs
        # any organic soil needs to be designated as hazard=True.
        # will override an erroneous "False" designation.
        if self.uscs == "OL" or self.uscs == "OH":
            self.hazard = True

        self.Nq = None #(0.3359)*np.exp(0.1247*self.phi)

    def insert(self, unit_weight, friction_angle, cohesion, layer_depth, hazard=False, uscs=None):
        """
        Adds a new soil layer to the subsurface profile.

        Args:
            unit_weight : (flt)
                approximate unit weight of the soil.
            friction_angle : (flt)
                approximate friction angle of the soil.
            cohesion : (flt)
                approximate cohesion of the soil.
            layer_depth : (flt)
                the depth from the ground surface (z = 0) to the
                top of the soil strata (z > 0).

        Returns:
            None
        """
        if layer_depth > self.layer_depth:
            if self.underlying_layer is None:
                self.underlying_layer = Soil(unit_weight, friction_angle, cohesion, layer_depth)
                self.layer_thickness = layer_depth - self.layer_depth
            else:
                self.underlying_layer.insert(unit_weight, friction_angle, cohesion, layer_depth)