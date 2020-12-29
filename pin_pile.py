import numpy as np
import math 
from soil import Soil

class PinPile():
    """
    A class used represent a series of pin piles and calculate the required
    design specifications based on the material properties of the pile and soil.

    Please see README documentation for an in-depth discussion of the calculations
    performed to obtain the pile design parameters. 

    Attributes
    ----------
    width : (flt)
        width of a single pin pile. 
    spacing : (flt)
        center-to-center spacing on pin piles.

    Methods
    -------
    design_depth(slide_mass, intact_soil):
        calculates the required design depth of the pin piles.

    bending_moment(slide_mass, intact_soil):
        calculates the bending moment of a pin pile. 
        Bending moment is used to determine the ultimate design depth.

    print_results():
        prints the calculated design specifications to the 
        terminal in a succinct narrative for easy interpretation.
    """

    def __init__(self, width, spacing):
        # pre-determined pile specifications
        self.width = width
        self.spacing = self.width*spacing

        # calculated parameters
        self.sigma_avg = None
        self.sigma_L_ds = None
        self.sum_T = None
        self.z_bar = None

        self.pile_depth = None
        self.depth_SF = None
        self.embedment = None

        self.moment = None
        self.moment_arm = None

    def calculate_min_depth(self, slide_mass, intact_soil):
        """
        Calculates the required design depth for the pin piles
        to retain the slide mass as defined by user. 

        Args:
            slide_mass : (Soil) 
            a Soil instance representing the slide mass.

            intact_soil : (Soil) 
            a Soil instance representing the intact soil
            layer the pile will bear in.

        Returns:
            None

        """
        if intact_soil.underlying_layer is not None:
            bearing_layer_depth = intact_soil.layer_thickness + intact_soil.layer_depth
        else:
            bearing_layer_depth = math.inf
        
        depth = np.linspace(0, slide_mass.layer_thickness, num=5)
        zB = depth/self.width
        kq = coeff_kq(slide_mass.phi, zB)
        kc = coeff_kc(slide_mass.phi, zB)
        
        sigma_V = slide_mass.gamma*depth
        sigma_L = (kc*slide_mass.cohesion)+(sigma_V*kq)
    
        z = (depth + np.append(0, depth[:-1]))/2
        resultant = (depth + np.append(0, depth[:-1]))*(sigma_V + np.append(0, sigma_V[:-1]))/2
        fz = resultant*z

        final_depth = intact_soil.layer_depth*self.width
        final_zb = intact_soil.layer_depth
        final_sigma_V = intact_soil.gamma*(final_depth-intact_soil.layer_depth) + slide_mass.gamma*intact_soil.layer_depth
        final_sigma_L = final_sigma_V*(coeff_kq(final_zb, intact_soil.phi)) + (coeff_kc(final_zb, intact_soil.phi))*intact_soil.cohesion
    
        self.sum_T = np.sum(resultant[1:])
        sum_fz = np.sum(fz[1:])

        self.z_bar = sum_fz/self.sum_T
    
        self.sigma_avg = (final_sigma_L - sigma_L[-1]) / (final_depth - intact_soil.layer_depth)
        self.sigma_L_ds = sigma_L[-1]
        
        min_d = intact_soil.layer_depth
        d1 = (-((sigma_L[-1]*2)/self.sigma_avg) + np.sqrt(((sigma_L[-1]*2)/self.sigma_avg)**2 - 4*(-(self.sum_T + (self.sigma_avg/2)*min_d**2 + sigma_L[-1]*min_d)/self.sigma_avg)))/2
        d_d1 = min_d - d1
        F1L1 = (sigma_L[-1]*d1* ( (intact_soil.layer_depth-self.z_bar) + (d1/2) )) + ( (self.sigma_avg/2)*(d1**2)*( (intact_soil.layer_depth-self.z_bar) + 2*(d1/3)) )
        F2L2 = ( (sigma_L[-1]+self.sigma_avg*d1)*d_d1*((intact_soil.layer_depth-self.z_bar)+d1+(d_d1/2)) ) + ( (self.sigma_avg/2)*(d_d1**2)*( (intact_soil.layer_depth-self.z_bar)+d1+(2*d_d1/3)) )
        
        while abs(1 - F1L1/F2L2) > 0.01:
            d1 = (-((sigma_L[-1]*2)/self.sigma_avg) + np.sqrt(((sigma_L[-1]*2)/self.sigma_avg)**2 - 4*(-(self.sum_T + (self.sigma_avg/2)*min_d**2 + sigma_L[-1]*min_d)/self.sigma_avg)))/2
            d_d1 = min_d - d1

            F1L1 = (sigma_L[-1]*d1* ( (intact_soil.layer_depth-self.z_bar) + (d1/2) )) + ( (self.sigma_avg/2)*(d1**2)*( (intact_soil.layer_depth-self.z_bar) + 2*(d1/3)) )
            
            F2L2 = ( (sigma_L[-1]+self.sigma_avg*d1)*d_d1*((intact_soil.layer_depth-self.z_bar)+d1+(d_d1/2)) ) + ( (self.sigma_avg/2)*(d_d1**2)*( (intact_soil.layer_depth-self.z_bar)+d1+(2*d_d1/3)) )
            if F2L2 > F1L1:
                min_d -= 0.01
            else:
                min_d += 0.01
        
        self.pile_depth = min_d
        self.depth_SF = 1.3*self.pile_depth
        self.embedment = self.depth_SF + intact_soil.layer_depth
        
        if self.pile_depth > bearing_layer_depth:
            calculate_min_depth(slide_mass, intact_soil.underlying_layer)
    
    def bending_moment(self, slide_mass, intact_soil):
        """
        performs bending moment calculation.

        Args:
            slide_mass : (Soil) 
            a Soil instance representing the slide mass.

            intact_soil : (Soil) 
            a Soil instance representing the intact soil
            layer the pile will bear in.

        Returns:
            None
        """
        x = (self.sigma_L_ds + np.sqrt(self.sigma_L_ds**2 + 2*self.sigma_avg*self.sum_T))/(2*self.sigma_avg)
        self.moment = (self.sum_T*(x+intact_soil.layer_depth-self.z_bar) - ((self.sigma_avg*(x**3))/6) - ((self.sigma_L_ds*(x**2))/2))/1000
        self.moment_arm = x+intact_soil.layer_depth
        
    def print_results(self):
        """
        prints results of the results of the pin pile calculations to the terminal
        in a narrative fashion for quick, easy interpretation.
        """

        print("The pin pile retaining wall should have a minimum"
              " total embedment of {} feet and a minimum embedment"
              " below the failure surface of {} feet.\n".format(round(self.embedment,2), round(self.pile_depth,2)))
        
        print("Pin piles should have a minimum diameter of {} inches"
              " and a maximum center-on-center spacing of {} pier diameters\n".format(self.width*12, self.spacing))
        
        print("The force per unit width of pile is {} kips per foot"
              " located at {} feet below top of pile\n".format(round(self.sum_T/1000,2), round(self.z_bar,2)))
              
        print("The lateral resistance per linear foot is {} kips per foot\n".format(round(self.sum_T/2000,2)))
              
        print("The pin pile wall may be designed using a maximum bending"
              " moment of {} kip-feet per foot located at {} feet below"
              " the top of the pin pile\n".format(round(self.moment,2), round(self.moment_arm,2)))


    def design_depth(self, soil_profile):
        """
        Calculates and returns required design depth for the pin piles
        to retain the slide mass as defined by user. 

        Args:
            soil_profile : (Soil) 
            a Soil instance representing the subsurface profile.

        Returns:
            None
        """
        slide_mass = soil_profile
        intact_soil = soil_profile.underlying_layer

        self.calculate_min_depth(slide_mass, intact_soil)
        self.bending_moment(slide_mass, intact_soil)

def coeff_kq(phi, x):
    """
    Determines appropriate K_q coefficient based on friction angle and depth.
    
    Please see README documentation for an in-depth discussion of appropriate
    methods to obtain the material properties from both in-situ and laboratory
    tests. 

    Args:
        phi (flt): friction angle of soil strata. 
        x (flt): nominal depth. 

    Returns:
        kq (float): K_q coefficient of soil. 
    """

    x += 0.1
    if phi > 47.5:
        kq = 222	
    elif phi > 42.5:
        kq = -0.0298*x**2 + 3.3082*x + 18.456
    elif phi > 37.5:		
        kq = -0.0305*x**2 + 1.8933*x + 11.695
    elif phi > 32.5:				
        kq = -0.0263*x**2 + 1.2454*x + 7.997
    elif phi > 27.5:				
        kq = -0.0215*x**2 + 0.8025*x + 5.3649
    elif phi > 22.5:				
        kq = 0.001*x**3 - 0.039*x**2 + 0.6159*x + 3.7461
    elif phi > 17.5:				
        kq = 0.0005*x**3 - 0.0216*x**2 + 0.3756*x + 2.4859
    elif phi > 12.5:				
        kq = 0.0004*x**3 - 0.0174*x**2 + 0.2452*x + 1.6662
    elif phi > 7.5:				
        kq = 0.0002*x**3 - 0.0087*x**2 + 0.1264*x + 1.0113
    elif phi > 2.5:				
        kq = -0.0008*x**2 + 0.0279*x + 0.4913
    else:				
        kq = 0
    return kq

def coeff_kc(phi, x):
    """
    Determines appropriate K_q coefficient based on friction angle and depth.
    
    Please see README documentation for an in-depth discussion of appropriate
    methods to obtain the material properties from both in-situ and laboratory
    tests. 

    Args:
        phi (flt): friction angle of soil strata. 
        x (flt): nominal depth. 

    Returns:
        kc (float): K_c coefficient of soil. 
    """

    x += 0.1 
    if phi > 47.5:
        kc = 759	
    elif phi > 42.5:			
        kc = -0.5208*x**2 + 27.815*x + 16.123
    elif phi > 37.5:				
        kc = -0.38*x**2 + 15.569*x + 17.044		
    elif phi > 32.5:		
        kc = 0.0114*x**3 - 0.5662*x**2 + 11.083*x + 11.353	
    elif phi > 27.5:			
        kc = 0.014*x**3 - 0.5459*x**2 + 7.7909*x + 8.6346	
    elif phi > 22.5:			
        kc = 7.0512*np.log(x) + 13.073
    elif phi > 17.5:				
        kc = 4.4885*np.log(x) + 10.248	
    elif phi > 12.5:			
        kc = 3.0067*np.log(x) + 8.2786	
    elif phi > 7.5:			
        kc = 1.9716*np.log(x) + 7.1678
    elif phi > 2.5:
        kc = 1.5053*np.log(x) + 5.7476
    else:		
        kc = 0.0019*x**3 - 0.073*x**2 + 0.9069*x + 4.0468
    return kc