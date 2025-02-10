"""
CLIPPING A NETCDF FILE BY USING A SHAPEFILE

- This code will clip all available .nc files in a given folder according to the shapefile chosen

* The variables that need to be adjusted are given from lines 22 to 27 *
    + Path to shapefile: "shapefile_user"
    + Folder which contains the IMD netCDF files: "nc_folder" (make sure the folder exclusively contains the IMD files)
    + Folder in which outputs are to be saved: "output_folder"
    + Switch to box clipping instead of shapefile clipping: "box_clip"
        - will take the bounds of the shapefile as clipping geometry instead of the shapefile geometry itself
    + Adjust clipping: "padding"
        - if any grid/grids are being excluded, try the padding method to include them
        - only available in case of box_clip = True

                                        -k.r.bro_05
"""
import os
import xarray as xr
import geopandas as gpd

shapefile_user = r"C:\Users\koust\PycharmProjects\ncc_bin_conv\GIS stuff\NEI_shapefile.shp"
nc_folder = r"C:\Users\koust\Desktop\PhD\IMD_grid\2_IMDinterpolated\temp_min-realtime_ncInterpolated"
output_folder = r"C:\Users\koust\Desktop\PhD\IMD_grid\3_IMDclipped"

box_clip = False
padding = 0.2  # Adjust this value as needed


# Make new directory as per the input contents
new_folder_name = os.path.basename(nc_folder.rstrip(os.sep))
var_out_folder = os.path.join(output_folder, new_folder_name) + r'_clipped'
os.makedirs(var_out_folder, exist_ok=True)

# Function to clip netCDF files using shapefile
def clip_netcdf_with_shapefile(nc_file, shapefile, output_file):
    try:
        # Load the NetCDF file
        data = xr.open_dataset(nc_file)

        # Rename spatial dimensions if necessary
        if "LONGITUDE" in data.dims and "LATITUDE" in data.dims:
            data = data.rename({"LONGITUDE": "lon", "LATITUDE": "lat"})
        elif "x" not in data.dims or "y" not in data.dims:
            raise ValueError("Spatial dimensions not found. Check dimension names in the NetCDF file.")

        # Set spatial dimensions
        data = data.rio.set_spatial_dims(x_dim="lon", y_dim="lat", inplace=True)

        # Load the shapefile
        shape = gpd.read_file(shapefile)

        # Assume EPSG:4326 if CRS is missing in the NetCDF file
        if not data.rio.crs:
            data = data.rio.write_crs("EPSG:4326", inplace=True)

        # Align shapefile CRS to NetCDF CRS
        shape = shape.to_crs(data.rio.crs)

        if box_clip:
            # Adjustable clip
            bounds = shape.total_bounds
            padded_bounds = [
                bounds[0] - padding,  # min x
                bounds[1] - padding,  # min y
                bounds[2] + padding,  # max x
                bounds[3] + padding,  # max y
            ]

            # Use the padded bounds in clip_box
            clipped = data.rio.clip_box(
                minx=padded_bounds[0], miny=padded_bounds[1],
                maxx=padded_bounds[2], maxy=padded_bounds[3]
            )

        else:
            # Clip the NetCDF data
            clipped = data.rio.clip(shape.geometry, shape.crs)

        # Save the clipped NetCDF
        clipped.to_netcdf(output_file)
        print(f"Clipped NetCDF file saved as {os.path.basename(output_file.rstrip(os.sep))}")

    except Exception as e:
        print(f"Error clipping file {nc_file}: {e}")


# File paths
for file in os.listdir(nc_folder):
    if file.endswith(".nc"):
        nc_file_path = os.path.join(nc_folder, file)
        output_file_name = os.path.splitext(file)[0] + "_clipped.nc"  # Add suffix to output file
        output_file_path = os.path.join(var_out_folder, output_file_name)

        # Clip the NetCDF file
        clip_netcdf_with_shapefile(nc_file_path, shapefile_user, output_file_path)