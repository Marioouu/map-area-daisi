import folium
import numpy as np
import streamlit as st
from pyproj import Geod
from folium.plugins import Draw
from streamlit_folium import st_folium

geod = Geod('+a=6378137 +f=0.0033528106647475126')


def area_calculator(coordinates):
    '''
    Calculates area given the coordinate array of boundaries

    Parameters:
    - coordinates (np.ndarray) : array of boundary points

    Return:
    - area float : Area in m^2
    - perim float: Perimeter in m
    '''
    coordinates = np.array(coordinates)
    lats = coordinates[:,1]
    lons = coordinates[:,0]

    # Compute:
    area, perim = geod.polygon_area_perimeter(lons, lats)

    return abs(area), abs(perim) # Positive is counterclockwise, the data is clockwise.

def st_ui():
    st.header('Area Calculator Daisi 📍')
    st.sidebar.subheader('Mode')
    boundary_mode = st.sidebar.radio('Metrics Calculation Mode', ['Single-Boundary Mode', 'Multi-Boundary Mode'], help="""
        Single-Boundary Mode: Calculate area and perimeter for a single boundary \n
        Multi-Boundary Mode: Calculate area and perimeter for multiple boundaries
    """)
    st.sidebar.subheader('Units')
    area_units = st.sidebar.radio('Area units', ['km\u00b2', 'm\u00b2'])
    perim_units = st.sidebar.radio('Perimeter units', ['km', 'm'])

    m = folium.Map(min_lot=-180,
                max_lot=180,
                max_bounds=True,
                min_zoom = 0, zoom_start = 1, max_zoom = 19)

    Draw(export=False,
        draw_options={'polyline': False, 'polygon': {'allowIntersection': False}, 'marker': False, 'rectangle': False, 'circle': False, 'circlemarker': False},
        edit_options={'poly': {'allowIntersection': False}}).add_to(m)

    st_data = st_folium(m, width = 700, height=500)
    if st_data and st_data['all_drawings'] and st_data['all_drawings'][0]['geometry']:
        if boundary_mode == 'Single-Boundary Mode':
            if len(st_data['all_drawings']) > 1:
                st.warning('Please clear all existing areas before proceeding!', icon="🗑️")
            area, perim = area_calculator(st_data['all_drawings'][-1]['geometry']['coordinates'][0])
        else:
            area = 0
            perim = 0
            for drawing in st_data['all_drawings']:
                t_area, t_perim = area_calculator(drawing['geometry']['coordinates'][0])
                area += t_area
                perim += t_perim

        if area_units == 'km\u00b2':
            area /= 1000000

        if perim_units == 'km':
            perim /= 1000

        st.title('Dimensions of the region:')
        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Area')
            st.write(area, area_units)
        with col2:
            st.subheader('Perimeter')
            st.write(perim, perim_units)

if __name__ == '__main__':
    st_ui()
