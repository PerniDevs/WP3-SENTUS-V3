#!/usr/bin/env python

########################################################################
# PreprocessingPlots.py:
# This is the PreprocessingPlots Module of SENTUS tool
#
#  Project:        SENTUS
#  File:           PreprocessingPlots.py
#
#   Author: Agustin Pernigotti
#   Copyright 2024 Agustin Pernigotti
#
# -----------------------------------------------------------------
# Date       | Author             | Action
# -----------------------------------------------------------------
#
########################################################################


import sys, os
import numpy as np
from pandas import unique
from pandas import read_csv
from InputOutput import PvtIdx
from InputOutput import REJECTION_CAUSE_DESC
sys.path.append(os.getcwd() + '/' + \
    os.path.dirname(sys.argv[0]) + '/' + 'COMMON')
from COMMON import GnssConstants
from COMMON.Plots import generatePlot
from COMMON.allPRNs import allprns
from COMMON.Coordinates import xyz2llh


def initPlot(PreproObsFile, PlotConf, Title, Label, xLabelRequired:bool):
    PreproObsFileName = os.path.basename(PreproObsFile)
    PreproObsFileNameSplit = PreproObsFileName.split('_')
    Rcvr = PreproObsFileNameSplit[2]
    DatepDat = PreproObsFileNameSplit[3]
    Date = DatepDat.split('.')[0]
    Year = Date[1:3]
    Doy = Date[4:]

    if xLabelRequired:
        PlotConf["xLabel"] = "Hour of Day %s" % Doy 

    PlotConf["Title"] = "%s from %s on Year %s"\
        " DoY %s" % (Title, Rcvr, Year, Doy)

    PlotConf["Path"] = sys.argv[1] + '/OUT/PVT/figures/' + \
        '%s_%s_Y%sD%s.png' % (Label, Rcvr, Year, Doy)
    
    return PlotConf


def plotNumsat(PvtObsFile, PvtsObsData):
    # Set Conf Dicts
    PlotTitle = "Number of Satellites"
    PlotLabel = "NUMBER_OF_GAL+GPS_SATELLITES"
    PlotConf = {
        "Type": "Lines",
        "FigSize" : (10.4, 6.6),

        "xLabel" : "Hour of DoY 011",

        "xTicks": range(round(PvtsObsData[PvtIdx["SOD"]].min() / GnssConstants.S_IN_H), round(PvtsObsData[PvtIdx["SOD"]].max() / GnssConstants.S_IN_H) + 1),
        "xLim" : [round(PvtsObsData[PvtIdx["SOD"]].min() / GnssConstants.S_IN_H), round(PvtsObsData[PvtIdx["SOD"]].max() / GnssConstants.S_IN_H)],

        "yLabel": "Number of Satellites",
        "yLim" : [0, 20],
        "yTicks" : range(0, 20),

        "Grid" : 1,
        "c" : {0: "orange", 1: "green"},
        "Marker" : "",
        "LineWidth" : 1,
        "LineStyle" : "-",

        "Label" : {0: "RAW", 1: "Used"},
        "LabelLoc" : "upper left",
        
        "xData": {
            0: PvtsObsData[PvtIdx["SOD"]] / GnssConstants.S_IN_H,
            1: PvtsObsData[PvtIdx["SOD"]] / GnssConstants.S_IN_H
        },

        "yData": {
            0: PvtsObsData[PvtIdx["NUMSATSVIS"]],
            1: PvtsObsData[PvtIdx["NUMSAT"]],
        },

    }

    PlotConf = initPlot(PvtObsFile, PlotConf, PlotTitle, PlotLabel, xLabelRequired=True)

    generatePlot(PlotConf)


def plotDOP(PvtObsFile, PvtsObsData):
    PlotTitle = "DOP"
    PlotLabel = "DOP"
    PlotConf = {
        "Type": "Lines",
        "FigSize" : (10.4, 6.6),

        "xLabel" : "Hour of DoY 011",

        "xTicks": range(round(PvtsObsData[PvtIdx["SOD"]].min() / GnssConstants.S_IN_H), round(PvtsObsData[PvtIdx["SOD"]].max() / GnssConstants.S_IN_H) + 1),
        "xLim" : [round(PvtsObsData[PvtIdx["SOD"]].min() / GnssConstants.S_IN_H), round(PvtsObsData[PvtIdx["SOD"]].max() / GnssConstants.S_IN_H)],

        "yLabel": "DOP",
        "yLim" : [0, 4],
        
        "yLabel2": "Number of Satellites",
        "yLim2": [0,PvtsObsData[PvtIdx["NUMSATSVIS"]].max() + 3],
        "yTicks2": range(0, PvtsObsData[PvtIdx["NUMSATSVIS"]].max() + 3), 

        "Grid" : 1,
        "c" : {0: "orange", 1: "blue", 2: "green", 3: "cyan"},
        "Marker" : "",
        "LineWidth" : 1,
        "LineStyle" : "-",

        "Label" : {0: "NUM SV", 1: "PDOP", 2: "VDOP" , 3: "HDOP"},
        "LabelLoc" : "best",
        
        "MultiAxis": True,
        
        "xData": {
            0: PvtsObsData[PvtIdx["SOD"]] / GnssConstants.S_IN_H,
            1: PvtsObsData[PvtIdx["SOD"]] / GnssConstants.S_IN_H,
            2: PvtsObsData[PvtIdx["SOD"]] / GnssConstants.S_IN_H,
            3: PvtsObsData[PvtIdx["SOD"]] / GnssConstants.S_IN_H
        },

        "yData": {
            0: PvtsObsData[PvtIdx["NUMSAT"]],
            1: PvtsObsData[PvtIdx["PDOP"]],
            2: PvtsObsData[PvtIdx["VDOP"]],
            3: PvtsObsData[PvtIdx["HDOP"]]
        },

    }

    PlotConf = initPlot(PvtObsFile, PlotConf, PlotTitle, PlotLabel, xLabelRequired=True)

    generatePlot(PlotConf)


def plotLeoTracks(PvtObsFile, PvtsObsData):
    
    PlotTitle = "Leo Satellite Tracks"
    PlotLabel = "LEO_TRACKS"
    maxLat = 90
    maxLon = 180
     
    PlotConf = {
        "Type": "Lines",
        "FigSize" : (14.4, 10.6),

        "LonMin" : -maxLon,
        "LonMax" : maxLon,
        "LatMin" : -maxLat,
        "LatMax" : maxLat,
        "LonStep" : 15,
        "LatStep" : 10,

        # PlotConf["yLabel"] = "Latitude [deg]"
        "yTicks" : range(-maxLat,maxLat+1,10),
        "yLim" : [-maxLat, maxLat],

        # PlotConf["xLabel"] = "Longitude [deg]"
        "xTicks" : range(-maxLon,maxLon+1,15),
        "xLim" : [-maxLon, maxLon],

        "Grid": True,
        "s" : 1,

        "Map": True,
        
        "Marker" : '.',
        "LineWidth" : 1,

        "ColorBar" : "gnuplot",
        "ColorBarLabel" : "Second of the day",
        "ColorBarMin" : PvtsObsData[PvtIdx["SOD"]].min(),
        "ColorBarMax" : PvtsObsData[PvtIdx["SOD"]].max(),

        "Label": {0},
        
        "xData": {0:PvtsObsData[PvtIdx["LONG"]]},

        "yData": {0: PvtsObsData[PvtIdx["LAT"]]},

        "zData": {0: PvtsObsData[PvtIdx["SOD"]]},
    }

    PlotConf = initPlot(PvtObsFile, PlotConf, PlotTitle, PlotLabel, xLabelRequired=False)

    generatePlot(PlotConf)


def plotClk(PvtObsFile, PvtsObsData):
    PlotTitle = "Estimated Receiver Clock wrt GPST"
    PlotLabel = "RCVR_CLK"
    PlotConf = {
        "Type": "Lines",
        "FigSize" : (14.4, 10.6),

        "xLabel" : "Hour of DoY 011",

        "xTicks": range(round(PvtsObsData[PvtIdx["SOD"]].min() / GnssConstants.S_IN_H), round(PvtsObsData[PvtIdx["SOD"]].max() / GnssConstants.S_IN_H) + 1),
        "xLim" : [round(PvtsObsData[PvtIdx["SOD"]].min() / GnssConstants.S_IN_H), round(PvtsObsData[PvtIdx["SOD"]].max() / GnssConstants.S_IN_H)],

        "yLabel": "Estimated Receiver clock wrt GPST [m]",

        "Grid" : 1,
        "c" : {0: "green"},
        "Marker" : ".",
        "LineWidth" : 1,
        "LineStyle": "",
        "s": 1,

        "Label" : {0: "CLK EST"},
        "LabelLoc" : "best",
        
        "MultiAxis": True,
        
        "xData": {
            0: PvtsObsData[PvtIdx["SOD"]] / GnssConstants.S_IN_H,
        },

        "yData": {
            0: PvtsObsData[PvtIdx["CLK"]],
        },

    }

    PlotConf = initPlot(PvtObsFile, PlotConf, PlotTitle, PlotLabel, xLabelRequired=True)

    generatePlot(PlotConf)


def plotGgto(PvtObsFile, PvtsObsData):
    PlotTitle = "Estimated GGTO"
    PlotLabel = "GGTO"
    PlotConf = {
        "Type": "Lines",
        "FigSize" : (14.4, 10.6),

        "xLabel" : "Hour of DoY 011",

        "xTicks": range(round(PvtsObsData[PvtIdx["SOD"]].min() / GnssConstants.S_IN_H), round(PvtsObsData[PvtIdx["SOD"]].max() / GnssConstants.S_IN_H) + 1),
        "xLim" : [round(PvtsObsData[PvtIdx["SOD"]].min() / GnssConstants.S_IN_H), round(PvtsObsData[PvtIdx["SOD"]].max() / GnssConstants.S_IN_H)],

        "yLabel": "Estimated GGTO [m]",        

        "Grid" : 1,
        "c" : {0: "red"},
        "Marker" : ".",
        "LineWidth" : 1,
        "LineStyle": "",
        "s": 1,

        "Label" : {0: "GGTO"},
        "LabelLoc" : "best",
        
        "MultiAxis": True,
        
        "xData": {
            0: PvtsObsData[PvtIdx["SOD"]] / GnssConstants.S_IN_H,
        },

        "yData": {
            0: PvtsObsData[PvtIdx["GGTO"]],
        },

    }

    PlotConf = initPlot(PvtObsFile, PlotConf, PlotTitle, PlotLabel, xLabelRequired=True)

    generatePlot(PlotConf)


def plotENU(PvtObsFile, PvtsObsData):
    PlotTitle = "East North Up Postion Errors"
    PlotLabel = "ENU_PE"
    PlotConf = {
        "Type": "Lines",
        "FigSize" : (14.4, 10.6),

        "xLabel" : "Hour of DoY 011",

        "xTicks": range(round(PvtsObsData[PvtIdx["SOD"]].min() / GnssConstants.S_IN_H), round(PvtsObsData[PvtIdx["SOD"]].max() / GnssConstants.S_IN_H) + 1),
        "xLim" : [round(PvtsObsData[PvtIdx["SOD"]].min() / GnssConstants.S_IN_H), round(PvtsObsData[PvtIdx["SOD"]].max() / GnssConstants.S_IN_H)],

        "yLabel": "East North Up Postion Errors",

        "Grid" : 1,
        "c" : {0: "orange", 1: "red", 2: "green"},
        "Marker" : ".",
        "LineWidth" : 1,
        "LineStyle": "",
        "s": 1,

        "Label" : {0: "EPE", 1: "NPE", 2: "UPE"},
        "LabelLoc" : "best",
        
        "xData": {
            0: PvtsObsData[PvtIdx["SOD"]] / GnssConstants.S_IN_H,
            1: PvtsObsData[PvtIdx["SOD"]] / GnssConstants.S_IN_H,
            2: PvtsObsData[PvtIdx["SOD"]] / GnssConstants.S_IN_H,
        },

        "yData": {
            0: PvtsObsData[PvtIdx["EPE"]],
            1: PvtsObsData[PvtIdx["NPE"]],
            2: PvtsObsData[PvtIdx["UPE"]],
        },

    }

    PlotConf = initPlot(PvtObsFile, PlotConf, PlotTitle, PlotLabel, xLabelRequired=True)

    generatePlot(PlotConf)


def plotEPEvsNPE(PvtObsFile, PvtsObsData):
    PlotTitle = "Horizontal position Error vs DOP"
    PlotLabel = "EPE_VS_NPE"
    PlotConf = {
        "Type": "Lines",
        "FigSize" : (14.4, 10.6),

        "xLabel" : "EPE[m]",

        # "xTicks": range(round(PvtsObsData[PvtIdx["SOD"]].min() / GnssConstants.S_IN_H), round(PvtsObsData[PvtIdx["SOD"]].max() / GnssConstants.S_IN_H) + 1),
        # "xLim" : [round(PvtsObsData[PvtIdx["SOD"]].min() / GnssConstants.S_IN_H), round(PvtsObsData[PvtIdx["SOD"]].max() / GnssConstants.S_IN_H)],

        "yLabel": "NPE[m]",

        "Grid" : 1,
        "c" : {0: "orange", 1: "red", 2: "green"},
        "Marker" : ".",
        "LineWidth" : 1,
        "LineStyle": "",
        "s": 1,

        "ColorBar" : "gnuplot",
        "ColorBarLabel" : "HDOP[m]",
        "ColorBarMin" : PvtsObsData[PvtIdx["HDOP"]].min(),
        "ColorBarMax" : PvtsObsData[PvtIdx["HDOP"]].max(),

        "Label" : {0},
        
        "xData": {
            0: PvtsObsData[PvtIdx["EPE"]],
        },

        "yData": {
            0: PvtsObsData[PvtIdx["NPE"]],
        },

         "zData": {
            0: PvtsObsData[PvtIdx["HDOP"]],
        },

    }

    PlotConf = initPlot(PvtObsFile, PlotConf, PlotTitle, PlotLabel, xLabelRequired=True)

    generatePlot(PlotConf)


def plotHVPE(PvtObsFile, PvtsObsData):
    PlotTitle = "Horizontal and Vertical Postion Errors"
    PlotLabel = "HV_PE"
    PlotConf = {
        "Type": "Lines",
        "FigSize" : (14.4, 10.6),

        "xLabel" : "Hour of DoY 011",

        "xTicks": range(round(PvtsObsData[PvtIdx["SOD"]].min() / GnssConstants.S_IN_H), round(PvtsObsData[PvtIdx["SOD"]].max() / GnssConstants.S_IN_H) + 1),
        "xLim" : [round(PvtsObsData[PvtIdx["SOD"]].min() / GnssConstants.S_IN_H), round(PvtsObsData[PvtIdx["SOD"]].max() / GnssConstants.S_IN_H)],

        "yLabel": "East North Up Postion Errors [m]",

        "Grid" : 1,
        "c" : {0: "green", 1: "red"},
        "Marker" : ".",
        "LineWidth" : 1,
        "LineStyle": "",
        "s": 1,

        "Label" : {0: "VPE", 1: "HPE"},
        "LabelLoc" : "best",
        
        "xData": {
            0: PvtsObsData[PvtIdx["SOD"]] / GnssConstants.S_IN_H,
            1: PvtsObsData[PvtIdx["SOD"]] / GnssConstants.S_IN_H,
        },

        "yData": {
            0: PvtsObsData[PvtIdx["VPE"]],
            1: PvtsObsData[PvtIdx["HPE"]],
        },

    }

    PlotConf = initPlot(PvtObsFile, PlotConf, PlotTitle, PlotLabel, xLabelRequired=True)

    generatePlot(PlotConf)


def generatePvtsPlots(PvtObsFile):
    
    # Purpose: generate output plots regarding Corrections results

    # Parameters
    # ==========
    # CorrObsFile: str
    #         Path to CORR OBS output file

    # Returns
    # =======
    # Nothing


    # Number of satellites
    # ----------------------------------------------------------
    # Read the cols we need from PREPRO OBS file
    PvtsObsData = read_csv(PvtObsFile, delim_whitespace=True, skiprows=1, header=None,\
    usecols=[PvtIdx["SOD"], PvtIdx["NUMSATSVIS"], PvtIdx["NUMSAT"]])
    
    print('INFO: Number of Satellites...')

    # Configure plot and call plot generation function
    plotNumsat(PvtObsFile, PvtsObsData)

    # DOP
    # ----------------------------------------------------------
    # Read the cols we need from PVT file
    PvtsObsData = read_csv(PvtObsFile, delim_whitespace=True, skiprows=1, header=None,\
    usecols=[PvtIdx["SOD"], PvtIdx["NUMSATSVIS"], PvtIdx["NUMSAT"], PvtIdx["PDOP"], PvtIdx["VDOP"], PvtIdx["HDOP"]])
    
    print('INFO: Plot DOP...')

    # Configure plot and call plot generation function
    plotDOP(PvtObsFile, PvtsObsData)


    # LEO Tracks
    # ----------------------------------------------------------
    # Read the cols we need from PVT file
    PvtsObsData = read_csv(PvtObsFile, delim_whitespace=True, skiprows=1, header=None,\
    usecols=[PvtIdx["SOD"], PvtIdx["LONG"], PvtIdx["LAT"]])
    
    print('INFO: Plot Leo Tracks...')

    # Configure plot and call plot generation function
    plotLeoTracks(PvtObsFile, PvtsObsData)


    # Receiver Clock
    # ----------------------------------------------------------
    # Read the cols we need from PVT file
    PvtsObsData = read_csv(PvtObsFile, delim_whitespace=True, skiprows=1, header=None,\
    usecols=[PvtIdx["SOD"], PvtIdx["CLK"]])
    
    print('INFO: Plot Estimated RCVR CLK...')

    # Configure plot and call plot generation function
    plotClk(PvtObsFile, PvtsObsData)


    # GGTO
    # ----------------------------------------------------------
    # Read the cols we need from PVT file
    PvtsObsData = read_csv(PvtObsFile, delim_whitespace=True, skiprows=1, header=None,\
    usecols=[PvtIdx["SOD"], PvtIdx["GGTO"]])
    
    print('INFO: Plot GGTO...')

    # Configure plot and call plot generation function
    plotGgto(PvtObsFile, PvtsObsData)


    # ENU
    # ----------------------------------------------------------
    # Read the cols we need from PVT file
    PvtsObsData = read_csv(PvtObsFile, delim_whitespace=True, skiprows=1, header=None,\
    usecols=[PvtIdx["SOD"], PvtIdx["EPE"], PvtIdx["NPE"], PvtIdx["UPE"]])
    
    print('INFO: Plot ENU...')

    # Configure plot and call plot generation function
    plotENU(PvtObsFile, PvtsObsData)


    # EPE vs NPE
    # ----------------------------------------------------------
    # Read the cols we need from PVT file
    PvtsObsData = read_csv(PvtObsFile, delim_whitespace=True, skiprows=1, header=None,\
    usecols=[PvtIdx["EPE"], PvtIdx["NPE"], PvtIdx["HDOP"]])
    
    print('INFO: Plot EPE vs NPE...')

    # Configure plot and call plot generation function
    plotEPEvsNPE(PvtObsFile, PvtsObsData)


    # HVPE
    # ----------------------------------------------------------
    # Read the cols we need from PVT file
    PvtsObsData = read_csv(PvtObsFile, delim_whitespace=True, skiprows=1, header=None,\
    usecols=[PvtIdx["SOD"], PvtIdx["HPE"], PvtIdx["VPE"]])
    
    print('INFO: Plot HVPE...')

    # Configure plot and call plot generation function
    plotHVPE(PvtObsFile, PvtsObsData)