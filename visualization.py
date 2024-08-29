import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import cairosvg
from io import BytesIO

class HeatingVisualizer:
    def __init__(self, width=800, height=400):
        self.width = width
        self.height = height
        self.font_size = 12
        try:
            self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", self.font_size)
        except:
            self.font = ImageFont.load_default()

    def create_time_series_plot(self, hypocaust_data, modern_data):
        """Create interactive time series comparison plot with enhanced features"""
        fig = make_subplots(
            rows=5, cols=1,
            subplot_titles=(
                'Mean Temperature Over Time',
                'Temperature Change Rate (°C/hour)',
                'Energy Retention Over Time',
                'Temperature Uniformity',
                'System Efficiency'
            ),
            vertical_spacing=0.08,
            row_heights=[0.2, 0.2, 0.2, 0.2, 0.2]
        )
        
        # Extract time data
        time_steps_h = [d['hours_elapsed'] for d in hypocaust_data]
        time_steps_m = [d['hours_elapsed'] for d in modern_data]
        
        # Define metrics to plot
        metrics = [
            ('mean_temperature', 'Temperature (°C)'),
            ('temp_change_rate', 'Rate (°C/hour)'),
            ('energy_retention', 'Retention Ratio'),
            ('uniformity', 'Uniformity'),
            ('efficiency', 'Efficiency')
        ]
        
        # Colors for systems
        colors = {'hypocaust': 'firebrick', 'modern': 'royalblue'}
        
        # Add traces for each metric
        for row, (metric, label) in enumerate(metrics, 1):
            # Hypocaust system data
            hypocaust_y = [d[metric] for d in hypocaust_data]
            fig.add_trace(
                go.Scatter(
                    x=time_steps_h,
                    y=hypocaust_y,
                    name=f'Hypocaust {metric.replace("_", " ").title()}',
                    line=dict(color=colors['hypocaust']),
                    hovertemplate=(
                        f"Time: %{{x:.1f}} hours<br>"
                        f"{label}: %{{y:.2f}}<br>"
                        f"<extra>Hypocaust System</extra>"
                    )
                ),
                row=row, col=1
            )
            
            # Modern system data
            modern_y = [d[metric] for d in modern_data]
            fig.add_trace(
                go.Scatter(
                    x=time_steps_m,
                    y=modern_y,
                    name=f'Modern {metric.replace("_", " ").title()}',
                    line=dict(color=colors['modern']),
                    hovertemplate=(
                        f"Time: %{{x:.1f}} hours<br>"
                        f"{label}: %{{y:.2f}}<br>"
                        f"<extra>Modern System</extra>"
                    )
                ),
                row=row, col=1
            )
            
            # Add annotations for critical points
            if metric == 'efficiency':
                max_h_idx = np.argmax(hypocaust_y)
                max_m_idx = np.argmax(modern_y)
                
                # Add annotation for maximum efficiency points
                fig.add_annotation(
                    x=time_steps_h[max_h_idx], y=hypocaust_y[max_h_idx],
                    text="Peak Efficiency",
                    showarrow=True,
                    arrowhead=1,
                    row=row, col=1,
                    font=dict(color=colors['hypocaust'])
                )
                fig.add_annotation(
                    x=time_steps_m[max_m_idx], y=modern_y[max_m_idx],
                    text="Peak Efficiency",
                    showarrow=True,
                    arrowhead=1,
                    row=row, col=1,
                    font=dict(color=colors['modern'])
                )
            
            # Update y-axis labels
            fig.update_yaxes(title_text=label, row=row, col=1)
        
        # Update layout
        fig.update_layout(
            height=1200,
            showlegend=True,
            title_text="Detailed Time Series Analysis of Heating Systems",
            xaxis5_title="Time (hours)",
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            )
        )
        
        # Add vertical guidelines at critical points
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
        
        return fig

    # [Previous methods remain unchanged...]
    
    def create_system_diagram(self, system_type):
        """Load and process SVG template for system visualization"""
        template_path = f"assets/{system_type}_template.svg"
        
        try:
            # Read the SVG template
            with open(template_path, 'r') as f:
                svg_content = f.read()
            
            # Convert SVG to PNG using cairosvg
            png_data = cairosvg.svg2png(bytestring=svg_content.encode('utf-8'))
            
            # Create PIL Image from PNG data
            image = Image.open(BytesIO(png_data))
            return image
            
        except Exception as e:
            print(f"Error creating system diagram: {e}")
            # Create a blank image with error message
            img = Image.new('RGB', (self.width, self.height), 'white')
            draw = ImageDraw.Draw(img)
            draw.text((self.width//2, self.height//2), "Error loading diagram", 
                     fill='red', font=self.font, anchor="mm")
            return img

    def create_heatmap(self, temperature_data):
        """Create detailed heatmap visualization of temperature distribution"""
        fig, ax = plt.subplots(figsize=(10, 6))
        im = ax.imshow(temperature_data, cmap='RdYlBu_r', interpolation='bicubic')
        plt.colorbar(im, ax=ax, label='Temperature (°C)')
        
        # Add contour lines for better visualization of temperature gradients
        cs = ax.contour(temperature_data, colors='black', alpha=0.5, 
                     levels=np.linspace(temperature_data.min(), temperature_data.max(), 10))
        
        ax.set_title('Temperature Distribution')
        ax.set_xlabel('Room Width')
        ax.set_ylabel('Room Height')
        
        # Ensure the plot is properly formatted for Streamlit
        plt.tight_layout()
        
        return fig

    def create_3d_heatmap(self, temperature_data, room_dimensions):
        """Create 3D surface plot of temperature distribution"""
        # Create coordinate grids
        x = np.linspace(0, room_dimensions[0], temperature_data.shape[1])
        y = np.linspace(0, room_dimensions[1], temperature_data.shape[0])
        X, Y = np.meshgrid(x, y)
        
        # Create 3D surface plot
        fig = go.Figure(data=[go.Surface(
            x=X,
            y=Y,
            z=temperature_data,
            colorscale='RdYlBu_r',
            colorbar=dict(
                title='Temperature (°C)',
                titleside='right'
            )
        )])
        
        # Update layout for better visualization
        fig.update_layout(
            title='3D Temperature Distribution',
            scene=dict(
                xaxis_title='Room Length (m)',
                yaxis_title='Room Width (m)',
                zaxis_title='Temperature (°C)',
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.2)
                )
            ),
            width=800,
            height=600,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        
        return fig
