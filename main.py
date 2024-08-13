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
    
    # Room dimensions in an expander
    with st.sidebar.expander("Room Dimensions", expanded=True):
        room_size = {
            'length': st.number_input("Room Length (m)", 5, 20, 10),
            'width': st.number_input("Room Width (m)", 5, 20, 8),
            'height': st.number_input("Room Height (m)", 2, 5, 3)
        }

    # Material selection in an expander
    with st.sidebar.expander("Material Properties", expanded=True):
        # Separate materials by period for the selected system
        ancient_materials = material_db.get_materials_by_period('ancient')
        modern_materials = material_db.get_materials_by_period('modern')
        
        # Create lists of material names for dropdowns
        ancient_building_materials = list(ancient_materials['building'].keys())
        modern_building_materials = list(modern_materials['building'].keys())
        
        # Material selection dropdowns
        hypocaust_material = st.selectbox(
            "Hypocaust System Material",
            ancient_building_materials,
            format_func=lambda x: material_db.get_building_material(x)['name']
        )
        modern_material = st.selectbox(
            "Modern System Material",
            modern_building_materials,
            format_func=lambda x: material_db.get_building_material(x)['name']
        )
        
        # Display selected material properties
        if hypocaust_material:
            mat = material_db.get_building_material(hypocaust_material)
            st.write("Hypocaust Material Properties:")
            st.write(f"- Thermal Conductivity: {mat['thermal_conductivity']} W/mK")
            st.write(f"- Thermal Resistance: {mat['thermal_resistance']} m²K/W")
            st.write(f"- Emissivity: {mat['emissivity']}")
        
        if modern_material:
            mat = material_db.get_building_material(modern_material)
            st.write("Modern Material Properties:")
            st.write(f"- Thermal Conductivity: {mat['thermal_conductivity']} W/mK")
            st.write(f"- Thermal Resistance: {mat['thermal_resistance']} m²K/W")
            st.write(f"- Emissivity: {mat['emissivity']}")

    # Simulation settings in an expander
    with st.sidebar.expander("Simulation Settings", expanded=True):
        time_steps = st.slider("Simulation Time Steps", 50, 200, 100)
        initial_temp = st.slider("Initial Temperature (°C)", 0, 30, 15)
        source_temp = st.slider("Heat Source Temperature (°C)", 40, 100, 80)

    # Run simulation button
    if st.sidebar.button('Run Simulation'):
        # Get material properties for simulations
        hypocaust_props = material_db.get_building_material(hypocaust_material)
        modern_props = material_db.get_building_material(modern_material)
        
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

        # Display results in two columns
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Hypocaust System")
            hypocaust_temp = hypocaust_sim.calculate_heat_transfer(initial_temp, time_steps)
            hypocaust_metrics = hypocaust_sim.calculate_efficiency(hypocaust_temp)
            
            # Visualization
            visualizer = HeatingVisualizer()
            st.image(visualizer.create_system_diagram('hypocaust'))
            st.pyplot(visualizer.create_heatmap(hypocaust_temp))
            
            # Metrics
            st.write("System Metrics:")
            hypocaust_formatted = format_results(hypocaust_metrics)
            for key, value in hypocaust_formatted.items():
                st.write(f"- {key.title()}: {value}")

        with col2:
            st.subheader("Modern Heating System")
            modern_temp = modern_sim.calculate_heat_transfer(initial_temp, time_steps)
            modern_metrics = modern_sim.calculate_efficiency(modern_temp)
            
            # Visualization
            st.image(visualizer.create_system_diagram('modern'))
            st.pyplot(visualizer.create_heatmap(modern_temp))
            
            # Metrics
            st.write("System Metrics:")
            modern_formatted = format_results(modern_metrics)
            for key, value in modern_formatted.items():
                st.write(f"- {key.title()}: {value}")

        # Environmental Impact Analysis
        st.header("Environmental Impact")
        
        volume = room_size['length'] * room_size['width'] * room_size['height']
        temp_diff = source_temp - initial_temp
        
        power_hypocaust = calculate_power_consumption(
            volume, temp_diff, hypocaust_metrics['efficiency']
        )
        power_modern = calculate_power_consumption(
            volume, temp_diff, modern_metrics['efficiency']
        )
        
        # Calculate emissions
        duration = 24  # hours
        hypocaust_emissions = hypocaust_sim.calculate_co2_emissions(power_hypocaust, duration)
        modern_emissions = modern_sim.calculate_co2_emissions(power_modern, duration)
        
        # Display emissions comparison
        st.subheader("Daily CO2 Emissions (kg)")
        emissions_data = {
            'Hypocaust': hypocaust_emissions,
            'Modern': modern_emissions
        }
        
        for system, emissions in emissions_data.items():
            st.write(f"\n{system} System:")
            for source, value in emissions.items():
                st.write(f"- {source.title()}: {value:.2f} kg CO2")

        # Material Comparison
        st.header("Material Comparison")
        comparison = material_db.get_material_comparison(hypocaust_material, modern_material)
        if comparison:
            st.write("Relative Performance (Hypocaust vs Modern):")
            for key, value in comparison.items():
                st.write(f"- {key.replace('_', ' ').title()}: {value:.2f}x")

if __name__ == "__main__":
    main()
