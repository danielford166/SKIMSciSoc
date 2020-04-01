#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 22 13:43:32 2018

@author: rr
"""

import cPickle as pickle;
import numpy as np;
import matplotlib.pyplot as plt;
import python_util.parameter_sets as ps;
import python_util.skim_utilities as su;
from netCDF4 import Dataset;
from os import path;
from mpl_toolkits.basemap import Basemap;
from random import random;

plotShelfBoundary = True;
plotNormals = False;
plotGridIntersects = False;

def to_lon_lat_boundary_coordinates(coordinates, params):
    for i in range(len(coordinates)):
        coordinates[i] = su.convert_index_to_lonlat(coordinates[i][0], coordinates[i][1], params.pixelRes, lon0=params.originLon, lat0=params.originLat);
    return coordinates;

def to_lon_lat_normals(xCoords, yCoords, lineCentrePoints, ontoShelfDirection, params):
    for i in range(len(xCoords)):
        xCoord = xCoords[i];
        yCoord = yCoords[i];
        lon1, lat1 = su.convert_index_to_lonlat(xCoord[0], yCoord[0], params.pixelRes, lon0=params.originLon, lat0=params.originLat);
        lon2, lat2 = su.convert_index_to_lonlat(xCoord[1], yCoord[1], params.pixelRes, lon0=params.originLon, lat0=params.originLat);
        xCoords[i] = (lon1, lon2);
        yCoords[i] = (lat1, lat2);
        
        #c, d = su.convert_index_to_lonlat(lineCentrePoints[i][0]+ontoShelfDirection[i][0], lineCentrePoints[i][1]+ontoShelfDirection[i][1], params.pixelRes, lon0=lineCentrePoints[i][0], lat0=lineCentrePoints[i][1]);
        
        lineCentrePoints[i] = su.convert_index_to_lonlat(lineCentrePoints[i][0], lineCentrePoints[i][1], params.pixelRes, lon0=params.originLon, lat0=params.originLat);
        ontoShelfDirection[i] = ontoShelfDirection[i]/np.linalg.norm(ontoShelfDirection[i]);
        ontoShelfDirection[i] = su.convert_index_to_lonlat(ontoShelfDirection[i][0], ontoShelfDirection[i][1], params.pixelRes, lon0=0, lat0=0);
        
        #a, b = lineCentrePoints[i];
        
        #ontoShelfDirection[i] = (c-a, d-b);
        
    return xCoords, yCoords, lineCentrePoints, ontoShelfDirection;

def concat_lists(lists):
    newList = [];
    for l in lists:
        newList = newList + l;
    return newList;

def draw_box(mapFig, lon1, lat1, lon2, lat2, color='b'):
    lons = [lon1, lon2];
    lats = [lat1, lat2];
    x, y = mapFig(lons, lats);
#    lines = [((x[0], y[0]), (x[1], y[0])),
#             ((x[0], y[0]), (x[0], y[1])), 
#             ((x[1], y[1]), (x[0], y[1])), 
#             ((x[1], y[1]), (x[1], y[0]))];
    linesX = [x[0], x[1], x[0], x[0], x[1], x[0], x[1], x[1]];
    linesY = [y[0], y[0], y[0], y[1], y[1], y[1], y[1], y[0]];
    mapFig.plot(linesX, linesY, color=color);

params = ps.get_example_method_plot_params();
#if params.paramsetName != "europeanshelf": #Could actually use the shelf coordinates filename (which is also stored in params)...
#    raise ValueError("This plotting script is intended only for the 'global' parameter set. Significant adaptation is required for use with any other datasets that may change the shelf-coordinates.");

data = pickle.load(open(path.join("data/output/ekman_geostrophic_surface_currents_"+params.paramsetName+".p"), "rb"));
shelfCoordData = concat_lists(pickle.load(open(path.join("data/shelf_coordinates/", params.contourPathFile), "rb")).coordinatesLists);
shelfCoordData = to_lon_lat_boundary_coordinates(shelfCoordData, params);
shelfCoordDataDeep = concat_lists(pickle.load(open(path.join("data/shelf_coordinates/", params.contourPathFileDeep), "rb")).coordinatesLists);
shelfCoordDataDeep = to_lon_lat_boundary_coordinates(shelfCoordDataDeep, params);
bathy = Dataset("/home/rr/Files/Tasks/20180914_SKIM/data/GEBCO_bathymetry_0.25x0.25deg.nc", 'r');
depth = np.flipud(bathy.variables["mean_depth"][:]);
depth = su.apply_mask(depth, None, params.ilatRange, params.ilonRange);


#Reused plot parameters
figsize = (8.5, 6.5);
ticksize = 16;


###############################################
#Plot shallow and deep contours
###############################################
if plotShelfBoundary == True:
    plt.figure(figsize=figsize);
    mapFig = Basemap(llcrnrlon=params.originLon, llcrnrlat=params.maxLat+0.25, urcrnrlon=params.maxLon-0.25, urcrnrlat=params.originLat, resolution='l', projection='cyl', lat_0 = 39.5, lon_0 = -3.25);
    mapFig.drawmapboundary(fill_color=(0.85, 0.85, 0.85));
    mapFig.fillcontinents(color=(0.5, 0.5, 0.5), zorder=1);
    mapFig.drawmeridians(np.arange(0, 360, 2.5), labels=[0,0,0,1], color=(0.3, 0.3, 0.3), fontsize=ticksize);
    mapFig.drawparallels(np.arange(-90, 90, 2.5), labels=[1,0,0,0], color=(0.3, 0.3, 0.3), fontsize=ticksize);
    
    #Bathymetry
    lon = np.arange(params.originLon, params.maxLon, 0.25);
    lat = np.arange(params.originLat, params.maxLat, -0.25);
    x, y = np.meshgrid(lon, lat);
    xi, yi = mapFig(x, y);
    cs = mapFig.pcolormesh(xi,yi, depth);#, cmap=cmap);
    
    #Deep contour
    xs = [tup[0] for tup in shelfCoordDataDeep];
    ys = [tup[1] for tup in shelfCoordDataDeep];
    x, y = mapFig(xs, ys);
    mapFig.plot(x, y, color=(0.75, 0.0, 0.0));
    
    #Shallow contour
    xs = [tup[0] for tup in shelfCoordData];
    ys = [tup[1] for tup in shelfCoordData];
    x, y = mapFig(xs, ys);
    mapFig.plot(x, y, 'r');
    plt.savefig("plots/method_demonstration/shelf_boundary_2tmp.png");


###############################################
#Plot straight lines and normal directions (low n).
###############################################
if plotNormals == True:
    #Read data and process from coordinates to lon and lat
    extraInfo = pickle.load(open("data/output/extra_info_"+params.paramsetName+".p", "rb"));
    lineLons, lineLats, lineCentrePoints, onShelfDirectionVectors = to_lon_lat_normals(extraInfo["lineXCoords"], extraInfo["lineYCoords"], extraInfo["lineCentrePoints"], extraInfo["onShelfDirectionVectors"], params);    
    pointLineIndex = extraInfo["pointLineIndex"];
    
    #Select colours
    colours = [];
    minCol = 0.25; scal=1.0-minCol;
    for i in range(0, len(extraInfo["lineXCoords"])):
        colours.append((minCol+scal*random(), minCol+scal*random(), minCol+scal*random()));
    
    plt.figure(figsize=figsize);
    mapFig = Basemap(llcrnrlon=params.originLon, llcrnrlat=params.maxLat+0.25, urcrnrlon=params.maxLon-0.25, urcrnrlat=params.originLat, resolution='l', projection='cyl', lat_0 = 39.5, lon_0 = -3.25);
    mapFig.drawmapboundary(fill_color=(0.85, 0.85, 0.85));
    mapFig.fillcontinents(color=(0.5, 0.5, 0.5), zorder=1);
    mapFig.drawmeridians(np.arange(0, 360, 2.5), labels=[0,0,0,1], color=(0.3, 0.3, 0.3), fontsize=ticksize);
    mapFig.drawparallels(np.arange(-90, 90, 2.5), labels=[1,0,0,0], color=(0.3, 0.3, 0.3), fontsize=ticksize);
    
    #Bathometry
    lon = np.arange(params.originLon, params.maxLon, 0.25);
    lat = np.arange(params.originLat, params.maxLat, -0.25);
    x, y = np.meshgrid(lon, lat);
    xi, yi = mapFig(x, y);
    cs = mapFig.pcolormesh(xi,yi, depth);#, cmap=cmap);

    #Contour points
    xs = [tup[0] for tup in shelfCoordData];
    ys = [tup[1] for tup in shelfCoordData];
    x, y = mapFig(xs, ys);
    for i in range(len(x)):
        dimmedColour = (0.7*colours[pointLineIndex[i]][0], 0.7*colours[pointLineIndex[i]][1], 0.7*colours[pointLineIndex[i]][2]);
        mapFig.scatter(x[i], y[i], color=dimmedColour);
    
    #Lines and normals
    for i in range(0, len(lineLons)):
        #Lines
        lineLon = lineLons[i];
        lineLat = lineLats[i];
        x, y = mapFig(lineLon, lineLat);
        mapFig.plot(x, y, color=colours[i]);#, 'o-', markersize=5, linewidth=1);
        
        #Normals
        arrowScale = 2.0;
        x, y = mapFig([lineCentrePoints[i][0], onShelfDirectionVectors[i][0]], [lineCentrePoints[i][1], onShelfDirectionVectors[i][1]]);
        plt.arrow(x[0], y[0], x[1]*arrowScale, y[1]*arrowScale, linewidth=1, head_width=0.25, head_length=0.25, color=colours[i]);
    
    plt.savefig("plots/method_demonstration/shelf_normals.png");


#########################
#Plot grid intersects
#########################
if plotGridIntersects == True:
    gridIntercepts = extraInfo["gridIntercepts"];
    
    plt.figure(figsize=figsize);
    mapFig = Basemap(llcrnrlon=params.originLon, llcrnrlat=params.maxLat+0.25, urcrnrlon=params.maxLon-0.25, urcrnrlat=params.originLat, resolution='l', projection='cyl', lat_0 = 39.5, lon_0 = -3.25);
    mapFig.drawmapboundary(fill_color=(0.85, 0.85, 0.85));
    mapFig.fillcontinents(color=(0.5, 0.5, 0.5), zorder=1);
    mapFig.drawmeridians(np.arange(0, 360, 2.5), labels=[0,0,0,1], color=(0.3, 0.3, 0.3), fontsize=ticksize);
    mapFig.drawparallels(np.arange(-90, 90, 2.5), labels=[1,0,0,0], color=(0.3, 0.3, 0.3), fontsize=ticksize);
    
    #Bathometry
    lon = np.arange(params.originLon, params.maxLon, 0.25);
    lat = np.arange(params.originLat, params.maxLat, -0.25);
    x, y = np.meshgrid(lon, lat);
    xi, yi = mapFig(x, y);
    cs = mapFig.pcolormesh(xi,yi, depth);#, cmap=cmap);

    #Plot intersected grids
    for gridIntercept in gridIntercepts:
        lon1, lat1 = su.convert_index_to_lonlat(gridIntercept.bx1, gridIntercept.by1, params.pixelRes, lon0=params.originLon, lat0=params.originLat);
        lon2, lat2 = su.convert_index_to_lonlat(gridIntercept.bx2, gridIntercept.by2, params.pixelRes, lon0=params.originLon, lat0=params.originLat);
        draw_box(mapFig, lon1, lat1, lon2, lat2, color='r');
    #Plot line segments:
    colour = 'y';
    for gridIntercept in gridIntercepts:
        xs = (gridIntercept.i1lon, gridIntercept.i2lon);
        ys = (gridIntercept.i1lat, gridIntercept.i2lat);
        x, y = mapFig(xs, ys);
        mapFig.plot(x, y, color=colour);
        if colour == 'y':
            colour = 'g';
        else:
            colour = 'y';

    plt.savefig("plots/method_demonstration/grid_intersects.png");






#dimming = 0.6;
#
#
#
#normalsFig, normalsAx = plt.subplots(1);
#normalsAx.imshow(depth);
#for i in range(0, len(lineXCoords)):
#    minCol = 0.25; scal=1.0-minCol; colour = (minCol+scal*random(), minCol+scal*random(), minCol+scal*random());
#    normalsAx.plot(lineXCoords[i], lineYCoords[i], color = colour);
#    normalsAx.plot([lineCentrePoints[i][0], lineCentrePoints[i][0]+onShelfDirectionVectors[i][0]], [lineCentrePoints[i][1], lineCentrePoints[i][1]+onShelfDirectionVectors[i][1]], color=colour);
#plt.scatter(x[w], y[w], c=(colours[i][0]*dim, colours[i][1]*dim, colours[i][2]*dim), s=6);
#for i in range(len(params)):
#    plt.plot(xRange[i], yRange[i], c=colours[i]);
#
#
#plt.figure(figsize=figsize);
#mapFig = Basemap(llcrnrlon=-180.0, llcrnrlat=-90, urcrnrlon=180.0, urcrnrlat=90.0, resolution='l', projection='cyl', lat_0 = 39.5, lon_0 = -3.25);
##mapFig = Basemap(width=40000000, height=24000000, resolution='l', projection='stere', lat_ts=0.0, lat_0=0.0, lon_0=0.0);
#mapFig.drawmapboundary(fill_color=(0.85, 0.85, 0.85));
#mapFig.fillcontinents(color=(0.5, 0.5, 0.5), zorder=1);
#mapFig.drawmeridians(np.arange(0, 360, 60), labels=[0,0,0,1], color=(0.3, 0.3, 0.3), fontsize=ticksize);
#mapFig.drawparallels(np.arange(-90, 90, 30), labels=[1,0,0,0], color=(0.3, 0.3, 0.3), fontsize=ticksize);
#mapFig.scatter(lons, lats, latlon=True, c=ngeostrophicProportions, marker='o', cmap=plt.cm.YlOrRd);
#
#cbar = plt.colorbar(orientation="horizontal", ticks=[0.0, 0.5, 1.0]);
#plt.clim(0, 1);
#cbar.set_label("relative strength of geostrophic current", fontsize=ticksize);
#cbar.ax.set_yticklabels(["0.0", "0.5", "1.0"]);
#plt.title("January, February, March, 2014", fontsize=ticksize);