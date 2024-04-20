import os
import time
import csv

# Define resistance values and measurement interval
resistances = [100000, 50000, 25000, 12500, 6200, 3100, 1500]  # Ohms
measurement_interval = 500  # seconds

# Function to take and log measurements
def log_measurements(spi, i2c, ad5272_address, resistor_value):
    # Set potentiometer resistance
    with open(file_path, mode='a', newline='') as file:
        csv_writer = csv.writer(file)
        
        # Set potentiometer resistance
        set_ad5272_resistor(i2c, ad5272_address, resistor_value)
        
        # Log current and voltage for measurement_interval
        start_time = time.time()
        while (time.time() - start_time) < measurement_interval:
            i_reading = mcp3564_read_differential_channel_blocking(spi, 0)
            v = mcp3564_read_differential_channel_blocking(spi, 1)
            i = i_reading / (4.7 * 200)  # Adjust this calculation as needed for calibration
            power = v * i
            log_entry = [
                f"{time.time() - start_time:2.1f}", 
                f"{1000*i:2.3f}", 
                f"{v:1.5f}", 
                f"{power*1000:2.3f}", 
                f"{resistor_value:5.0f}"
            ]
            
            # Write log entry to CSV file
            csv_writer.writerow(log_entry)
            
            # Sleep for desired interval
            time.sleep(1)
    # set_ad5272_resistor(i2c, ad5272_address, resistor_value)
    
    # # Log current and voltage for measurement_interval
    # start_time = time.time()
    # while (time.time() - start_time) < measurement_interval:
    #     i_reading = mcp3564_read_differential_channel_blocking(spi, 0)
    #     v = mcp3564_read_differential_channel_blocking(spi, 1)
    #     i = i_reading / (4.7 * 200)  # Adjust this calculation as needed for calibration
    #     power = v * i
    #     print(f"Time: {time.time() - start_time:2.1f}s, Current = {1000*i:2.3f}mA, Voltage = {v:1.5f}V, Power = {power*1000:2.3f}mW, Resistance = {resistor_value:5.0f} Ohms")
    #     time.sleep(1)  # Adjust as necessary for how frequently you want to take measurements within the interval

# Main loop to cycle through resistance values
file_path = "measurement_log.csv"
# Ensure the header is written if the file is new
if not os.path.exists(file_path):
    with open(file_path, mode='w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(["Time (s)", "Current (mA)", "Voltage (V)", "Power (mW)", "Resistance (Ohms)"])

for resistance in resistances:
    sb.disconnect_mfc()
    log_measurements(spi, i2c, ad5272_address, 1023, file_path)  # Maximum resistance to simulate open circuit
    sb.connect_mfc()
    log_measurements(spi, i2c, ad5272_address, resistance, file_path)
# for resistance in resistances:
#     sb.disconnect_mfc()
#     log_measurements(spi, i2c, ad5272_address, 1023)  # Maximum resistance to simulate open circuit
#     sb.connect_mfc()
#     log_measurements(spi, i2c, ad5272_address, resistance)

print("Measurement sequence completed.")
