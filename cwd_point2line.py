# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# cwd_point2line.py
# Author: Hayden Elza (hayden.elza@gmail.com)
# Last Updated: 2016-07-12
# Usage: cwd_point2line <cwd_points> <cwd_lines> 
# Description: Convert cwd points to lines. This script was written for use
#              in the Flambeau project as a part of the Forest Landscape
#              Ecology Lab of UW Madison and the Forestry Dept of NCSU.
# ---------------------------------------------------------------------------

# Import arcpy module
import arcpy
import os
import sys

# Script arguments
cwd_points_path = arcpy.GetParameterAsText(0)
cwd_lines_path  = arcpy.GetParameterAsText(1)  # This is a path of a not yet existing shapefile

# Create ouput cwd lines shapefile
if arcpy.Exists(cwd_lines_path): 
	arcpy.AddError("Output for CWD Lines already exists.")
	sys.exit(1)
else: arcpy.CreateFeatureclass_management(os.path.dirname(cwd_lines_path), os.path.basename(cwd_lines_path), "POLYLINE", "", "DISABLED", "DISABLED", cwd_points_path, "", "0", "0", "0")

# Use search cursor to read xy location and ID of each point
tree_dict = {}
with arcpy.da.SearchCursor(cwd_points_path, ["SHAPE@XY", "ID"]) as cursor:
	for row in cursor:

		# Get x, y, and ID
		x,y = row[0]
		ID = row[1]

		# Check if ID contains valid characters
		valid_char = set("0123456789_")
		if not set(ID).issubset(valid_char):
			arcpy.AddError(ID + " contains invalid characters. Valid characters are '0123456789_'.")
			sys.exit(1)
		
		# Populate dictionary where keys are the tree number (first four characters)
		if not tree_dict.has_key(ID[:4]):

			# If key does not exist, create it
			tree_dict[ID[:4]] = {ID[4:]:[x,y]}
		
		else:

			# Check for duplicate node codes
			if tree_dict[ID[:4]].has_key(ID[4:]):
				arcpy.AddError("Check for duplicate node code in tree number " + ID)
				sys.exit(1)

			# If everything looks good, append point to tree
			else: tree_dict[ID[:4]][ID[4:]] = [x,y]

# Add fields to cwd lines
arcpy.AddField_management(cwd_lines_path, "tree_num", "TEXT", "", "", "4", "", "NULLABLE", "NON_REQUIRED", "")

# With insert cursor open for cwd lines
with arcpy.da.InsertCursor(cwd_lines_path, ["SHAPE@", "tree_num"]) as cursor:

	# Iterate through each tree
	for key in tree_dict:

		# Get tree and nodes
		tree = tree_dict[key]  # Dictionary of nodes and coordinates
		nodes = tree.keys()    # List of node codes

		# Check for reshoots
		reshoots = set()
		for node in nodes:
			if "_" in node:
				reshoots.add(node.split("_")[0])

		# If there are reshoots use last reshoot and remove others
		if len(reshoots) > 0:

			# For each node reshot
			for reshot_node in reshoots:

				# Get shots
				shots = [str(node) for node in nodes if node.split("_")[0] == reshot_node]

				# Get last shot
				last_shot = str(max([int(shot.split("_")[1]) for shot in shots if len(shot.split("_")) > 1]))

				# Remove all unused shots
				for shot in shots:

					# First shot or reshoots that are not the last one
					if ("_" not in shot) or (shot.split("_")[1] != last_shot): 
						arcpy.AddWarning("Removed shot: " + key + shot)
						nodes.remove(shot)
						del tree[shot]

				# Rename last shot in tree dict and nodes list to not contain the underscore suffix
				tree[reshot_node] = tree.pop(str(reshot_node) + str("_") + str(last_shot))
				nodes.remove(str(reshot_node) + str("_") + str(last_shot))
				nodes.append(reshot_node)

		# Default case, connect nodes 0 and 1
		multiline = [[arcpy.Point(tree["0"][0], tree["0"][1]),
		              arcpy.Point(tree["1"][0], tree["1"][1])]]

		# Forks, where node code length > 1
		for node in nodes:
			if len(node) > 1:

				# Add line connecting node and it's source, e.g., 110 and 11
				multiline.append([arcpy.Point(tree[node[:-1]][0], tree[node[:-1]][1]),
					              arcpy.Point(tree[node][0], tree[node][1])])

		# Create multipart polyline to be added to feature class
		polyline = arcpy.Polyline(arcpy.Array(multiline),arcpy.Describe(cwd_points_path).spatialReference)

		# Update cursor with new values
		cursor.insertRow([polyline, key])