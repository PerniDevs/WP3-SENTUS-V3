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

from collections import OrderedDict
import numpy as np

def initializePerfInfo(Conf):
        PerfInfoObs = OrderedDict({})
        PerfInfoObs = {
        "Rcvr":Conf["SAT_ACRONYM"],
        "Epe": [],  # East Position Error
        "Npe": [],  # North Position Error
        "Upe": [],  # Up Position Error
        "Hpe": [],  # Horizontal Position Error (calculated during update)
        "Vpe": [],  # Vertical Position Error (calculated during update)
        "Pdop": [], "Hdop": [], "Vdop": [], "Gdop": [], "Tdop": [],# DOP values
        "Samples":0,
        "SamNoSol": 0,  # Counter for epochs with no solution
        "NumSat": [], 
    }
        
        return PerfInfoObs

def updatePerfEpoch(EPE, NPE, UPE, GDOP, PDOP, TDOP, HDOP, VDOP, HPE, VPE, NumSat, PerfInfoObs):
    PerfInfoObs["Epe"].append(EPE)
    PerfInfoObs["Npe"].append(NPE)
    PerfInfoObs["Upe"].append(UPE)
    PerfInfoObs["Hpe"].append(HPE)  
    PerfInfoObs["Vpe"].append(VPE)
    PerfInfoObs["Gdop"].append(GDOP)
    PerfInfoObs["Pdop"].append(PDOP)
    PerfInfoObs["Tdop"].append(TDOP)
    PerfInfoObs["Hdop"].append(HDOP)
    PerfInfoObs["Vdop"].append(VDOP)
    PerfInfoObs["NumSat"].append(NumSat)
    return PerfInfoObs

def computeFinalPerf(PerfInfoObs):
    # Calculate the final statistics from the accumulated performance information
    
    finalPerf = OrderedDict({})
    finalPerf = {
        "Rcvr": PerfInfoObs["Rcvr"],
        # Total samples and no-solution samples
        "Samples": len(PerfInfoObs["Hpe"]) + PerfInfoObs["SamNoSol"],
        "SamNoSol": PerfInfoObs["SamNoSol"],
        
        # Satellite count statistics (min and max from PerfInfoObs)
        "Nsvmin": min(PerfInfoObs["NumSat"]),
        "Nsvmax": max(PerfInfoObs["NumSat"]),
        
        # RMS Errors for HPE and VPE
        "Hperms": np.sqrt(np.mean(np.array(PerfInfoObs["Hpe"])**2)),
        "Vperms": np.sqrt(np.mean(np.array(PerfInfoObs["Vpe"])**2)),
        
        # 95th percentile errors
        "Hpe95": np.percentile(PerfInfoObs["Hpe"], 95),
        "Vpe95": np.percentile(PerfInfoObs["Vpe"], 95),
        
        # Maximum errors observed
        "HpeMax":np.max(PerfInfoObs["Hpe"]),
        "VpeMax":np.max(PerfInfoObs["Vpe"]),
        
        # Maximum DOPs observed
        "PdopMax": np.max(PerfInfoObs["Pdop"]),
        "HdopMax": np.max(PerfInfoObs["Hdop"]),
        "VdopMax": np.max(PerfInfoObs["Vdop"]),
    }

    return finalPerf