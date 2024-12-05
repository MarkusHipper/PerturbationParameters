
import numpy as np
import scipy.io
from scipy.integrate import trapezoid, cumtrapz
import csv

def get_perturbation_parameters(Beltvelocity, Frequency, Refpoint_TD, Refpoint_FO, Multiplier_STD):
    """
    Calculates various perturbation parameters from belt velocity data.

    Args:
        Beltvelocity (np.ndarray): Array of belt velocities for a trial.
        Frequency (int): Sampling frequency of the data.
        Refpoint_TD (float): Reference touchdown time index.
        Refpoint_FO (float): Reference foot-off time index.
        Multiplier_STD (float): Multiplier for standard deviation threshold.

    Returns:
        dict: A dictionary containing calculated perturbation parameters.
    """
    # Calculate baseline velocity and its standard deviation
    Baselinevelocity = np.mean(Beltvelocity[:3 * Frequency])
    Baselinevelocity_std = np.std(Beltvelocity[:3 * Frequency])

    # Find maximum absolute perturbation velocity and its index
    PerturbationVelocity_abs = np.max(np.abs(Beltvelocity))
    PerturbationVelocity_index = np.argmax(np.abs(Beltvelocity))
    PerturbationVelocity = Beltvelocity[PerturbationVelocity_index]

    # Identify the start of the perturbation
    PerturbationStart = None
    threshold = Baselinevelocity + Multiplier_STD * Baselinevelocity_std if PerturbationVelocity > 0 else \
                Baselinevelocity - Multiplier_STD * Baselinevelocity_std
    for i in range(PerturbationVelocity_index, -1, -1):
        if (PerturbationVelocity > 0 and Beltvelocity[i] <= threshold) or \
           (PerturbationVelocity < 0 and Beltvelocity[i] >= threshold):
            PerturbationStart = i
            break

    # Identify the end of the perturbation
    PerturbationEnd = None
    for i in range(PerturbationVelocity_index, len(Beltvelocity)):
        if (PerturbationVelocity > 0 and Beltvelocity[i] <= threshold) or \
           (PerturbationVelocity < 0 and Beltvelocity[i] >= threshold):
            PerturbationEnd = i
            break

    # Calculate perturbation duration, offsets, and distances
    velocity_diff = Beltvelocity[PerturbationStart:PerturbationEnd + 1] - Baselinevelocity
    PerturbationDistance = trapezoid(velocity_diff) / Frequency
    PerturbationOffset = (PerturbationStart - Refpoint_TD) / Frequency
    PerturbationOffset_relative = (PerturbationOffset / ((Refpoint_FO - Refpoint_TD) / Frequency)
                                    if Refpoint_FO != 0 else 'Refpoint_FO is missing')
    Acceleration1Duration = (PerturbationVelocity_index - PerturbationStart) / Frequency
    Acceleration2Duration = (PerturbationEnd - PerturbationVelocity_index) / Frequency
    PerturbationDuration = (PerturbationEnd - PerturbationStart) / Frequency
    VelocityAmplitude = abs(Baselinevelocity - PerturbationVelocity)

    return {
        "Baselinevelocity": Baselinevelocity,
        "PerturbationVelocity": PerturbationVelocity,
        "PerturbationOffset": PerturbationOffset,
        "PerturbationOffset_relative": PerturbationOffset_relative,
        "Acceleration1Duration": Acceleration1Duration,
        "Acceleration2Duration": Acceleration2Duration,
        "PerturbationDuration": PerturbationDuration,
        "VelocityAmplitude": VelocityAmplitude,
        "PerturbationDistance": PerturbationDistance
    }

def access_nested_data_directly(input_data):
    """
    Extracts 'Beltvelocity', 'Referencepoint_TD', and 'Referencepoint_FO' 
    from a nested MATLAB .mat data structure.

    Args:
        input_data (np.ndarray): Nested MATLAB .mat data structure.

    Returns:
        dict: Extracted data as NumPy arrays.
    """
    belt_velocities = []
    ref_td = []
    ref_fo = []

    try:
        # Iterate through the nested structure to extract relevant data
        for participant in input_data['Participant']:
            for trial in participant[0]:
                for sub_trial in trial[0]:
                    for measurement in sub_trial[0]:
                        belt_velocity = measurement[0][0]
                        ref_td_value = measurement[1][0]
                        ref_fo_value = measurement[2][0]

                        # Append the flattened or relevant data
                        belt_velocities.append(belt_velocity.flatten())
                        ref_td.append(ref_td_value.flatten())
                        ref_fo.append(ref_fo_value.flatten())

        return {
            'Beltvelocity': np.hstack(belt_velocities),
            'Referencepoint_TD': np.hstack(ref_td),
            'Referencepoint_FO': np.hstack(ref_fo),
        }

    except Exception as e:
        print(f"Error accessing nested data: {e}")
        return None

def collect_belt_velocities(belt_velocity):
    """
    Collects and stacks belt velocity data into a 2D array.

    Args:
        belt_velocity (list): List of tuples containing belt velocity arrays.

    Returns:
        np.ndarray: A 2D array of stacked velocity data.
    """
    all_belt_velocities = []

    for bv in belt_velocity:
        velocity_array = bv[0][0]  # Extract the array
        velocity_array = velocity_array.flatten()  # Flatten to 1D
        all_belt_velocities.append(velocity_array)

    return np.array(all_belt_velocities)

if __name__ == "__main__":
    # Path to the .mat file
    mat_file_path = "\Inputdata.mat" #insert correct file path to 'Inputdata.mat'

    # Load the .mat file
    mat_data = scipy.io.loadmat(mat_file_path)

    # Extract nested data
    input_data = mat_data.get('Inputdata')
    result = access_nested_data_directly(input_data)

    if result:
        # Extract relevant arrays
        belt_velocity = result['Beltvelocity']
        td = result['Referencepoint_TD']
        fo = result['Referencepoint_FO']

        # Collect belt velocities
        all_belt_velocities = collect_belt_velocities(belt_velocity)

        # Compute perturbation parameters for each velocity profile
        pert_params_list = []
        for i in range(len(all_belt_velocities)):
            pert_params = get_perturbation_parameters(all_belt_velocities[i], 200, td[i], fo[i], 1)
            pert_params_list.append(pert_params)

        # Write results to a CSV file
        header = pert_params_list[0].keys()
        output_path = r"C:\Users\CVonDiecken\Downloads\AP_pert_paramater_script\perturbation_params.csv"
        with open(output_path, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=header)
            writer.writeheader()
            writer.writerows(pert_params_list)

        print("Perturbation parameters saved to 'perturbation_params.csv'")
