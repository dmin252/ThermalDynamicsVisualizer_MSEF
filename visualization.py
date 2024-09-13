import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import plotly.graph_objects as go
import os
from datetime import datetime, timedelta

class HeatingVisualizer:
    def __init__(self, width=800, height=400):
        self.width = width
        self.height = height
        self.font_size = 12
        try:
            self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", self.font_size)
        except:
            self.font = ImageFont.load_default()
        
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
        
    def _draw_hypocaust(self, draw):
        """Draw detailed hypocaust system diagram with annotations"""
        # Room outline
        draw.rectangle([50, 50, 750, 350], outline='black')
        
        # Underground chamber (Hypocaustum)
        draw.rectangle([50, 300, 750, 350], outline='black', fill='brown')
        self._draw_label_with_leader(draw, (400, 325), "Hypocaustum (Hollow Space)", "white")
        
        # Floor tiles (Suspensura)
        draw.rectangle([50, 290, 750, 300], fill='gray', outline='black')
        self._draw_label_with_leader(draw, (200, 295), "Suspensura (Floor Tiles)")
        
        # Pillars (Pilae) in staggered arrangement
        pillar_positions = [(100, 250), (200, 270), (300, 250), (400, 270), 
                          (500, 250), (600, 270), (700, 250)]
        for x, y in pillar_positions:
            draw.rectangle([x, y, x+20, 300], fill='gray')
        self._draw_label_with_leader(draw, (pillar_positions[2][0], pillar_positions[2][1]), 
                                   "Pilae (Support Pillars)")
        
        # Underground furnace (Praefurnium)
        draw.rectangle([50, 350, 150, 380], fill='red')
        draw.polygon([(70, 350), (90, 330), (110, 350)], fill='orange')
        self._draw_label_with_leader(draw, (100, 365), "Praefurnium (Furnace)", "white")
        
        # Wall ducts (Tubuli)
        for x in [60, 740]:
            for y in range(100, 301, 50):
                draw.rectangle([x-5, y, x+5, y+40], fill='orange', outline='black')
        self._draw_label_with_leader(draw, (60, 150), "Tubuli (Wall Ducts)")
        
        # Hot air flow patterns
        flow_points = [
            [(150, 340), (300, 320)],
            [(350, 320), (500, 340)],
            [(550, 340), (700, 320)],
            [(100, 200), (100, 150)],  # Vertical flow in tubuli
            [(700, 200), (700, 150)]
        ]
        for start, end in flow_points:
            self._draw_flow_arrow(draw, start, end, 'red', 2)
        
    def _draw_modern(self, draw):
        """Draw detailed modern heating system diagram with annotations"""
        # Room outline
        draw.rectangle([50, 50, 750, 350], outline='black')
        
        # Radiator with fins
        base_x, base_y = 100, 100
        draw.rectangle([base_x, base_y, base_x+50, base_y+200], fill='red', outline='black')
        self._draw_label_with_leader(draw, (base_x+25, base_y+100), "Radiator Unit")
        
        # Add radiator fins
        for y in range(base_y+20, base_y+200, 20):
            draw.rectangle([base_x-10, y, base_x+60, y+5], fill='red', outline='black')
        
        # Supply and return pipes
        draw.rectangle([base_x+20, base_y-30, base_x+30, base_y], fill='red')
        draw.rectangle([base_x+20, base_y+200, base_x+30, base_y+230], fill='blue')
        self._draw_label_with_leader(draw, (base_x+25, base_y-15), "Supply Pipe")
        self._draw_label_with_leader(draw, (base_x+25, base_y+215), "Return Pipe")
        
        # Temperature control valve
        valve_y = base_y+200
        draw.ellipse([base_x+15, valve_y+5, base_x+35, valve_y+25], fill='gray')
        self._draw_label_with_leader(draw, (base_x+25, valve_y+15), "Control Valve")
        
        # Wall mounting points
        mount_points = [(base_x-10, base_y+50), (base_x-10, base_y+150)]
        for x, y in mount_points:
            draw.rectangle([x-5, y-5, x+5, y+5], fill='gray')
        self._draw_label_with_leader(draw, mount_points[0], "Wall Mount")
        
        # Room air circulation patterns
        circulation_points = [
            [(160, 150), (200, 120)],  # Rising hot air
            [(200, 120), (300, 100)],  # Ceiling flow
            [(300, 100), (400, 120)],
            [(400, 120), (400, 200)],  # Falling cool air
            [(400, 200), (300, 220)],
            [(300, 220), (200, 200)]   # Return flow
        ]
        for start, end in circulation_points:
            self._draw_flow_arrow(draw, start, end, 'blue', 2)
        
        # Add legend
        legend_y = 320
        # Hot air flow
        draw.line([600, legend_y, 650, legend_y], fill='red', width=2)
        draw.text((660, legend_y-8), "Hot Air Flow", font=self.font, fill='black')
        # Cold air flow
        draw.line([600, legend_y+20, 650, legend_y+20], fill='blue', width=2)
        draw.text((660, legend_y+12), "Cold Air Flow", font=self.font, fill='black')
        
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
        """Create energy retention comparison plot with enhanced tooltips"""
        fig = go.Figure()
        
        # Generate time of day labels
        start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        time_labels = [(start_time + timedelta(hours=h)).strftime('%H:%M') for h in time_hours]
        
        # Add traces for both systems with enhanced tooltips
        fig.add_trace(go.Scatter(
            x=time_hours,
            y=hypocaust_retention,
            name='Hypocaust System',
            line=dict(color='#FF4B4B', width=2),
            hovertemplate=(
                '<b>Hypocaust System</b><br>' +
                'Time: %{customdata}<br>' +
                'Retention: %{y:.1f}%<br>' +
                'Baseline: 85% ± 10%<extra></extra>'
            ),
            customdata=time_labels
        ))
        
        fig.add_trace(go.Scatter(
            x=time_hours,
            y=modern_retention,
            name='Modern System',
            line=dict(color='#1F77B4', width=2),
            hovertemplate=(
                '<b>Modern System</b><br>' +
                'Time: %{customdata}<br>' +
                'Retention: %{y:.1f}%<br>' +
                'Baseline: 75% ± 15%<extra></extra>'
            ),
            customdata=time_labels
        ))
        
        # Update layout with enhanced styling
        fig.update_layout(
            title={
                'text': '24-Hour Energy Retention Comparison',
                'font': dict(size=24)
            },
            xaxis_title='Time (hours)',
            yaxis_title='Energy Retained (%)',
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor='rgba(255, 255, 255, 0.8)',
                bordercolor='rgba(0, 0, 0, 0.2)',
                borderwidth=1
            ),
            width=800,
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        # Update axes with enhanced styling
        fig.update_xaxes(
            range=[0, 24],
            dtick=2,
            gridcolor='rgba(0, 0, 0, 0.1)',
            showline=True,
            linewidth=1,
            linecolor='black',
            ticktext=time_labels[::2],  # Show every 2 hours
            tickvals=list(range(0, 25, 2))
        )
        
        fig.update_yaxes(
            range=[0, 100],
            dtick=10,
            gridcolor='rgba(0, 0, 0, 0.1)',
            showline=True,
            linewidth=1,
            linecolor='black'
        )
        
        # Add a rectangular shape to highlight the baseline ranges
        fig.add_shape(
            type="rect",
            x0=0,
            x1=24,
            y0=75,
            y1=95,
            fillcolor="rgba(255, 75, 75, 0.1)",
            line=dict(width=0),
            name="Hypocaust Range"
        )
        
        fig.add_shape(
            type="rect",
            x0=0,
            x1=24,
            y0=60,
            y1=90,
            fillcolor="rgba(31, 119, 180, 0.1)",
            line=dict(width=0),
            name="Modern Range"
        )
        
        return fig