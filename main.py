from machine import Pin, ADC
import utime, time
import onewire
import ds18x20

# Define ADC pin
adc = ADC(Pin(26))
# Excitation LED
led = Pin(0, Pin.OUT)
led.off()

# Define Temp sensor pins
power_pin = machine.Pin(1, machine.Pin.OUT)
data_pin = machine.Pin(2)

# Initialize DS18B20
ow = onewire.OneWire(data_pin)
ds = ds18x20.DS18X20(ow)

# Set up CSV file
filename = "adc_data.txt"
header = "Time (ms),ADC Value,Temp\n"

def read_temperature():
    # Turn on the sensor
    power_pin.value(1)
    time.sleep(1)  # Wait for the sensor to stabilize
    
    roms = ds.scan()  # Scan for devices on the bus
    if len(roms) == 0:
        print("No DS18B20 found!")
        power_pin.value(0)
        return None
    
    # Start temperature conversion
    ds.convert_temp()
    time.sleep_ms(750)  # Wait for conversion to complete
    
    # Read the temperature
    temperature = ds.read_temp(roms[0])
    
    # Turn off the sensor
    power_pin.value(0)
    
    return temperature

def generate_array():
    result = []
    
    # First segment: 0.01 to 0.29 in steps of 0.01
    for i in range(1, 30):
        result.append(i / 100)
    
    # Second segment: 0.3 to 3 in steps of 0.1
    for i in range(3, 31):
        result.append(i / 10)
    
    # Third segment: 4 to 30 in steps of 1
    for i in range(4, 31):
        result.append(i)
    
    # Fourth segment: 40 to 300 in steps of 10
    for i in range(40, 301, 10):
        result.append(i)
    
    # Fifth segment: 400 to 3000 in steps of 100
    for i in range(400, 3100, 100):
        result.append(i)
    
    # Sixth segment: 4000 to 5000 in steps of 1000
    for i in range(4000, 6000, 1000):
        result.append(i)
    
    return result

def read_adc(sample_times, adc):
    data = []
    start_time = utime.ticks_us()
    
    for i in range(10):
        adc_value = adc.read_u16()
        data.append([utime.ticks_us(), adc_value])

    for sample_time in sample_times:
        # Convert sample time from ms to us
        sample_time_us = sample_time * 1000

        while True:
            current_time = utime.ticks_us()
            if current_time - start_time >= sample_time_us:
                break

        adc_value = adc.read_u16()
        #data.append(((current_time - start_time) / 1000.0, adc_value))
        data.append([utime.ticks_us(), adc_value])
        
    for d in data:
        d[0] = (d[0] - start_time)/1000

    return data
 
def main():
    temp_ini = read_temperature()
    sample_times = generate_array()
    led.on()
    data = read_adc(sample_times, adc)
    #time.sleep(10)
    led.off()
    temp_end = read_temperature()

    with open(filename, mode='w') as file:
        file.write(header)
        file.write(f",,{temp_ini}\n")
        for line in data:
            file.write("{},{}\n".format(*line))
            print("time:{}, adc:{}".format(*line))
        file.write(f",,{temp_end}\n")

    print("Data collection complete.")
    
    second_column = [row[1] for row in data]
    min_value = min(second_column)
    max_value = max(second_column)
    fv_fm = (max_value-min_value)/max_value
    print("fv/fm:",fv_fm)

if __name__ == "__main__":
    main()
