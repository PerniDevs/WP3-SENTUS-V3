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

# Import External and Internal functions and Libraries
#----------------------------------------------------------------------
import numpy as np
from collections import OrderedDict
from COMMON import GnssConstants as Const
from COMMON.Wlsq import computeDops, computeS, buildGmatrix, buildWmatrix, runWlsqIteration
from Perf import updatePerfEpoch

def computeWlsqSolution(CorrInfo, Conf, Sod, RcvrRefPosLlh, PerfInfoObs):
    '''
        Purpose: 
            To compute a WLSQ solution
        Inputs: 
            CorrInfo: dcitionary with corrected information
            Conf: Configuration file
        Returns:
            PosInfo
    '''
    # Initialize Output Dict
    PosInfo = OrderedDict({})

    # Initialize PosInfo dictionary
    PosInfoObs = OrderedDict({})
    PosInfoObs = {
        "Sod": 0.0,         # Second of the day
        "Lon": 0.0,         # Receiver Estimated Longitude
        "Lat": 0.0,         # Receiver Estimated Latitude
        "Alt": 0.0,         # Receiver Estimated Altitude
        "Clk": 0.0,         # Receiver estimated clock Bias
        "Ggto": 0.0,        # Estimated GGTO
        "Sol": 0,           # 0: No solution | 1: Solution
        "NumSatsVis": 0,    # Number of Visible Satellites
        "NumSat": 0,        # Number of Satellites in
        "Hpe": 0.0,         # HPE
        "Vpe": 0.0,         # VPE
        "Epe": 0.0,         # EPE
        "Npe": 0.0,         # NPE
        "Upe": 0.0,         # UPE
        "Hdop": 0.0,        # HDOP
        "Vdop": 0.0,        # VDOP
        "Pdop": 0.0,        # PDOP
    }

    # Prepare outputs
    # Get Sod
    PosInfoObs["Sod"] = Sod
    # # Get number of Satellites
    PosInfoObs["NumSat"] = sum(1 for SatCorrInfo in CorrInfo.values() if SatCorrInfo["Flag"] == 1)
    # Get number of valid Satellites
    PosInfoObs["NumSatsVis"] = sum(1 for _ in CorrInfo.values())
    
    # Build G: Observation and W: Wighting Matrices
    # -----------------------------------------------------------------
    # Initialize G based on the number of constellations so 5 unknows XYZ, bGPS and bGAL:
    G = np.empty([0, 5]) # 4 columns XYZ and B for the clocks
    
    # Initialize W as a square matrix of zeros with size (valid_sat_count x valid_sat_count)
    W = np.zeros((PosInfoObs["NumSat"], PosInfoObs["NumSat"]))
    
    # Keep track of the index for valid satellites
    valid_idx = 0
    CodeRes = []
    SatPos = []
    CorrCode = []
    bGPS = None
    bGAL = None

    # Loop over all Satellite Corrected Measurements
    for SatLabel, SatCorrInfo in CorrInfo.items():
        #  Filter by valid measurements Flag = 1
        if SatCorrInfo["Flag"] == 1:
            # Build Geometry Matrix in line with SBAS standards
            G = buildGmatrix(G, SatLabel, SatCorrInfo)

            # Build Weight Matrix in line with SBAS standards
            W, valid_idx = buildWmatrix(W, SatCorrInfo, valid_idx)

            # accumulate all the satellites Code Corrected Ranges (since is the true distance)
            CorrCode.append([SatCorrInfo["CorrCode"], SatLabel[0]])
            CodeRes.append(SatCorrInfo["CodeResidual"] + SatCorrInfo["RcvrClk"])

            # accumulate the Geometrical Range
            SatPos.append([SatCorrInfo["SatX"], SatCorrInfo["SatY"], SatCorrInfo["SatZ"], SatLabel[0]])

            # accumulate all the satellites CLKs divide by constellation
            if SatLabel[0] == "G" and bGPS is None:
                bGPS = SatCorrInfo["RcvrClk"][0]
            elif SatLabel[0] == "E" and bGAL is None:
                bGAL = SatCorrInfo["RcvrClk"][0]

    # Reshape vectors to be stacked vertically
    CorrCode = np.array(CorrCode).reshape(len(CorrCode), 2)
    CodeRes = np.array(CodeRes).reshape(len(CodeRes), 1)
    SatPos = np.array(SatPos)
    
    # Perform PVT solution using all SVs with Flag==1
    # -----------------------------------------------------------------
    # Compute Solution if the minimum required satellites are available
    if PosInfoObs["NumSat"] >= Const.MIN_NUM_SATS_PVT:
        
        # Compute DOPs
        GDOP, PDOP, TDOP, HDOP, VDOP = computeDops(G, SatCorrInfo)

        # Check if PDOP is below the configured threshold
        if PDOP <= Const.MAX_PDOP_PVT:

            # Compute the Projection Matrix
            S = computeS(G, W)

            # Get the estimated PVT solution: Position and Clock aplying WLSE filter
            # Initial Position guess is the Receiver Reference Position
            # -----------------------------------------------------------------
            # Get the residuals in ENU
            resEnu = np.dot(S, CodeRes)
            
            # Transform the three first components to llh
            lat = np.rad2deg(resEnu[1]/Const.EARTH_RADIUS)
            lon = np.rad2deg(resEnu[0]/(Const.EARTH_RADIUS * np.cos(np.deg2rad(lat))))
            h = resEnu[2]
            
            # Build the RcvrPosClkDelta
            RcvrPosClkDelta = np.array([lon, lat, h, resEnu[3], resEnu[4]])
            
            # Build the RcvrClkPos since the Position of the satellite is shared for all the GPS and GALILEO
            # The RcvrClkPos will have the pos in XYZ and the b
            RcvrPosClk = np.array([RcvrRefPosLlh[0], RcvrRefPosLlh[1], RcvrRefPosLlh[2], 0, 0]).reshape(-1, 1)
            
            # Initialize counter for WLSQ convergence
            NumIter = 0
            
            # Initialize EPE, NPE, UPE 
            EPE = resEnu[0]
            NPE = resEnu[1]
            UPE = resEnu[2]
            
            while NumIter <= Conf["MAX_LSQ_ITER"] and np.linalg.norm(RcvrPosClkDelta) > Const.LSQ_DELTA_EPS:
                # Increase the number of iterations
                # Use WLSQ for Clock
                NumIter, RcvrPosClkDelta, RcvrPosClk, resENU = runWlsqIteration(CorrCode, SatPos, S, RcvrPosClk, RcvrPosClkDelta, NumIter)   

                # After Iterations perform transformations to get them in ENU          
                EPE += resENU[0]
                NPE += resENU[1]
                UPE += resENU[2]

            #Update PVT dictionary
            PosInfoObs["Lon"] = RcvrPosClk[0]
            PosInfoObs["Lat"] = RcvrPosClk[1]
            PosInfoObs["Alt"] = RcvrPosClk[2]
            PosInfoObs["Clk"] = RcvrPosClk[3]
            PosInfoObs["Ggto"] = (RcvrPosClk[4] - RcvrPosClk[3]) / Const.SPEED_OF_LIGHT / Const.NS_TO_S
            PosInfoObs["Epe"] = EPE
            PosInfoObs["Npe"] = NPE
            PosInfoObs["Upe"] = UPE
            PosInfoObs["Hpe"] = np.sqrt(EPE**2 + NPE**2)
            PosInfoObs["Vpe"] = np.abs(UPE)
            PosInfoObs["Hdop"] = HDOP
            PosInfoObs["Vdop"] = VDOP
            PosInfoObs["Pdop"] = PDOP
            PosInfoObs["Sol"] = 1

            # Update Performance Intermediatee Information
            PerfInfoObs = updatePerfEpoch(EPE, NPE, UPE, GDOP, PDOP, TDOP, HDOP, VDOP, PosInfoObs["Hpe"], PosInfoObs["Vpe"], PosInfoObs["NumSat"], PerfInfoObs)
        
        else:
            PosInfoObs["Sol"] = 0
            PerfInfoObs["SamNoSol"] += 1
    
    else:
        PosInfoObs["Sol"] = 0
        PerfInfoObs["SamNoSol"] += 1

    PosInfo = PosInfoObs

    return PosInfo, PerfInfoObs