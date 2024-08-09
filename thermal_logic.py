import numpy as np
from scipy.integrate import odeint

class ThermalSimulation:
    def __init__(self, room_dimensions, material_properties):
        self.dimensions = room_dimensions
        self.properties = material_properties
        self.grid_size = (50, 50)
        
    def calculate_heat_transfer(self, initial_temp, time_steps):
        """Calculate heat transfer using finite difference method"""
        dx, dy = self.dimensions[0]/self.grid_size[0], self.dimensions[1]/self.grid_size[1]
        alpha = self.properties['thermal_diffusivity']
        dt = 0.25 * min(dx, dy)**2 / alpha
        
        # Initialize temperature grid
        T = np.ones(self.grid_size) * initial_temp
        
        # Apply boundary conditions
        T[0, :] = self.properties['source_temp']
        
        # Time evolution
        for t in range(time_steps):
            T_new = T.copy()
            for i in range(1, self.grid_size[0]-1):
                for j in range(1, self.grid_size[1]-1):
                    T_new[i,j] = T[i,j] + alpha * dt * (
                        (T[i+1,j] - 2*T[i,j] + T[i-1,j])/dx**2 +
                        (T[i,j+1] - 2*T[i,j] + T[i,j-1])/dy**2
                    )
            T = T_new
            
        return T
    
    def calculate_efficiency(self, temperature_distribution):
        """Calculate heating system efficiency"""
        mean_temp = np.mean(temperature_distribution)
        temp_uniformity = 1 - np.std(temperature_distribution)/mean_temp
        return {
            'mean_temperature': mean_temp,
            'uniformity': temp_uniformity,
            'efficiency': temp_uniformity * (mean_temp/self.properties['source_temp'])
        }
    
    def calculate_co2_emissions(self, power_consumption, duration):
        """Calculate CO2 emissions based on power consumption"""
        # Average CO2 emissions per kWh (varies by energy source)
        co2_per_kwh = {
            'natural_gas': 0.2,
            'electricity': 0.5,
            'wood': 0.1
        }
        
        return {
            source: consumption * co2_per_kwh[source] * duration 
            for source in co2_per_kwh
        }
