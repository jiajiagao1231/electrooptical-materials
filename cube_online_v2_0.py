import numpy as np
import skspatial
from skspatial.objects import Sphere
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import sys
import streamlit as st
from pyvista import * #Plotter as Plotter
import pyvista as pv


def is_run_via_streamlit():
	if "-no_streamlit" in sys.argv:
		print("detecting argument -no_streamlit")
		print("assuming this is not run via streamlit")
		return False
	else:
		print("assuming this is run via streamlit")
		return True



filename = st.text_input('Enter filename', 'testcube')
ax_grid = st.checkbox('Use ax_grid', False)
testvalue = st.slider('Select test value', min_value=-9., max_value=0.0, step=0.1, value=-4.0)
testvalue=10**testvalue


tolerance = st.slider('Select tolerance', min_value=-10., max_value=-1.0, step=0.1, value=-5.0)
tolerance=10**tolerance

if tolerance >= testvalue:
	tolerance = testvalue/10
	#tolerance = st.slider('Select tolerance', min_value=-10., max_value=-1.0, step=0.1, value=np.log10(tolerance))
	#tolerance=10**tolerance
	st.warning("Tolerance should be smaller than test value. Setting tolerance to test value/10")


# Create sliders for rotation angles
#azimuth = st.slider('Azimuth angle', min_value=0, max_value=360, step=5, value=90)
#elevation = st.slider('Elevation angle', min_value=0, max_value=90, step=5, value=20)
#roll = st.slider('Roll angle', min_value=0, max_value=360, step=5, value=0)
reduce_number_of_gridpoints = st.checkbox('Reduce number of gridpoints', 0)



#vielleicht todo zum plotten mit grid
is_bohr=False

is_angstrom=False

#filename="testcube"
#ax_grid=False

#testvalue = 10**(-4)
#tolerance = 10**(-5)  # define a tolerance for values close to testvalue


def v_coordinates(nth_v,n1,vec1, n2,vec2,n3, vec3, origin):
    #nth voxel defines ix, iy,iz
    def get_position_indices(nth_v, n1, n2, n3):
        ix, rem = divmod(nth_v, n2 * n3)
        iy, iz = divmod(rem, n3)
        return ix, iy, iz
    ix, iy, iz = get_position_indices(nth_v, n1, n2, n3)
    coordinates = np.array(origin) + ix * np.array(vec1) + iy * np.array(vec2) + iz * np.array(vec3) 
    return coordinates

@st.cache_data
def load_data(filename):
	with open(filename,"r") as inf:
		at_dict={}
		vol_dict={}
		v_dump=[]
		counter=0
		for line in inf:
			counter+=1
			if counter<=2:
				continue
			elif counter==4:
				#obda x coordinate
				n_v1, v11,v12,v13=[float(i) if '.' in i else int(i) for i in line.split()]
			elif counter==5:
				#obda y coordinate
				n_v2, v21,v22,v23=[float(i) if '.' in i else int(i) for i in line.split()]
			elif counter==6:
				#obda z coordinate
				n_v3, v31,v32,v33=[float(i) if '.' in i else int(i) for i in line.split()]
			elif counter==3:
				#origin of coordinate system
				natoms, o1, o2, o3=[float(i) if '.' in i else int(i) for i in line.split()]
				O=[o1,o2,o3]
			elif counter > 6 and counter <= 6+natoms:
				#, atomic number, charge, coordinates for atoms 
				at_dict[counter-6]=[int(line.split()[0]), float(line.split()[1]), [float(line.split()[2]),float(line.split()[3]), float(line.split()[4]) ]]
			elif counter > 6+natoms:
				v_dump.extend(list(map(float,line.split())))
			else:
				print(counter)
				raise ValueError("you should not be here")
		if n_v1 > 0.0 and n_v2 > 0.0 and n_v3 > 0.0:
			is_bohr=True
			is_angstrom=False
		elif n_v1 < 0.0 and n_v2 < 0.0 and n_v3 < 0.0:
			is_bohr=False
			is_angstrom=True
		else:
			raise ValueError("mixed units for different coordinates are not implemented -contact Ph.D. if this occurs or convert your cube file so that either angstrom or bohr is used but not both")
		v1 = [v11, v12, v13]
		v2 = [v21, v22, v23]
		v3 = [v31, v32, v33]
		matrix = np.array([v1, v2, v3])
		determinant = np.linalg.det(matrix)
		v_dump=np.array(v_dump)
		# Check if the determinant is close to zero
		if np.isclose(determinant, 0):
			raise ValueError("Vectors are linearly dependent")
		for i in range(len(v_dump)):
			#fill dictionary with coordinates and corresponding values
			vol_dict[i]=[v_coordinates(i,n_v1,v1, n_v2,v2,n_v3, v3, O),v_dump[i] ]
	
	coordinates = [v[0] for v in vol_dict.values()]
	# min and maximum values for plotting
	min_values = [min(coordinate[i] for coordinate in coordinates) for i in range(3)]
	max_values = [max(coordinate[i] for coordinate in coordinates) for i in range(3)]	
	return natoms, at_dict, vol_dict, coordinates, min_values, max_values


def plot_data(vol_dict, at_dict, testvalue, tolerance, colordict, xmin, xmax, ymin, ymax, zmin, zmax, ax_grid):
	fig=plt.figure()
	ax=fig.add_subplot(projection="3d" )
	#ax = Axes3D(fig)
	#ax.view_init(elev=elevation, azim=azimuth,roll=roll)
	# chose isovalue (positive)
	close_values_array = np.array([v[0] for v in vol_dict.values() if abs(v[1] - testvalue) <= tolerance])
	close_values_array2 = np.array([v[0] for v in vol_dict.values() if abs(v[1] + testvalue) <= tolerance])


	if len(close_values_array) <= 1 or len(close_values_array2) <= 1:
		raise ValueError("no values found within tolerance")
	#close_values_array.T necessary so that we do not have coordinates [xi,yi,zi], [xi+1,yi+1, zi+i], ... but all x all y all z

	for i in range(natoms):
		print(*at_dict[i+1][2])
		sphere=skspatial.objects.Sphere(at_dict[i+1][2], radius=0.5)
		current_color= colordict[at_dict[i+1][0]] if at_dict[i+1][0] in colordict.keys() else "cyan"
		sphere.plot_3d(ax, alpha=0.8, color=current_color)
		ax.plot(*at_dict[i+1][2], "x")

		if ax_grid!=True:
			ax.grid(False)
			ax.set_xticks([])
			ax.set_yticks([])
			ax.set_zticks([])
			ax.set_axis_off()
	ax.scatter(*close_values_array.T, color="blue", alpha=0.05, s=0.1)
	ax.scatter(*close_values_array2.T, color="red", alpha=0.1, s=0.1)
	ax.set_xlim([xmin, xmax])
	ax.set_ylim([ymin, ymax])
	ax.set_zlim([zmin, zmax])

	if is_run_via_streamlit():
		st.pyplot(fig)
	else:
		plt.show()
		plt.clf()
		plt.close()
		


def plot_data_pyvista(vol_dict, at_dict, testvalue, tolerance, colordict, xmin, xmax, ymin, ymax, zmin, zmax):
    # Create a PyVista plotter
    plotter = pv.Plotter()
    # chose isovalue (positive)
    close_values_array = np.array([v[0] for v in vol_dict.values() if abs(v[1] - testvalue) <= tolerance])
    close_values_array2 = np.array([v[0] for v in vol_dict.values() if abs(v[1] + testvalue) <= tolerance])
    if len(close_values_array) <= 1 or len(close_values_array2) <= 1:
		#try setting tolerance to testvalue/10
        raise ValueError("no values found within tolerance")
    # Plot spheres and points
    for i in range(natoms):
        sphere_center = at_dict[i+1][2]
        current_color = colordict[at_dict[i+1][0]] if at_dict[i+1][0] in colordict.keys() else "cyan"
        # Create a sphere at the atom's location
        sphere = pv.Sphere(center=sphere_center, radius=0.75)
        plotter.add_mesh(sphere, color=current_color, opacity=0.8)
    plotter.add_points(close_values_array, color="blue", opacity=0.5, point_size=1)
    plotter.add_points(close_values_array2, color="red", opacity=0.5, point_size=1)

    plotter.show()




natoms, at_dict, vol_dict, coordinates, min_values, max_values=load_data(filename)


colordict={
1: "gray",
6: "black",
7:"blue",
8:"red",
}

if not is_run_via_streamlit():
	for i in colordict.keys():
		print(f"atomic number {i} is colored {colordict[i]}")





xmin=ymin=zmin=min(min_values)
xmax=ymax=zmax=max(max_values)



correct_isovalue = False


if is_run_via_streamlit():
	plot_data_pyvista(vol_dict, at_dict, testvalue, tolerance, colordict, xmin, xmax, ymin, ymax, zmin, zmax)
	
else:
	while True:
		plot_data(vol_dict, at_dict, testvalue, tolerance, colordict, xmin, xmax, ymin, ymax, zmin, zmax, ax_grid)
		inputvalue_corretly_chosen=False
		
		while inputvalue_corretly_chosen!=True:
			inputvalue=input("Do you want to correct desired isovalue (y/n)")
			if inputvalue=="y" or inputvalue=="n":
				inputvalue_corretly_chosen=True
				if inputvalue=="n":
					exit()
			else:
				inputvalue_corretly_chosen=False
				print("please enter y or n")
		

			testvalue = float(input("Enter test value: "))
			tolerance = float(input("Enter tolerance: (recommended testvalue/10) "))
			plot_data(vol_dict, at_dict, testvalue, tolerance, colordict, xmin, xmax, ymin, ymax, zmin, zmax, ax_grid)



