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
            
    # [Previous methods remain unchanged...]
    
    def create_time_series_plot(self, time_steps, mean_temp_history, efficiency_history):
        """Create time series plot of temperature and efficiency evolution"""
        fig = go.Figure()
        
        # Add mean temperature trace
        fig.add_trace(go.Scatter(
            x=list(range(time_steps + 1)),
            y=mean_temp_history,
            name='Mean Temperature',
            line=dict(color='#ff7f0e', width=2),
            yaxis='y1'
        ))
        
        # Add efficiency trace
        fig.add_trace(go.Scatter(
            x=list(range(time_steps + 1)),
            y=[e * 100 for e in efficiency_history],  # Convert to percentage
            name='System Efficiency',
            line=dict(color='#1f77b4', width=2),
            yaxis='y2'
        ))
        
        # Update layout with dual y-axes
        fig.update_layout(
            title='Temperature and Efficiency Evolution',
            xaxis=dict(title='Time Steps'),
            yaxis=dict(
                title='Temperature (°C)',
                titlefont=dict(color='#ff7f0e'),
                tickfont=dict(color='#ff7f0e')
            ),
            yaxis2=dict(
                title='Efficiency (%)',
                titlefont=dict(color='#1f77b4'),
                tickfont=dict(color='#1f77b4'),
                anchor='x',
                overlaying='y',
                side='right'
            ),
            showlegend=True,
            legend=dict(
                yanchor='top',
                y=0.99,
                xanchor='left',
                x=0.01
            ),
            hovermode='x unified'
        )
        
        return fig
    
    def create_temperature_evolution_animation(self, T_history):
        """Create an animated heatmap of temperature evolution"""
        frames = []
        
        for temp_distribution in T_history:
            frame = go.Frame(
                data=[go.Heatmap(
                    z=temp_distribution,
                    colorscale='RdYlBu_r',
                    showscale=True,
                    colorbar=dict(title='Temperature (°C)')
                )]
            )
            frames.append(frame)
        
        # Create the base figure with initial frame
        fig = go.Figure(
            data=[go.Heatmap(
                z=T_history[0],
                colorscale='RdYlBu_r',
                showscale=True,
                colorbar=dict(title='Temperature (°C)')
            )],
            frames=frames
        )
        
        # Add animation controls
        fig.update_layout(
            title='Temperature Distribution Evolution',
            updatemenus=[dict(
                type='buttons',
                showactive=False,
                buttons=[
                    dict(label='Play',
                         method='animate',
                         args=[None, dict(frame=dict(duration=100, redraw=True), fromcurrent=True)]),
                    dict(label='Pause',
                         method='animate',
                         args=[[None], dict(frame=dict(duration=0, redraw=False), mode='immediate')])
                ]
            )],
            sliders=[dict(
                currentvalue=dict(prefix='Time Step: '),
                steps=[dict(
                    args=[[f.name], dict(mode='immediate', frame=dict(duration=0, redraw=False))],
                    label=str(k),
                    method='animate'
                ) for k, f in enumerate(frames)]
            )]
        )
        
        return fig
