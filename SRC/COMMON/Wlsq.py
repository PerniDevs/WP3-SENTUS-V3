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


import numpy as np
from COMMON.Coordinates import llh2xyz
import COMMON.GnssConstants as Const

def runWlsqIteration(CorrCode, SatPos, S, RcvrPosClk, RcvrPosDelta, NumIter):

    # Compute the newX by adding the deltas from previous iteration to the current position
    RcvrPosClk = RcvrPosClk + RcvrPosDelta
    # Transform from long, lat and height to XYZ 
    RcvrPosClkXYZ = llh2xyz(RcvrPosClk[0], RcvrPosClk[1], RcvrPosClk[2])

    # Initialize residuals dictionary
    r = []

    # Discretize between GPS and Galileo and append the new residual
    for i, SatXYZ in enumerate(SatPos):
        # Recompute Geometrical ranges and residuals Code - Norm(RcvrPosClkXYZ)
        if SatXYZ[-1] == "G" and SatXYZ[-1] in CorrCode[i][1]:
            r.append(float(CorrCode[i][0]) - np.linalg.norm(np.array(SatXYZ[:3], dtype=float).reshape(-1,1) - RcvrPosClkXYZ) - RcvrPosClk[3])
        elif SatXYZ[-1] == "E" and SatXYZ[-1] in CorrCode[i][1]:
            r.append(float(CorrCode[i][0]) - np.linalg.norm(np.array(SatXYZ[:3], dtype=float).reshape(-1,1) - RcvrPosClkXYZ) - RcvrPosClk[4])

    # Compute Delta
    resENU = np.dot(S, r)
    # Transform the three first components to llh
    lat = np.rad2deg(resENU[1]/Const.EARTH_RADIUS)
    lon = np.rad2deg(resENU[0]/(Const.EARTH_RADIUS * np.cos(np.deg2rad(lat))))
    h = resENU[2]
    RcvrPosDelta = np.array([lon, lat, h, resENU[3], resENU[4]])

    # Increase the Number of Iterations
    NumIter +=1 

    return NumIter, RcvrPosDelta, RcvrPosClk, resENU


def buildGmatrix(G, SatLabel, SatCorrInfo):
    
    # Build rotation Matrix and Qenu
    Azim = np.deg2rad(SatCorrInfo["Azimuth"])
    Elev = np.deg2rad(SatCorrInfo["Elevation"])

    East = -np.cos(Elev) * np.sin(Azim)
    North = -np.cos(Elev) * np.cos(Azim)
    Up = -np.sin(Elev)

    GRow = np.array([East, North, Up])

    # Append values according to contellation
    if SatLabel[0] == "G":
        GRow = np.hstack([GRow, 1, 0])
    elif SatLabel[0] == "E":
        GRow = np.hstack([GRow, 0, 1])
    
    G = np.vstack([G, GRow])
    return G


def buildWmatrix(W, SatCorrInfo, valid_idx):
    
    weight = 1 / (SatCorrInfo["SigmaUere"]**2)

    W[valid_idx, valid_idx] = weight

    valid_idx += 1

    return W, valid_idx


def computeDops(G, SatCorrInfo):

    # Compute Q matrix
    Q = np.linalg.inv(np.dot(G.transpose(), G))

    # Compute GDOP
    GDOP = np.sqrt(np.sum(np.diag(Q)))
    # Compute PDOP
    PDOP = np.sqrt(np.sum(np.diag(Q)[:3]))
    # Compute TDOP
    TDOP = np.sqrt(np.diag(Q)[-1])
    
    # Compute DOP ENU, we need to take the xyz components of the Q matrix
    # Qxyz = Q[:3, :3]
    # # Build rotation Matrix and Qenu
    # Azim = np.deg2rad(SatCorrInfo["Azimuth"])
    # Elev = np.deg2rad(SatCorrInfo["Elevation"])

    # # Construct the rotation matrix R
    # R = np.array([[-np.sin(Azim), np.cos(Azim), 0],
    #             [-np.cos(Azim) * np.sin(Elev), -np.sin(Azim) * np.sin(Elev), np.cos(Elev)],
    #             [np.cos(Azim) * np.cos(Elev), np.sin(Azim) * np.cos(Elev), np.sin(Elev)]])
    
    # # Build Qenu
    # Qenu = np.dot(np.dot(R.transpose(), Qxyz), R)

    # Compute HDOP
    HDOP = np.sqrt(np.sum(np.diag(Q)[:2]))
    # Compute VDOP
    VDOP = np.sqrt(np.diag(Q)[2])
    # VDOP = np.sqrt(np.diag(Q)[-1])

    return GDOP, PDOP, TDOP, HDOP, VDOP


def computeS(G, W):
    S = np.dot(np.linalg.inv(np.dot(np.dot(G.transpose(), W), G)), np.dot(G.transpose(), W))
    return S