# ThermaBrick test article firmware

ESP32 controller firmware for the reduced-scale test article (TBK-PRC-002). It covers the five functions that test plan TBK-TST-001, section 1, requires: charge mode, hold mode, blower control, logging and the safe state. It is written for the Arduino framework and built with PlatformIO. Licensed MIT (see `LICENSE-SOFTWARE`).

> **Safety:** This firmware is the second layer of protection, not the first. The REX-C100 limit and the latching relay open the heater circuit at 600 °C whatever the ESP32 is doing. Never bridge or bypass them, and run TBK-TST-001 TP1 before any heated test.

## Layout

| Path | Contents |
| --- | --- |
| `src/main.cpp` | Controller: thermocouples, heater burst firing, blower, HTTP API, log buffer |
| `lib/control/` | Control and safety logic with no Arduino dependency: PI loops, fault latching, MAX6675 decoding, airflow and power math |
| `test/test_control/` | Unit tests for `lib/control`, run on the host |
| `tools/logger.py` | Logging host: polls the controller and writes the test CSV; also the heartbeat |
| `tools/git_rev.py` | Stamps the build with the Git commit |
| `include/secrets.example.h` | Template for Wi-Fi credentials and the API token |

## Build and flash

```bash
pip install platformio
```

```bash
cp firmware/include/secrets.example.h firmware/include/secrets.h
```

Edit `secrets.h` with the Wi-Fi name, password and a long random `API_TOKEN`. The file is ignored by Git. Then, from `firmware/`:

```bash
pio test -e native
```

```bash
pio run -e esp32dev -t upload
```

```bash
pio device monitor
```

The monitor prints the IP address once Wi-Fi connects, then one CSV row every 10 s. Build `esp32dev_test` instead only for TP1 step 5. It adds an `/inject` endpoint that fakes T1, and it must never be used for a heated test.

## Wiring

The complete circuit, including the 120 V side, is the schematic TBK-DWG-003 (`cad/drawings/TBK-DWG-003.pdf`), with KiCad source in `electronics/test-article/`. Table 1 lists the ESP32 connections. The optional controller board, TBK-DWG-004, uses the same pins. On that board GPIO 26 drives the SSR through a 2N3904 and GPIO 25 drives an IRLZ44N; high means on in both cases, so the firmware is unchanged.

| Signal | ESP32 GPIO | Connects to |
| --- | --- | --- |
| SCK (shared) | 18 | SCK on all five MAX6675 modules |
| SO (shared) | 19 | SO on all five MAX6675 modules |
| CS, T1 well wall (control) | 5 | MAX6675 #1 |
| CS, T3 sand center | 17 | MAX6675 #2 |
| CS, T4 sand outer | 16 | MAX6675 #3 |
| CS, T5 exchanger outlet air | 4 | MAX6675 #4 |
| CS, T6 room air | 22 | MAX6675 #5 |
| SSR input + | 26 | SSR terminal 3, with a **10 kΩ pull-down from GPIO 26 to GND** |
| Blower PWM | 25 | MOSFET module signal input, with a 10 kΩ pull-down to GND |
| 5 V and GND | 5V, GND | 12 V to 5 V buck converter; MAX6675 modules take 3.3 V |

*Table 1. Controller wiring.*

Generic SSR-25DA relays specify a 3 V to 32 V input, so 3.3 V from the GPIO is near the bottom of their range. If the SSR's LED does not light reliably, drive its input from 5 V through a small NPN transistor, and keep the pull-down on the GPIO. The pull-down on GPIO 26 is required. It holds the SSR off while the ESP32 boots, resets or is unprogrammed (TBK-TST-001, section 1, item 5). T2 is not wired to the ESP32; it goes only to the REX-C100.

The heater circuit is the 120 V line through the 10 A fuse, then the latching relay contacts, then the SSR, then the four heaters in parallel. The latching relay coil circuit is the line through STOP (normally closed), then START (normally open) in parallel with the relay's own holding contact, then the REX-C100 relay (closed below 600 °C), then the coil.

## How it works

- **Thermocouples.** All five channels are read once a second, by a bit-banged read with the timing of the Adafruit driver. A frame of all zeros, or with the dummy sign bit or device ID bit set, is rejected as a bus fault. An open thermocouple is reported separately. Invalid readings are logged as blank fields, never as 0 °C.
- **Heater output.** A 10 ms timer fires the SSR in bursts within a 1 s window, so the zero-cross SSR switches whole mains cycles. The duty resolution is 1 %, or 10 W on the 1.0 kW article.
- **Charge mode.** Full power until T1 first reaches the setpoint (550 °C by default), then PI control on T1 with a bumpless handover. The default gains are 0.05 per K (full to zero over 20 K) and 300 s. Tune them in TP3 if T1 overshoots by more than 10 K or oscillates.
- **Hold mode.** PI control on T1 from the start, at a lower setpoint, for the TP2 bake-out.
- **Manual mode.** A fixed duty of up to 25 %, for commissioning and the TP1 fault checks only.
- **Blower.** Either a fixed PWM duty, or a closed-loop exchanger duty in watts: ṁ cp (T5 − T6), with airflow from the TP0 duty-to-flow table. The PWM frequency defaults to 100 Hz, which suits 2-wire 12 V blowers switched by a MOSFET. Change it with `/config?pwm_hz=` if the blower stalls or whines.
- **Logging.** One row every 10 s goes into a 3 h ring buffer in RAM and to the serial port. `tools/logger.py` collects the rows over HTTP. The time stamp is seconds since boot; the logger adds wall-clock time.

## Safety model

Any of the conditions in Table 2 latches a fault. A latched fault turns the heaters off at once and sets the heater mode to off. Clearing the fault never restarts heating: the operator must clear it and then command the heater mode again.

| Bit | Fault | Trigger |
| --- | --- | --- |
| 1 | T1 invalid | T1 open or unreadable for 3 consecutive reads (3 s) |
| 2 | T1 high | T1 above 575 °C, after the calibration offset |
| 4 | Sand high | T3 or T4 above 560 °C (quartz inversion margin) |
| 8 | Log stale | No `/log` poll for more than 60 s, or none since boot |
| 16 | Loop stall | Main loop silent for 6 s; the output timer also forces the SSR off by itself |

*Table 2. Latched faults.*

The ESP32 task watchdog resets the controller if the main loop hangs for 8 s. After a reset the heaters stay off, held by the pull-down resistor, until they are commanded again. The "log stale" fault is latched at every boot, so heaters cannot run until a logging host is connected and the fault has been cleared.

## HTTP API

Every request needs `?token=` when `API_TOKEN` is set. All requests are GET, so they can be sent with `curl` or a browser.

| Request | Effect |
| --- | --- |
| `/status` | JSON: temperatures, modes, duties, power, energy, airflow, exchanger duty, faults |
| `/log?since=N` | CSV header, then the buffered rows after sequence N (up to 360 per call); also the heartbeat |
| `/heater?mode=charge&sp=550` | Charge mode; the setpoint is limited to 20 °C to 550 °C |
| `/heater?mode=hold&sp=200` | Hold mode |
| `/heater?mode=manual&duty=0.10` | Manual duty, 0 to 0.25 |
| `/heater?mode=off` | Heaters off |
| `/blower?mode=duty&value=0.5` | Fixed blower duty, 0 to 1 |
| `/blower?mode=power&value=250` | Closed-loop exchanger duty in W |
| `/blower?mode=off` | Blower off |
| `/config` | Show the configuration. With parameters, set and save it to flash: `v_line`, `r_heat`, `kp`, `ti`, `kpb`, `tib`, `bmin`, `off_t1`, `pwm_hz`, `air` |
| `/clear` | Clear latched faults if no fault condition is present |

*Table 3. HTTP API.*

The `air` table takes duty-to-airflow pairs from TP0, as duty (0 to 1) and L/s, in ascending order. For example: `/config?air=0.25:1.1,0.5:2.2,0.75:3.2,1:4.0`. Set `r_heat` to the parallel hot resistance: the TP0 cold values in parallel, times 1.04. Set `v_line` to the voltage measured at the start of each run.

## Running a test

A typical TP3 charge, from the repo root. Replace `HOST` and `TOKEN` with the controller's address and the API token.

```bash
python firmware/tools/logger.py --host HOST --token TOKEN --procedure TP3 --vline 119.6
```

With the logger running, in a second terminal:

```bash
curl "http://HOST/clear?token=TOKEN"
```

```bash
curl "http://HOST/heater?mode=charge&sp=550&token=TOKEN"
```

Stop by commanding `mode=off`, or press STOP on the enclosure. The logger writes to `docs/05-tests/data/YYYY-MM-DD_TP3.csv`, and a restart on the same day appends to the same file.

## Tests

`pio test -e native` runs 14 unit tests on the host. They cover:

- MAX6675 decoding and bus-fault rejection;
- charge mode's full-power-then-PI behavior;
- PI windup recovery;
- hold and manual modes;
- every safety latch and the rule that faults clear only when conditions are gone;
- burst timing, the airflow lookup and the power and duty math.

The hardware behavior is tested on the article itself in TBK-TST-001, TP1.
