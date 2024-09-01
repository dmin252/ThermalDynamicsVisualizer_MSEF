import streamlit as st
import numpy as np
from thermal_logic import ThermalSimulation
from visualization import HeatingVisualizer
from utils import validate_input, calculate_power_consumption, format_results
from materials_db import MaterialDatabase

def main():
    st.title("Thermal Simulation: Hypocaust vs Modern Heating")
    
    # Initialize material database
    material_db = MaterialDatabase()
    
    # Sidebar for system parameters
    st.sidebar.header("System Parameters")
    
    # [Previous sidebar code remains unchanged...]
    
    # Run simulation button
    if st.sidebar.button('Run Simulation'):
        # Get material properties for simulations
        hypocaust_props = material_db.get_building_material(hypocaust_material).copy()
        modern_props = material_db.get_building_material(modern_material).copy()
        
        # Calculate thermal diffusivity for both materials
        hypocaust_props['thermal_diffusivity'] = material_db.calculate_thermal_diffusivity(hypocaust_props)
        modern_props['thermal_diffusivity'] = material_db.calculate_thermal_diffusivity(modern_props)
        
        # Add source temperature to properties
        hypocaust_props['source_temp'] = source_temp
        modern_props['source_temp'] = source_temp

        # Create simulation instances
        hypocaust_sim = ThermalSimulation(
            (room_size['length'], room_size['width']),
            hypocaust_props,
            system_type='hypocaust'
        )
        modern_sim = ThermalSimulation(
            (room_size['length'], room_size['width']),
            modern_props,
            system_type='modern'
        )

        # Time-series Analysis Section
        st.header("Time-series Analysis")
        
        # Run simulations with time-series tracking
        hypocaust_temp, h_temp_history, h_mean_temp_history, h_efficiency_history = \
            hypocaust_sim.calculate_heat_transfer(initial_temp, time_steps)
        modern_temp, m_temp_history, m_mean_temp_history, m_efficiency_history = \
            modern_sim.calculate_heat_transfer(initial_temp, time_steps)
        
        # Create visualizer instance
        visualizer = HeatingVisualizer()
        
        # Display time-series plots
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Hypocaust System Evolution")
            st.plotly_chart(visualizer.create_time_series_plot(
                time_steps, h_mean_temp_history, h_efficiency_history
            ))
            
        with col2:
            st.subheader("Modern System Evolution")
            st.plotly_chart(visualizer.create_time_series_plot(
                time_steps, m_mean_temp_history, m_efficiency_history
            ))
        
        # Temperature Evolution Animation
        st.header("Temperature Distribution Evolution")
        system_choice = st.radio(
            "Select System to Visualize",
            ["Hypocaust", "Modern"]
        )
        
        if system_choice == "Hypocaust":
            st.plotly_chart(visualizer.create_temperature_evolution_animation(h_temp_history))
        else:
            st.plotly_chart(visualizer.create_temperature_evolution_animation(m_temp_history))
        
        # Previous visualization code remains...
        
        # System Comparison Section
        st.header("System Comparison")
        
        # Calculate time to reach target temperature
        target_temp = initial_temp + 0.7 * (source_temp - initial_temp)  # 70% of max temperature rise
        time_to_target_h = next((i for i, temp in enumerate(h_mean_temp_history) if temp >= target_temp), time_steps)
        time_to_target_m = next((i for i, temp in enumerate(m_mean_temp_history) if temp >= target_temp), time_steps)
        
        metrics_col1, metrics_col2 = st.columns(2)
        
        with metrics_col1:
            st.metric("Time to Target (Hypocaust)", f"{time_to_target_h} steps")
            st.metric("Final Efficiency (Hypocaust)", f"{h_efficiency_history[-1]*100:.1f}%")
            
        with metrics_col2:
            st.metric("Time to Target (Modern)", f"{time_to_target_m} steps")
            st.metric("Final Efficiency (Modern)", f"{m_efficiency_history[-1]*100:.1f}%")
        
        # Previous environmental impact and material comparison sections remain...

if __name__ == "__main__":
    main()
