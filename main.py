import streamlit as st
import numpy as np
import plotly.graph_objects as go
from thermal_logic import ThermalSimulation
from visualization import HeatingVisualizer
from utils import validate_input, calculate_power_consumption, format_results
from materials_db import MaterialDatabase

def create_emissions_chart(hypocaust_data, modern_data, category):
    """Create a bar chart comparing emissions between systems"""
    systems = ['Hypocaust System', 'Modern System']
    values = [hypocaust_data[category], modern_data[category]]
    
    fig = go.Figure(data=[
        go.Bar(name=systems[0], x=[category], y=[values[0]], marker_color='#FF4B4B'),
        go.Bar(name=systems[1], x=[category], y=[values[1]], marker_color='#1F77B4')
    ])
    
    fig.update_layout(
        title=f'{category.replace("_", " ").title()} Comparison',
        yaxis_title='CO₂ Emissions (kg)',
        barmode='group',
        width=400,
        height=300
    )
    
    return fig

def main():
    st.title("Thermal Simulation: Hypocaust vs Modern Heating")
    
    # Initialize material database
    material_db = MaterialDatabase()
    
    # Sidebar for system parameters
    st.sidebar.header("System Parameters")
    
    # Construction Parameters
    with st.sidebar.expander("Construction Parameters", expanded=True):
        # Common parameters
        floor_thickness = st.number_input("Floor Thickness (m)", 0.1, 1.0, 0.2, 0.1)
        wall_thickness = st.number_input("Wall Thickness (m)", 0.1, 1.0, 0.3, 0.1)
        
        # Hypocaust parameters
        st.subheader("Hypocaust System")
        hypocaust_params = {
            'pillar_height': st.number_input("Pillar Height (m)", 0.3, 1.0, 0.5, 0.1),
            'pillar_spacing': st.number_input("Pillar Spacing (m)", 0.5, 2.0, 1.0, 0.1),
            'chamber_height': st.number_input("Underground Chamber Height (m)", 0.3, 1.0, 0.5, 0.1)
        }
        
        # Modern system parameters
        st.subheader("Modern System")
        modern_params = {
            'radiator_height': st.number_input("Radiator Height (m)", 0.3, 2.0, 1.0, 0.1),
            'radiator_width': st.number_input("Radiator Width (m)", 0.3, 2.0, 0.8, 0.1),
            'radiator_placement': st.number_input("Radiator Placement Height (m)", 0.1, 2.0, 0.3, 0.1),
            'pipe_diameter': st.number_input("Pipe Diameter (mm)", 10.0, 50.0, 15.0, 1.0) / 1000  # Convert to meters
        }

    # Room dimensions in an expander
    with st.sidebar.expander("Room Dimensions", expanded=True):
        room_size = {
            'length': st.number_input("Room Length (m)", 5, 20, 10),
            'width': st.number_input("Room Width (m)", 5, 20, 8),
            'height': st.number_input("Room Height (m)", 2, 5, 3)
        }

    # Energy Source Configuration
    with st.sidebar.expander("Energy Source", expanded=True):
        fuel_type = st.selectbox(
            "Fuel Type",
            ["wood", "natural_gas", "electricity"],
            format_func=lambda x: x.replace("_", " ").title()
        )
        
        source_temp = st.slider("Heat Source Temperature (°C)", 40, 100, 80)
        
        # Different efficiency ranges based on fuel type
        if fuel_type == "wood":
            efficiency = st.slider("Combustion Efficiency (%)", 50, 80, 65)
        elif fuel_type == "natural_gas":
            efficiency = st.slider("Combustion Efficiency (%)", 70, 95, 85)
        else:  # Electricity
            efficiency = st.slider("Conversion Efficiency (%)", 90, 100, 95)
        
        efficiency = efficiency / 100  # Convert to decimal

    # Material Properties
    with st.sidebar.expander("Material Properties", expanded=True):
        # Get materials by period
        ancient_materials = material_db.get_materials_by_period('ancient')
        modern_materials = material_db.get_materials_by_period('modern')
        
        # Hypocaust material selection
        st.subheader("Hypocaust System Materials")
        hypocaust_material = st.selectbox(
            "Select Hypocaust Material",
            list(ancient_materials['building'].keys()),
            format_func=lambda x: ancient_materials['building'][x]['name']
        )
        hypocaust_props = ancient_materials['building'][hypocaust_material].copy()
        hypocaust_props['material_type'] = hypocaust_material
        
        # Modern system material selection
        st.subheader("Modern System Materials")
        modern_material = st.selectbox(
            "Select Modern Material",
            list(modern_materials['building'].keys()),
            format_func=lambda x: modern_materials['building'][x]['name']
        )
        modern_props = modern_materials['building'][modern_material].copy()
        modern_props['material_type'] = modern_material

    # Simulation settings
    with st.sidebar.expander("Simulation Settings", expanded=True):
        time_steps = st.slider("Simulation Time Steps", 50, 200, 100)
        initial_temp = st.slider("Initial Temperature (°C)", 0, 30, 15)

    # Run simulation button
    if st.sidebar.button('Run Simulation'):
        # Update material properties with energy source settings
        for props in [hypocaust_props, modern_props]:
            props.update({
                'source_temp': source_temp,
                'efficiency': efficiency,
                'fuel_type': fuel_type
            })
        
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
        
        # Update system parameters
        hypocaust_sim.update_system_params(hypocaust_params)
        modern_sim.update_system_params(modern_params)
        
        # Calculate temperature distributions
        hypocaust_temp = hypocaust_sim.calculate_heat_transfer(initial_temp, time_steps)
        modern_temp = modern_sim.calculate_heat_transfer(initial_temp, time_steps)
        
        # Calculate metrics
        hypocaust_metrics = hypocaust_sim.calculate_efficiency(hypocaust_temp)
        modern_metrics = modern_sim.calculate_efficiency(modern_temp)
        
        # Create visualizer
        visualizer = HeatingVisualizer()
        
        # Display system diagrams side by side
        st.subheader("System Diagrams")
        col1, col2 = st.columns(2)
        with col1:
            st.write("Hypocaust System")
            st.image(visualizer.create_system_diagram('hypocaust'))
        with col2:
            st.write("Modern Heating System")
            st.image(visualizer.create_system_diagram('modern'))
        
        # Display heat distribution visualizations
        st.subheader("Heat Distribution")
        
        # 2D heat maps
        col3, col4 = st.columns(2)
        with col3:
            st.write("Hypocaust System - 2D Heat Map")
            st.pyplot(visualizer.create_heatmap(hypocaust_temp))
        with col4:
            st.write("Modern System - 2D Heat Map")
            st.pyplot(visualizer.create_heatmap(modern_temp))
        
        # 3D visualizations
        col5, col6 = st.columns(2)
        with col5:
            st.write("Hypocaust System - 3D Visualization")
            st.plotly_chart(visualizer.create_3d_heatmap(
                hypocaust_temp,
                (room_size['length'], room_size['width'])
            ))
        with col6:
            st.write("Modern System - 3D Visualization")
            st.plotly_chart(visualizer.create_3d_heatmap(
                modern_temp,
                (room_size['length'], room_size['width'])
            ))
        
        # Display metrics side by side
        st.subheader("System Performance")
        col7, col8 = st.columns(2)
        with col7:
            st.write("Hypocaust System Metrics:")
            hypocaust_formatted = format_results(hypocaust_metrics)
            for key, value in hypocaust_formatted.items():
                st.write(f"- {key.title()}: {value}")
        with col8:
            st.write("Modern System Metrics:")
            modern_formatted = format_results(modern_metrics)
            for key, value in modern_formatted.items():
                st.write(f"- {key.title()}: {value}")
        
        # Energy Retention Analysis
        st.header("Energy Retention Analysis")
        hypocaust_hours, hypocaust_retention = hypocaust_sim.calculate_hourly_energy_retention(initial_temp)
        modern_hours, modern_retention = modern_sim.calculate_hourly_energy_retention(initial_temp)
        
        # Create and display combined energy retention plot
        retention_plot = visualizer.create_energy_retention_plot(
            hypocaust_hours, hypocaust_retention, modern_retention
        )
        st.plotly_chart(retention_plot)
        
        # Calculate power consumption for both systems
        volume = room_size['length'] * room_size['width'] * room_size['height']
        temp_diff = source_temp - initial_temp
        
        hypocaust_power = calculate_power_consumption(volume, temp_diff, hypocaust_metrics['efficiency'])
        modern_power = calculate_power_consumption(volume, temp_diff, modern_metrics['efficiency'])
        
        # Display power consumption comparison
        st.subheader("Power Consumption")
        col9, col10 = st.columns(2)
        with col9:
            st.write(f"Hypocaust System: {hypocaust_power:.2f} kWh")
        with col10:
            st.write(f"Modern System: {modern_power:.2f} kWh")
        
        # Enhanced Environmental Impact Analysis
        st.header("Environmental Impact Analysis")
        
        # Calculate detailed emissions for both systems
        hypocaust_emissions = hypocaust_sim.calculate_co2_emissions(hypocaust_power, 24)
        modern_emissions = modern_sim.calculate_co2_emissions(modern_power, 24)
        
        # Create tabs for different environmental metrics
        tabs = st.tabs(["Operational Emissions", "Embodied Carbon", "Maintenance Impact", "Net Impact"])
        
        with tabs[0]:
            st.subheader("Operational CO₂ Emissions")
            col11, col12 = st.columns(2)
            with col11:
                st.write("Hypocaust System:")
                for source, value in hypocaust_emissions['operational'].items():
                    st.write(f"- {source.title()}: {value:.2f} kg CO₂e")
            with col12:
                st.write("Modern System:")
                for source, value in modern_emissions['operational'].items():
                    st.write(f"- {source.title()}: {value:.2f} kg CO₂e")
            
            # Calculate total operational emissions for visualization
            operational_data = {
                'hypocaust': {'operational': sum(hypocaust_emissions['operational'].values())},
                'modern': {'operational': sum(modern_emissions['operational'].values())}
            }
            st.plotly_chart(create_emissions_chart(
                operational_data['hypocaust'],
                operational_data['modern'],
                'operational'
            ))
        
        with tabs[1]:
            st.subheader("Embodied Carbon")
            col13, col14 = st.columns(2)
            with col13:
                st.write(f"Hypocaust System: {hypocaust_emissions['embodied_carbon']:.2f} kg CO₂e")
            with col14:
                st.write(f"Modern System: {modern_emissions['embodied_carbon']:.2f} kg CO₂e")
            
            embodied_data = {
                'hypocaust': {'embodied': hypocaust_emissions['embodied_carbon']},
                'modern': {'embodied': modern_emissions['embodied_carbon']}
            }
            st.plotly_chart(create_emissions_chart(
                embodied_data['hypocaust'],
                embodied_data['modern'],
                'embodied'
            ))
        
        with tabs[2]:
            st.subheader("Maintenance Impact")
            col15, col16 = st.columns(2)
            with col15:
                st.write(f"Hypocaust System: {hypocaust_emissions['maintenance_impact']:.2f} kg CO₂e/year")
            with col16:
                st.write(f"Modern System: {modern_emissions['maintenance_impact']:.2f} kg CO₂e/year")
            
            maintenance_data = {
                'hypocaust': {'maintenance': hypocaust_emissions['maintenance_impact']},
                'modern': {'maintenance': modern_emissions['maintenance_impact']}
            }
            st.plotly_chart(create_emissions_chart(
                maintenance_data['hypocaust'],
                maintenance_data['modern'],
                'maintenance'
            ))
        
        with tabs[3]:
            st.subheader("Net Environmental Impact")
            col17, col18 = st.columns(2)
            with col17:
                st.write("Hypocaust System:")
                st.write(f"- Total Emissions: {hypocaust_emissions['net_emissions']:.2f} kg CO₂e")
                st.write(f"- Carbon Offset: {hypocaust_emissions['carbon_offset']:.2f} kg CO₂e")
            with col18:
                st.write("Modern System:")
                st.write(f"- Total Emissions: {modern_emissions['net_emissions']:.2f} kg CO₂e")
                st.write(f"- Carbon Offset: {modern_emissions['carbon_offset']:.2f} kg CO₂e")
            
            net_data = {
                'hypocaust': {'net': hypocaust_emissions['net_emissions']},
                'modern': {'net': modern_emissions['net_emissions']}
            }
            st.plotly_chart(create_emissions_chart(
                net_data['hypocaust'],
                net_data['modern'],
                'net'
            ))

if __name__ == "__main__":
    main()
