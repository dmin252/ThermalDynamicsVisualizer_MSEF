import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import plotly.graph_objects as go
import os

class HeatingVisualizer:
    def __init__(self, width=800, height=400):
        self.width = width
        self.height = height
        self.font_size = 12
        try:
            self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", self.font_size)
        except:
            self.font = ImageFont.load_default()
    
    def create_3d_system_diagram(self, system_type):
        """Create 3D diagram of heating system"""
        # Create 3D figure
        fig = go.Figure()
        
        if system_type == 'hypocaust':
            # Add 3D room structure
            fig.add_trace(go.Mesh3d(
                x=[0,0,0,0,1,1,1,1],
                y=[0,1,1,0,0,1,1,0],
                z=[0,0,1,1,0,0,1,1],
                opacity=0.4,
                color='gray'
            ))
            
            # Add pillars
            for x in np.linspace(0.2, 0.8, 5):
                fig.add_trace(go.Mesh3d(
                    x=[x,x,x,x,x+0.05,x+0.05,x+0.05,x+0.05],
                    y=[0.2,0.3,0.3,0.2,0.2,0.3,0.3,0.2],
                    z=[0,0,0.3,0.3,0,0,0.3,0.3],
                    color='brown'
                ))
            
            # Add heat flow arrows using cone plots
            fig.add_trace(go.Cone(
                x=[0.2,0.4,0.6,0.8],
                y=[0.25,0.25,0.25,0.25],
                z=[0.1,0.1,0.1,0.1],
                u=[0,0,0,0],
                v=[0,0,0,0],
                w=[0.2,0.2,0.2,0.2],
                colorscale='Reds',
                showscale=False
            ))
            
        else:  # modern system
            # Add room structure
            fig.add_trace(go.Mesh3d(
                x=[0,0,0,0,1,1,1,1],
                y=[0,1,1,0,0,1,1,0],
                z=[0,0,1,1,0,0,1,1],
                opacity=0.4,
                color='gray'
            ))
            
            # Add radiator
            fig.add_trace(go.Mesh3d(
                x=[0.1,0.1,0.1,0.1,0.2,0.2,0.2,0.2],
                y=[0.3,0.7,0.7,0.3,0.3,0.7,0.7,0.3],
                z=[0.2,0.2,0.8,0.8,0.2,0.2,0.8,0.8],
                color='red'
            ))
            
            # Add convection arrows
            fig.add_trace(go.Cone(
                x=[0.3,0.5,0.7],
                y=[0.5,0.5,0.5],
                z=[0.6,0.8,0.6],
                u=[0.2,0,0.2],
                v=[0,0,0],
                w=[0.1,-0.1,-0.1],
                colorscale='Reds',
                showscale=False
            ))
        
        # Update layout
        fig.update_layout(
            title=f'3D {system_type.title()} System',
            scene=dict(
                aspectmode='cube',
                xaxis_title='Length',
                yaxis_title='Width',
                zaxis_title='Height'
            ),
            showlegend=True,
            width=800,
            height=600
        )
        
        return fig
        
    def _draw_label_with_leader(self, draw, start_pos, text, color='black'):
        """Draw text label with a leader line connecting to component"""
        text_width = draw.textlength(text, font=self.font)
        text_height = self.font_size
        
        # Calculate end position for leader line (offset from start position)
        end_x = start_pos[0] + (30 if start_pos[0] < self.width/2 else -30)
        end_y = start_pos[1] - 20
        
        # Draw leader line
        draw.line([start_pos[0], start_pos[1], end_x, end_y], fill=color, width=1)
        
        # Position text based on which side of the image we're on
        if start_pos[0] < self.width/2:
            text_pos = (end_x + 5, end_y - text_height/2)
        else:
            text_pos = (end_x - text_width - 5, end_y - text_height/2)
        
        # Draw text
        draw.text(text_pos, text, font=self.font, fill=color)
        
    def _draw_flow_arrow(self, draw, start_pos, end_pos, color='red', width=2):
        """Draw an arrow to indicate flow direction"""
        draw.line([start_pos, end_pos], fill=color, width=width)
        # Add arrowhead
        angle = np.arctan2(end_pos[1] - start_pos[1], end_pos[0] - start_pos[0])
        arrow_length = 10
        arrow_angle = np.pi/6  # 30 degrees
        
        # Calculate arrowhead points
        point1 = (
            end_pos[0] - arrow_length * np.cos(angle + arrow_angle),
            end_pos[1] - arrow_length * np.sin(angle + arrow_angle)
        )
        point2 = (
            end_pos[0] - arrow_length * np.cos(angle - arrow_angle),
            end_pos[1] - arrow_length * np.sin(angle - arrow_angle)
        )
        
        draw.line([end_pos, point1], fill=color, width=width)
        draw.line([end_pos, point2], fill=color, width=width)
        
    def create_system_diagram(self, system_type):
        """Create detailed diagram of heating system"""
        img = Image.new('RGB', (self.width, self.height), 'white')
        draw = ImageDraw.Draw(img)
        
        if system_type == 'hypocaust':
            self._draw_hypocaust(draw)
        else:
            self._draw_modern(draw)
            
        return img
    
    def create_heatmap(self, temperature_data):
        """Create detailed heatmap visualization of temperature distribution"""
        plt.figure(figsize=(10, 6))
        plt.imshow(temperature_data, cmap='RdYlBu_r', interpolation='bicubic')
        plt.colorbar(label='Temperature (°C)')
        
        # Add contour lines for better visualization of temperature gradients
        plt.contour(temperature_data, colors='black', alpha=0.5, 
                   levels=np.linspace(temperature_data.min(), temperature_data.max(), 10))
        
        # Convert plot to image
        fig = plt.gcf()
        plt.close()
        
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
            colorbar=dict(title='Temperature (°C)')
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
            height=600
        )
        
        return fig

    def create_energy_retention_plot(self, time_hours, hypocaust_retention, modern_retention):
        """Create energy retention comparison plot"""
        fig = go.Figure()
        
        # Add traces for both systems
        fig.add_trace(go.Scatter(
            x=time_hours,
            y=hypocaust_retention,
            name='Hypocaust System',
            line=dict(color='#FF4B4B', width=2),
            hovertemplate='Hour: %{x}<br>Retention: %{y:.1f}%<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=time_hours,
            y=modern_retention,
            name='Modern System',
            line=dict(color='#1F77B4', width=2),
            hovertemplate='Hour: %{x}<br>Retention: %{y:.1f}%<extra></extra>'
        ))
        
        # Update layout
        fig.update_layout(
            title='24-Hour Energy Retention Comparison',
            xaxis_title='Time (hours)',
            yaxis_title='Energy Retained (%)',
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            ),
            width=800,
            height=400
        )
        
        # Update axes
        fig.update_xaxes(range=[0, 24], dtick=2)
        fig.update_yaxes(range=[0, 100], dtick=10)
        
        return fig
