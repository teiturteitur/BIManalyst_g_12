pressure_loss_db = {

    # Source of fitting zeta (ζ) values: Danvak "Climatic Systems", 2. ed., 1997, eds. H.E. Hansen, P. Kjerulf Jensen, Ole B. Stampe


    # =====================================================================
    # 1. BENDS – ROUND DUCTS
    # =====================================================================
    "bend_round": [
        # r/d = 1
        {"r_d": 1.0, "diameter_mm": 75,  "zeta": 0.44},
        {"r_d": 1.0, "diameter_mm": 100, "zeta": 0.37},
        {"r_d": 1.0, "diameter_mm": 125, "zeta": 0.30},
        {"r_d": 1.0, "diameter_mm": 150, "zeta": 0.25},
        {"r_d": 1.0, "diameter_mm": 200, "zeta": 0.24},
        {"r_d": 1.0, "diameter_mm": 250, "zeta": 0.24},

        # r/d = 1.5
        {"r_d": 1.5, "diameter_mm": 75,  "zeta": 0.30},
        {"r_d": 1.5, "diameter_mm": 100, "zeta": 0.21},
        {"r_d": 1.5, "diameter_mm": 125, "zeta": 0.16},
        {"r_d": 1.5, "diameter_mm": 150, "zeta": 0.14},
        {"r_d": 1.5, "diameter_mm": 200, "zeta": 0.11},
        {"r_d": 1.5, "diameter_mm": 250, "zeta": 0.11},
    ],

    # =====================================================================
    # 2. BENDS – RECTANGULAR DUCTS
    # =====================================================================
    "bend_rectangular": [
        # r/h = 0.5
        {"r_h": 0.5, "b_h": 0.25, "zeta": 1.53},
        {"r_h": 0.5, "b_h": 0.50, "zeta": 1.38},
        {"r_h": 0.5, "b_h": 0.75, "zeta": 1.29},
        {"r_h": 0.5, "b_h": 1.00, "zeta": 1.18},
        {"r_h": 0.5, "b_h": 1.50, "zeta": 1.06},
        {"r_h": 0.5, "b_h": 2.00, "zeta": 1.00},
        {"r_h": 0.5, "b_h": 4.00, "zeta": 1.06},

        # r/h = 0.75
        {"r_h": 0.75, "b_h": 0.25, "zeta": 0.57},
        {"r_h": 0.75, "b_h": 0.50, "zeta": 0.52},
        {"r_h": 0.75, "b_h": 0.75, "zeta": 0.48},
        {"r_h": 0.75, "b_h": 1.00, "zeta": 0.44},
        {"r_h": 0.75, "b_h": 1.50, "zeta": 0.40},
        {"r_h": 0.75, "b_h": 2.00, "zeta": 0.39},
        {"r_h": 0.75, "b_h": 4.00, "zeta": 0.40},

        # r/h = 1
        {"r_h": 1.0, "b_h": 0.25, "zeta": 0.27},
        {"r_h": 1.0, "b_h": 0.50, "zeta": 0.25},
        {"r_h": 1.0, "b_h": 0.75, "zeta": 0.23},
        {"r_h": 1.0, "b_h": 1.00, "zeta": 0.21},
        {"r_h": 1.0, "b_h": 1.50, "zeta": 0.19},
        {"r_h": 1.0, "b_h": 2.00, "zeta": 0.18},
        {"r_h": 1.0, "b_h": 4.00, "zeta": 0.19},

        # r/h = 1.5
        {"r_h": 1.5, "b_h": 0.25, "zeta": 0.22},
        {"r_h": 1.5, "b_h": 0.50, "zeta": 0.20},
        {"r_h": 1.5, "b_h": 0.75, "zeta": 0.19},
        {"r_h": 1.5, "b_h": 1.00, "zeta": 0.17},
        {"r_h": 1.5, "b_h": 1.50, "zeta": 0.15},
        {"r_h": 1.5, "b_h": 2.00, "zeta": 0.14},
        {"r_h": 1.5, "b_h": 4.00, "zeta": 0.15},

        # r/h = 2
        {"r_h": 2.0, "b_h": 0.25, "zeta": 0.20},
        {"r_h": 2.0, "b_h": 0.50, "zeta": 0.18},
        {"r_h": 2.0, "b_h": 0.75, "zeta": 0.16},
        {"r_h": 2.0, "b_h": 1.00, "zeta": 0.15},
        {"r_h": 2.0, "b_h": 1.50, "zeta": 0.14},
        {"r_h": 2.0, "b_h": 2.00, "zeta": 0.13},
        {"r_h": 2.0, "b_h": 4.00, "zeta": 0.14},
    ],

    # =====================================================================
    # 3. EXPANSIONS
    # =====================================================================
    # Table: ζ1 vs A2/A1 for angles 10, 20, 30 … 150 deg
    "expansion": [
        # angle_deg = 10°
        {'angle_deg': 10,  'A2_A1': 2, 'zeta': 0.11},
        {'angle_deg': 10,  'A2_A1': 4, 'zeta': 0.16},
        {'angle_deg': 10,  'A2_A1': 10, 'zeta': 0.21},
        {'angle_deg': 10,  'A2_A1': 16, 'zeta': 0.21},
        # angle_deg = 15°
        {'angle_deg': 15,  'A2_A1': 2, 'zeta': 0.13},
        {'angle_deg': 15,  'A2_A1': 4, 'zeta': 0.22},
        {'angle_deg': 15,  'A2_A1': 10, 'zeta': 0.28},
        {'angle_deg': 15,  'A2_A1': 16, 'zeta': 0.29},
        # angle_deg = 20°
        {'angle_deg': 20,  'A2_A1': 2, 'zeta': 0.19},
        {'angle_deg': 20,  'A2_A1': 4, 'zeta': 0.30},
        {'angle_deg': 20,  'A2_A1': 10, 'zeta': 0.37},
        {'angle_deg': 20,  'A2_A1': 16, 'zeta': 0.38},
        # angle_deg = 30°
        {'angle_deg': 30,  'A2_A1': 2, 'zeta': 0.32},
        {'angle_deg': 30,  'A2_A1': 4, 'zeta': 0.46},
        {'angle_deg': 30,  'A2_A1': 10, 'zeta': 0.59},
        {'angle_deg': 30,  'A2_A1': 16, 'zeta': 0.60},
        # angle_deg = 45°
        {'angle_deg': 45,  'A2_A1': 2, 'zeta': 0.33},
        {'angle_deg': 45,  'A2_A1': 4, 'zeta': 0.61},
        {'angle_deg': 45,  'A2_A1': 10, 'zeta': 0.76},
        {'angle_deg': 45,  'A2_A1': 16, 'zeta': 0.84},
        # angle_deg = 60°
        {'angle_deg': 60,  'A2_A1': 2, 'zeta': 0.33},
        {'angle_deg': 60,  'A2_A1': 4, 'zeta': 0.61},
        {'angle_deg': 60,  'A2_A1': 10, 'zeta': 0.79},
        {'angle_deg': 60,  'A2_A1': 16, 'zeta': 0.85},
        # angle_deg = 90°
        {'angle_deg': 90,  'A2_A1': 2, 'zeta': 0.32},
        {'angle_deg': 90,  'A2_A1': 4, 'zeta': 0.64},
        {'angle_deg': 90,  'A2_A1': 10, 'zeta': 0.83},
        {'angle_deg': 90,  'A2_A1': 16, 'zeta': 0.88},
        # angle_deg = 120°
        {'angle_deg': 120, 'A2_A1': 2, 'zeta': 0.31},
        {'angle_deg': 120, 'A2_A1': 4, 'zeta': 0.63},
        {'angle_deg': 120, 'A2_A1': 10, 'zeta': 0.84},
        {'angle_deg': 120, 'A2_A1': 16, 'zeta': 0.88},
        # angle_deg = 150°
        {'angle_deg': 150, 'A2_A1': 2, 'zeta': 0.30},
        {'angle_deg': 150, 'A2_A1': 4, 'zeta': 0.62},
        {'angle_deg': 150, 'A2_A1': 10, 'zeta': 0.83},
        {'angle_deg': 150, 'A2_A1': 16, 'zeta': 0.88},
        # angle_deg = 180°
        {'angle_deg': 180, 'A2_A1': 2, 'zeta': 0.30},
        {'angle_deg': 180, 'A2_A1': 4, 'zeta': 0.62},
        {'angle_deg': 180, 'A2_A1': 10, 'zeta': 0.83},
        {'angle_deg': 180, 'A2_A1': 16, 'zeta': 0.88}

    ],

    # =====================================================================
    # 4. REDUCTIONS
    # =====================================================================
    "reduction": [

        # angle_deg: = 10°
        {'angle_deg': 10,  'A1_A2': 0.1,  'zeta': 0.05},
        {'angle_deg': 10,  'A1_A2': 0.17, 'zeta': 0.05},
        {'angle_deg': 10,  'A1_A2': 0.25, 'zeta': 0.05},
        {'angle_deg': 10,  'A1_A2': 0.50, 'zeta': 0.05},
        # angle_deg: = 15°
        {'angle_deg': 15,  'A1_A2': 0.1,  'zeta': 0.05},
        {'angle_deg': 15,  'A1_A2': 0.17, 'zeta': 0.04},
        {'angle_deg': 15,  'A1_A2': 0.25, 'zeta': 0.04},
        {'angle_deg': 15,  'A1_A2': 0.50, 'zeta': 0.05},
        # angle_deg: = 20°
        {'angle_deg': 20,  'A1_A2': 0.1,  'zeta': 0.05},
        {'angle_deg': 20,  'A1_A2': 0.17, 'zeta': 0.04},
        {'angle_deg': 20,  'A1_A2': 0.25, 'zeta': 0.04},
        {'angle_deg': 20,  'A1_A2': 0.50, 'zeta': 0.05},
        # angle_deg: = 30°
        {'angle_deg': 30,  'A1_A2': 0.1,  'zeta': 0.05},
        {'angle_deg': 30,  'A1_A2': 0.17, 'zeta': 0.04},
        {'angle_deg': 30,  'A1_A2': 0.25, 'zeta': 0.04},
        {'angle_deg': 30,  'A1_A2': 0.50, 'zeta': 0.05},
        # angle_deg: = 45°
        {'angle_deg': 45,  'A1_A2': 0.1,  'zeta': 0.07},
        {'angle_deg': 45,  'A1_A2': 0.17, 'zeta': 0.06},
        {'angle_deg': 45,  'A1_A2': 0.25, 'zeta': 0.07},
        {'angle_deg': 45,  'A1_A2': 0.50, 'zeta': 0.06},
        # angle_deg: = 60°
        {'angle_deg': 60,  'A1_A2': 0.1,  'zeta': 0.08},
        {'angle_deg': 60,  'A1_A2': 0.17, 'zeta': 0.07},
        {'angle_deg': 60,  'A1_A2': 0.25, 'zeta': 0.07},
        {'angle_deg': 60,  'A1_A2': 0.50, 'zeta': 0.06},
        # angle_deg: = 90°
        {'angle_deg': 90,  'A1_A2': 0.1,  'zeta': 0.19},
        {'angle_deg': 90,  'A1_A2': 0.17, 'zeta': 0.18},
        {'angle_deg': 90,  'A1_A2': 0.25, 'zeta': 0.17},
        {'angle_deg': 90,  'A1_A2': 0.50, 'zeta': 0.12},
        # angle_deg: = 120°
        {'angle_deg': 120, 'A1_A2': 0.1,  'zeta': 0.29},
        {'angle_deg': 120, 'A1_A2': 0.17, 'zeta': 0.28},
        {'angle_deg': 120, 'A1_A2': 0.25, 'zeta': 0.27},
        {'angle_deg': 120, 'A1_A2': 0.50, 'zeta': 0.18},
        # angle_deg: = 150°
        {'angle_deg': 150, 'A1_A2': 0.1,  'zeta': 0.37},
        {'angle_deg': 150, 'A1_A2': 0.17, 'zeta': 0.36},
        {'angle_deg': 150, 'A1_A2': 0.25, 'zeta': 0.35},
        {'angle_deg': 150, 'A1_A2': 0.50, 'zeta': 0.24},
        # angle_deg: = 180°
        {'angle_deg': 180, 'A1_A2': 0.1,  'zeta': 0.43},
        {'angle_deg': 180, 'A1_A2': 0.17, 'zeta': 0.42},
        {'angle_deg': 180, 'A1_A2': 0.25, 'zeta': 0.41},
        {'angle_deg': 180, 'A1_A2': 0.50, 'zeta': 0.26}


    ],

    # =====================================================================
    # 5. T-SECTIONS – FLOW THROUGH
    # =====================================================================
    "t_through": [
        # A1_A2 = 0.1
        {"A1_A2": 0.1, "qv1_qv": 0.1, "zeta": 0.13},
        {"A1_A2": 0.1, "qv1_qv": 0.2, "zeta": 0.16},

        # A1_A2 = 0.2
        {"A1_A2": 0.2, "qv1_qv": 0.1, "zeta": 0.20},
        {"A1_A2": 0.2, "qv1_qv": 0.2, "zeta": 0.13},
        {"A1_A2": 0.2, "qv1_qv": 0.3, "zeta": 0.15},
        {"A1_A2": 0.2, "qv1_qv": 0.4, "zeta": 0.16},
        {"A1_A2": 0.2, "qv1_qv": 0.5, "zeta": 0.28},

        # A1_A2 = 0.3
        {"A1_A2": 0.3, "qv1_qv": 0.1, "zeta": 0.90},
        {"A1_A2": 0.3, "qv1_qv": 0.2, "zeta": 0.13},
        {"A1_A2": 0.3, "qv1_qv": 0.3, "zeta": 0.13},
        {"A1_A2": 0.3, "qv1_qv": 0.4, "zeta": 0.14},
        {"A1_A2": 0.3, "qv1_qv": 0.5, "zeta": 0.15},
        {"A1_A2": 0.3, "qv1_qv": 0.6, "zeta": 0.16},
        {"A1_A2": 0.3, "qv1_qv": 0.7, "zeta": 0.20},

        # A1_A2 = 0.4
        {"A1_A2": 0.4, "qv1_qv": 0.1, "zeta": 2.88},
        {"A1_A2": 0.4, "qv1_qv": 0.2, "zeta": 0.20},
        {"A1_A2": 0.4, "qv1_qv": 0.3, "zeta": 0.14},
        {"A1_A2": 0.4, "qv1_qv": 0.4, "zeta": 0.13},
        {"A1_A2": 0.4, "qv1_qv": 0.5, "zeta": 0.14},
        {"A1_A2": 0.4, "qv1_qv": 0.6, "zeta": 0.15},
        {"A1_A2": 0.4, "qv1_qv": 0.7, "zeta": 0.15},
        {"A1_A2": 0.4, "qv1_qv": 0.8, "zeta": 0.16},
        {"A1_A2": 0.4, "qv1_qv": 0.9, "zeta": 0.34},

        # A1_A2 = 0.5
        {"A1_A2": 0.5, "qv1_qv": 0.1, "zeta": 6.25},
        {"A1_A2": 0.5, "qv1_qv": 0.2, "zeta": 0.37},
        {"A1_A2": 0.5, "qv1_qv": 0.3, "zeta": 0.17},
        {"A1_A2": 0.5, "qv1_qv": 0.4, "zeta": 0.14},
        {"A1_A2": 0.5, "qv1_qv": 0.5, "zeta": 0.13},
        {"A1_A2": 0.5, "qv1_qv": 0.6, "zeta": 0.14},
        {"A1_A2": 0.5, "qv1_qv": 0.7, "zeta": 0.14},
        {"A1_A2": 0.5, "qv1_qv": 0.8, "zeta": 0.15},
        {"A1_A2": 0.5, "qv1_qv": 0.9, "zeta": 0.15},

        # A1_A2 = 0.6
        {"A1_A2": 0.6, "qv1_qv": 0.1, "zeta": 11.88},
        {"A1_A2": 0.6, "qv1_qv": 0.2, "zeta": 0.90},
        {"A1_A2": 0.6, "qv1_qv": 0.3, "zeta": 0.20},
        {"A1_A2": 0.6, "qv1_qv": 0.4, "zeta": 0.13},
        {"A1_A2": 0.6, "qv1_qv": 0.5, "zeta": 0.14},
        {"A1_A2": 0.6, "qv1_qv": 0.6, "zeta": 0.13},
        {"A1_A2": 0.6, "qv1_qv": 0.7, "zeta": 0.14},
        {"A1_A2": 0.6, "qv1_qv": 0.8, "zeta": 0.14},
        {"A1_A2": 0.6, "qv1_qv": 0.9, "zeta": 0.15},

        # A1_A2 = 0.7
        {"A1_A2": 0.7, "qv1_qv": 0.1, "zeta": 18.62},
        {"A1_A2": 0.7, "qv1_qv": 0.2, "zeta": 1.71},
        {"A1_A2": 0.7, "qv1_qv": 0.3, "zeta": 0.33},
        {"A1_A2": 0.7, "qv1_qv": 0.4, "zeta": 0.18},
        {"A1_A2": 0.7, "qv1_qv": 0.5, "zeta": 0.16},
        {"A1_A2": 0.7, "qv1_qv": 0.6, "zeta": 0.14},
        {"A1_A2": 0.7, "qv1_qv": 0.7, "zeta": 0.13},
        {"A1_A2": 0.7, "qv1_qv": 0.8, "zeta": 0.15},
        {"A1_A2": 0.7, "qv1_qv": 0.9, "zeta": 0.14},

        # A1_A2 = 0.8
        {"A1_A2": 0.8, "qv1_qv": 0.1, "zeta": 26.88},
        {"A1_A2": 0.8, "qv1_qv": 0.2, "zeta": 2.88},
        {"A1_A2": 0.8, "qv1_qv": 0.3, "zeta": 0.5},
        {"A1_A2": 0.8, "qv1_qv": 0.4, "zeta": 0.20},
        {"A1_A2": 0.8, "qv1_qv": 0.5, "zeta": 0.15},
        {"A1_A2": 0.8, "qv1_qv": 0.6, "zeta": 0.16},
        {"A1_A2": 0.8, "qv1_qv": 0.7, "zeta": 0.13},
        {"A1_A2": 0.8, "qv1_qv": 0.8, "zeta": 0.13},
        {"A1_A2": 0.8, "qv1_qv": 0.9, "zeta": 0.14},

        # A1_A2 = 0.9
        {"A1_A2": 0.9, "qv1_qv": 0.1, "zeta": 36.45},
        {"A1_A2": 0.9, "qv1_qv": 0.2, "zeta": 4.46},
        {"A1_A2": 0.9, "qv1_qv": 0.3, "zeta": 0.90},
        {"A1_A2": 0.9, "qv1_qv": 0.4, "zeta": 0.30},
        {"A1_A2": 0.9, "qv1_qv": 0.5, "zeta": 0.19},
        {"A1_A2": 0.9, "qv1_qv": 0.6, "zeta": 0.16},
        {"A1_A2": 0.9, "qv1_qv": 0.7, "zeta": 0.15},
        {"A1_A2": 0.9, "qv1_qv": 0.8, "zeta": 0.14},
        {"A1_A2": 0.9, "qv1_qv": 0.9, "zeta": 0.13},
    ],



    # =====================================================================
    # 6. T-SECTIONS – BRANCHING α = 90°
    # =====================================================================
    "t_branch_90": [
        # A2_Atot = 0.1
        {"A2_Atot": 0.1, "qv2_qv": 0.1, "zeta": 1.20},
        {"A2_Atot": 0.1, "qv2_qv": 0.2, "zeta": 0.62},
        {"A2_Atot": 0.1, "qv2_qv": 0.3, "zeta": 0.80},
        {"A2_Atot": 0.1, "qv2_qv": 0.4, "zeta": 1.28},
        {"A2_Atot": 0.1, "qv2_qv": 0.5, "zeta": 1.99},
        {"A2_Atot": 0.1, "qv2_qv": 0.6, "zeta": 2.92},
        {"A2_Atot": 0.1, "qv2_qv": 0.7, "zeta": 4.07},
        {"A2_Atot": 0.1, "qv2_qv": 0.8, "zeta": 5.44},
        {"A2_Atot": 0.1, "qv2_qv": 0.9, "zeta": 7.02},

        # A2_Atot = 0.2
        {"A2_Atot": 0.2, "qv2_qv": 0.1, "zeta": 4.10},
        {"A2_Atot": 0.2, "qv2_qv": 0.2, "zeta": 1.20},
        {"A2_Atot": 0.2, "qv2_qv": 0.3, "zeta": 0.72},
        {"A2_Atot": 0.2, "qv2_qv": 0.4, "zeta": 0.62},
        {"A2_Atot": 0.2, "qv2_qv": 0.5, "zeta": 0.66},
        {"A2_Atot": 0.2, "qv2_qv": 0.6, "zeta": 0.80},
        {"A2_Atot": 0.2, "qv2_qv": 0.7, "zeta": 1.01},
        {"A2_Atot": 0.2, "qv2_qv": 0.8, "zeta": 1.28},
        {"A2_Atot": 0.2, "qv2_qv": 0.9, "zeta": 1.60},

        # A2_Atot = 0.3
        {"A2_Atot": 0.3, "qv2_qv": 0.1, "zeta": 8.99},
        {"A2_Atot": 0.3, "qv2_qv": 0.2, "zeta": 2.40},
        {"A2_Atot": 0.3, "qv2_qv": 0.3, "zeta": 1.20},
        {"A2_Atot": 0.3, "qv2_qv": 0.4, "zeta": 0.81},
        {"A2_Atot": 0.3, "qv2_qv": 0.5, "zeta": 0.66},
        {"A2_Atot": 0.3, "qv2_qv": 0.6, "zeta": 0.62},
        {"A2_Atot": 0.3, "qv2_qv": 0.7, "zeta": 0.64},
        {"A2_Atot": 0.3, "qv2_qv": 0.8, "zeta": 0.70},
        {"A2_Atot": 0.3, "qv2_qv": 0.9, "zeta": 0.80},

        # A2_Atot = 0.4
        {"A2_Atot": 0.4, "qv2_qv": 0.1, "zeta": 15.89},
        {"A2_Atot": 0.4, "qv2_qv": 0.2, "zeta": 4.10},
        {"A2_Atot": 0.4, "qv2_qv": 0.3, "zeta": 1.94},
        {"A2_Atot": 0.4, "qv2_qv": 0.4, "zeta": 1.20},
        {"A2_Atot": 0.4, "qv2_qv": 0.5, "zeta": 0.88},
        {"A2_Atot": 0.4, "qv2_qv": 0.6, "zeta": 0.72},
        {"A2_Atot": 0.4, "qv2_qv": 0.7, "zeta": 0.64},
        {"A2_Atot": 0.4, "qv2_qv": 0.8, "zeta": 0.62},
        {"A2_Atot": 0.4, "qv2_qv": 0.9, "zeta": 0.63},

        # A2_Atot = 0.5
        {"A2_Atot": 0.5, "qv2_qv": 0.1, "zeta": 24.80},
        {"A2_Atot": 0.5, "qv2_qv": 0.2, "zeta": 6.29},
        {"A2_Atot": 0.5, "qv2_qv": 0.3, "zeta": 2.91},
        {"A2_Atot": 0.5, "qv2_qv": 0.4, "zeta": 1.74},
        {"A2_Atot": 0.5, "qv2_qv": 0.5, "zeta": 1.20},
        {"A2_Atot": 0.5, "qv2_qv": 0.6, "zeta": 0.92},
        {"A2_Atot": 0.5, "qv2_qv": 0.7, "zeta": 0.77},
        {"A2_Atot": 0.5, "qv2_qv": 0.8, "zeta": 0.68},
        {"A2_Atot": 0.5, "qv2_qv": 0.9, "zeta": 0.63},

        # A2_Atot = 0.6
        {"A2_Atot": 0.6, "qv2_qv": 0.1, "zeta": 35.73},
        {"A2_Atot": 0.6, "qv2_qv": 0.2, "zeta": 8.99},
        {"A2_Atot": 0.6, "qv2_qv": 0.3, "zeta": 4.10},
        {"A2_Atot": 0.6, "qv2_qv": 0.4, "zeta": 2.40},
        {"A2_Atot": 0.6, "qv2_qv": 0.5, "zeta": 1.62},
        {"A2_Atot": 0.6, "qv2_qv": 0.6, "zeta": 1.20},
        {"A2_Atot": 0.6, "qv2_qv": 0.7, "zeta": 0.96},
        {"A2_Atot": 0.6, "qv2_qv": 0.8, "zeta": 0.81},
        {"A2_Atot": 0.6, "qv2_qv": 0.9, "zeta": 0.72},

        # A2_Atot = 0.7
        {"A2_Atot": 0.7, "qv2_qv": 0.1, "zeta": 48.67},
        {"A2_Atot": 0.7, "qv2_qv": 0.2, "zeta": 12.19},
        {"A2_Atot": 0.7, "qv2_qv": 0.3, "zeta": 5.51},
        {"A2_Atot": 0.7, "qv2_qv": 0.4, "zeta": 3.19},
        {"A2_Atot": 0.7, "qv2_qv": 0.5, "zeta": 2.12},
        {"A2_Atot": 0.7, "qv2_qv": 0.6, "zeta": 1.55},
        {"A2_Atot": 0.7, "qv2_qv": 0.7, "zeta": 1.20},
        {"A2_Atot": 0.7, "qv2_qv": 0.8, "zeta": 0.99},
        {"A2_Atot": 0.7, "qv2_qv": 0.9, "zeta": 0.85},

        # A2_Atot = 0.8
        {"A2_Atot": 0.8, "qv2_qv": 0.1, "zeta": 63.63},
        {"A2_Atot": 0.8, "qv2_qv": 0.2, "zeta": 15.89},
        {"A2_Atot": 0.8, "qv2_qv": 0.3, "zeta": 7.14},
        {"A2_Atot": 0.8, "qv2_qv": 0.4, "zeta": 4.10},
        {"A2_Atot": 0.8, "qv2_qv": 0.5, "zeta": 2.70},
        {"A2_Atot": 0.8, "qv2_qv": 0.6, "zeta": 1.94},
        {"A2_Atot": 0.8, "qv2_qv": 0.7, "zeta": 1.49},
        {"A2_Atot": 0.8, "qv2_qv": 0.8, "zeta": 1.20},
        {"A2_Atot": 0.8, "qv2_qv": 0.9, "zeta": 1.01},

        # A2_Atot = 0.9
        {"A2_Atot": 0.9, "qv2_qv": 0.1, "zeta": 80.60},
        {"A2_Atot": 0.9, "qv2_qv": 0.2, "zeta": 20.10},
        {"A2_Atot": 0.9, "qv2_qv": 0.3, "zeta": 8.99},
        {"A2_Atot": 0.9, "qv2_qv": 0.4, "zeta": 5.13},
        {"A2_Atot": 0.9, "qv2_qv": 0.5, "zeta": 3.36},
        {"A2_Atot": 0.9, "qv2_qv": 0.6, "zeta": 2.40},
        {"A2_Atot": 0.9, "qv2_qv": 0.7, "zeta": 1.83},
        {"A2_Atot": 0.9, "qv2_qv": 0.8, "zeta": 1.46},
        {"A2_Atot": 0.9, "qv2_qv": 0.9, "zeta": 1.20}
    ],
}