# Purchasing checklist

Test article (TBK-PRC-002), accepted budget $727.70. Generated from `bom-test-article.csv` and `bom-controller-board.csv` by `bom/checklist.py`; regenerate after any BOM change instead of editing this file.

Prices are the BOM's budgetary estimates (US list prices, September 2026, before tax and shipping). Record the price actually paid beside each line.

Tick an item's box when it is ordered, and its **Received** box once it has arrived and passed its check.

## 1. Made-to-order heaters (order first)

Made-to-order cartridge heaters take two to four weeks. Order them the day the build is approved. Subtotal $72.00.

- [ ] **Nichrome heating elements**, qty 4, $18.00 each, $72.00. Supplier: Made-to-order import cartridge heater supplier (Amazon or AliExpress).
  - Specify: 5/8 in (15.9 mm) diameter, 18 in long, 120 V, 250 W, 16 in heated with the 2 in cold end at the lead end, leads 24 in or longer rated for high temperature.
  - [ ] Received: Measure each cold resistance: 55 to 60 ohm, all four within 5 % of each other.

## 2. Uline

Ships in one to three days. Subtotal $115.00.

- [ ] **Steel drum**, qty 1, $115.00 each, $115.00. Supplier: Uline S-19411.
  - Specify: Open head with bolt ring, unlined interior (Uline S-19411).
  - [ ] Received: No liner or interior coating. Remove the lid gasket before first firing.

## 3. Kiln or refractory supplier

Local pottery or kiln suppliers stock K-23 brick; call ahead. Subtotal $22.00.

- [ ] **Insulating firebrick**, qty 4, $5.50 each, $22.00. Supplier: Kiln or refractory supplier.
  - Specify: K-23 insulating firebrick, not dense firebrick.
  - [ ] Received: Light enough to lift easily; about 0.8 kg each.

## 4. DigiKey or Mouser

One order. Subtotal $12.20.

- [ ] **12 V supply**, qty 1, $12.00 each, $12.00. Supplier: Mean Well HDR-15-12 via DigiKey or Mouser.
  - Specify: Mean Well HDR-15-12, or an equal DIN-rail 12 V supply of 1.25 A or more.
  - [ ] Received: quantity and specification match the order.
- [ ] **Pull-down resistors**, qty 2, $0.10 each, $0.20. Supplier: DigiKey or an assortment on hand.
  - Specify: 10 kOhm, 1/4 W. Skip if an assortment is on hand.
  - [ ] Received: quantity and specification match the order.

## 5. Amazon or an electrical wholesaler

Controls, wiring and small parts. Buy from sellers with easy returns. Subtotal $182.00.

- [ ] **Inlet blower**, qty 1, $10.00 each, $10.00. Supplier: Amazon (9733 blower or equal).
  - Specify: 12 V, 0.8 A or less, 97 x 94 x 33 mm. High-speed 2 A to 3 A versions overload the supply.
  - [ ] Received: Run it on 12 V and measure the current.
- [ ] **Blower driver**, qty 1, $3.00 each, $3.00. Supplier: Amazon.
  - Specify: Logic-level MOSFET module rated 5 A or more.
  - [ ] Received: quantity and specification match the order.
- [ ] **Buck converter**, qty 1, $3.00 each, $3.00. Supplier: Amazon.
  - Specify: 12 V in, 5 V out, 3 A.
  - [ ] Received: Set or check 5.0 V out before connecting the ESP32.
- [ ] **ESP32 controller**, qty 1, $7.00 each, $7.00. Supplier: Amazon or Espressif via DigiKey.
  - Specify: Any ESP32-WROOM-32 board exposing GPIO 4, 5, 16, 17, 18, 19, 22, 25 and 26. For the optional controller board, a genuine 38-pin ESP32-DevKitC V4 only.
  - [ ] Received: quantity and specification match the order.
- [ ] **Thermocouple amplifier**, qty 1, $15.00 each, $15.00. Supplier: Amazon.
  - Specify: MAX6675 modules, pack of five.
  - [ ] Received: Pin order GND, VCC, SCK, CS, SO (required for the optional board).
- [ ] **K-type thermocouples**, qty 4, $8.00 each, $32.00. Supplier: Amazon (or Omega or Auber for tighter tolerance).
  - Specify: Type K, mineral insulated, ungrounded junction, 3 mm sheath, 500 mm.
  - [ ] Received: Check with a multimeter that neither lead is connected to the sheath.
- [ ] **Solid state relay**, qty 1, $9.00 each, $9.00. Supplier: Amazon (SSR-25DA or equal).
  - Specify: Zero-cross, DC control 3 to 32 V, AC load, 25 A.
  - [ ] Received: Counterfeits are common. Test it switching a lamp from a 3.3 V and a 5 V control signal.
- [ ] **SSR heat sink**, qty 1, $6.00 each, $6.00. Supplier: Amazon.
  - Specify: Panel mount with thermal pad, sized for one SSR.
  - [ ] Received: quantity and specification match the order.
- [ ] **Independent high limit**, qty 1, $14.00 each, $14.00. Supplier: Amazon.
  - Specify: REX-C100 with relay output (R*AN code), type K input, 100 to 240 VAC supply.
  - [ ] Received: Confirm the output is a relay, not an SSR driver, before panel cutting.
- [ ] **Latching power relay**, qty 1, $10.00 each, $10.00. Supplier: Amazon.
  - Specify: JQX-30F 2Z, DPDT, 120 VAC coil (not 220 VAC or 12 VDC), with DIN-rail socket.
  - [ ] Received: quantity and specification match the order.
- [ ] **Start and stop buttons**, qty 1, $5.00 each, $5.00. Supplier: Amazon.
  - Specify: 22 mm, one red normally closed (STOP) and one green normally open (START), rated 120 VAC.
  - [ ] Received: Check contact states with a multimeter.
- [ ] **Control enclosure**, qty 1, $30.00 each, $30.00. Supplier: Amazon or an electrical wholesaler.
  - Specify: Polycarbonate, 250 x 200 x 150 mm or larger, UL 94 V-0 or 5VA, IP65, with a mounting plate.
  - [ ] Received: Inside depth 140 mm or more (TBK-DWG-005).
- [ ] **DIN rail**, qty 1, $3.00 each, $3.00. Supplier: Amazon or an electrical wholesaler.
  - Specify: TS35 x 7.5.
  - [ ] Received: quantity and specification match the order.
- [ ] **Cable glands**, qty 4, $1.50 each, $6.00. Supplier: Amazon (assortment).
  - Specify: Nylon, IP68, with locknuts: one M16, two M20, one M25.
  - [ ] Received: quantity and specification match the order.
- [ ] **Lever connectors and PE stud**, qty 1, $5.00 each, $5.00. Supplier: Amazon or Home Depot.
  - Specify: Two 5-way lever connectors (Wago 221-415 or equal); M5 earth stud with ring lugs.
  - [ ] Received: quantity and specification match the order.
- [ ] **Wiring consumables**, qty 1, $12.00 each, $12.00. Supplier: Amazon.
  - Specify: Stranded 16 AWG and 22 AWG hookup wire rated 105 C; ferrules to suit; M5 ring lugs; heat-shrink.
  - [ ] Received: quantity and specification match the order.
- [ ] **Thermocouple extension**, qty 1, $12.00 each, $12.00. Supplier: Amazon.
  - Specify: Type K extension grade (not copper), with miniature type K plugs and jacks.
  - [ ] Received: Check polarity: yellow positive, red negative (ANSI).

## 6. Home Depot or Lowe's (one trip)

Pipe, sheet metal, insulation and sand. Subtotal $324.50.

- [ ] **Sand**, qty 3, $6.50 each, $19.50. Supplier: Home Depot or Lowe's (Quikrete play sand or equal).
  - Specify: Washed play sand. Avoid all-purpose or leveling sand, which contains clay.
  - [ ] Received: Weigh each bag.
- [ ] **Heater well pipe**, qty 1, $28.00 each, $28.00. Supplier: Home Depot or Lowe's.
  - Specify: 3/4 in black steel, not galvanized, 10 ft.
  - [ ] Received: quantity and specification match the order.
- [ ] **U-tube legs**, qty 2, $28.00 each, $56.00. Supplier: Home Depot or Lowe's.
  - Specify: 1-1/4 in x 36 in black steel nipples, not galvanized.
  - [ ] Received: quantity and specification match the order.
- [ ] **U-tube elbow**, qty 2, $8.00 each, $16.00. Supplier: Home Depot or Lowe's.
  - Specify: 1-1/4 in black malleable iron 90 deg elbows.
  - [ ] Received: quantity and specification match the order.
- [ ] **U-tube bottom nipple**, qty 1, $6.00 each, $6.00. Supplier: Home Depot or Lowe's.
  - Specify: 1-1/4 in x 6 in black steel nipple.
  - [ ] Received: quantity and specification match the order.
- [ ] **Dilution stack**, qty 1, $12.00 each, $12.00. Supplier: Home Depot or Lowe's.
  - Specify: 4 in single-wall black stovepipe, 24 in, not galvanized.
  - [ ] Received: quantity and specification match the order.
- [ ] **Stone wool batt**, qty 2, $60.00 each, $120.00. Supplier: ROCKWOOL Comfortbatt R15 via Home Depot or Lowe's.
  - Specify: ROCKWOOL Comfortbatt R15, 3.5 in, unfaced.
  - [ ] Received: quantity and specification match the order.
- [ ] **Jacket sheet**, qty 1, $30.00 each, $30.00. Supplier: Home Depot or Lowe's.
  - Specify: Aluminum roll flashing, 20 in x 25 ft.
  - [ ] Received: quantity and specification match the order.
- [ ] **Jacket fasteners and tape**, qty 1, $8.00 each, $8.00. Supplier: Home Depot or Lowe's.
  - Specify: Aluminum foil tape and sheet metal screws.
  - [ ] Received: quantity and specification match the order.
- [ ] **Fuse**, qty 1, $5.00 each, $5.00. Supplier: Home Depot or auto parts store.
  - Specify: Inline holder with 10 A fast-acting fuse; buy a spare fuse.
  - [ ] Received: quantity and specification match the order.
- [ ] **Supply cord**, qty 1, $8.00 each, $8.00. Supplier: Home Depot or Lowe's.
  - Specify: 14/3 SJT with NEMA 5-15 plug, 6 ft.
  - [ ] Received: quantity and specification match the order.
- [ ] **Heater junction box**, qty 1, $8.00 each, $8.00. Supplier: Home Depot plus Amazon.
  - Specify: Steel handy box; ceramic terminal block rated 250 V, 10 A or more.
  - [ ] Received: quantity and specification match the order.
- [ ] **Heater cable**, qty 1, $8.00 each, $8.00. Supplier: Home Depot or Lowe's.
  - Specify: 16/3 SJT, 2 m, black, white and green conductors.
  - [ ] Received: quantity and specification match the order.

**Test article total: $727.70** across 35 lines.

## Optional: controller board (TBK-DWG-004)

Only if building the controller on the printed board. Parts $27.85; the board replaces the buck converter and blower driver above ($6.00), so skip those two lines. Upload `electronics/controller-board/thermabrick-controller-board-gerbers-P1.zip` to the board house: 2 layers, 1.6 mm FR-4, 1 oz copper, HASL, any color.

- [ ] **Printed circuit board**, qty 1, $15.00 each, $15.00. 110 x 80 mm, 2 layer FR-4 1.6 mm, 1 oz copper, HASL; gerbers in electronics/controller-board (minimum order of 5 shares the cost). Supplier: JLCPCB or PCBWay.
  - [ ] Received: quantity and specification match the order.
- [ ] **Regulator**, qty 1, $4.50 each, $4.50. RECOM R-78E5.0-1.0, 12 V to 5 V switching regulator, SIP-3 (U1). Supplier: DigiKey or Mouser.
  - [ ] Received: quantity and specification match the order.
- [ ] **Input capacitor**, qty 1, $0.20 each, $0.20. Aluminum electrolytic 10 uF 25 V, 5 mm diameter, 2 mm pitch (C1). Supplier: DigiKey or Mouser.
  - [ ] Received: quantity and specification match the order.
- [ ] **Output capacitor**, qty 1, $0.20 each, $0.20. Aluminum electrolytic 22 uF 10 V, 5 mm diameter, 2 mm pitch (C2). Supplier: DigiKey or Mouser.
  - [ ] Received: quantity and specification match the order.
- [ ] **SSR driver transistor**, qty 1, $0.10 each, $0.10. 2N3904 NPN, TO-92 (Q1). Supplier: DigiKey or Mouser.
  - [ ] Received: quantity and specification match the order.
- [ ] **Blower MOSFET**, qty 1, $1.20 each, $1.20. IRLZ44N logic-level N-MOSFET, TO-220 (Q2). Supplier: DigiKey or Mouser.
  - [ ] Received: quantity and specification match the order.
- [ ] **Flyback diode**, qty 1, $0.15 each, $0.15. 1N5819 Schottky, DO-41 (D1). Supplier: DigiKey or Mouser.
  - [ ] Received: quantity and specification match the order.
- [ ] **Resistors**, qty 2, $0.10 each, $0.20. 1 kOhm (R3) and 100 Ohm (R4), 1/4 W, axial. Supplier: DigiKey or an assortment on hand.
  - [ ] Received: quantity and specification match the order.
- [ ] **ESP32 sockets**, qty 2, $0.80 each, $1.60. Female header 1x19, 2.54 mm, straight. Supplier: DigiKey or Amazon.
  - [ ] Received: quantity and specification match the order.
- [ ] **Module sockets**, qty 5, $0.30 each, $1.50. Female header 1x5, 2.54 mm, straight. Supplier: DigiKey or Amazon.
  - [ ] Received: quantity and specification match the order.
- [ ] **Screw terminals**, qty 3, $0.40 each, $1.20. 2-way screw terminal, 5.08 mm pitch (Phoenix MKDS 1,5 or equal). Supplier: DigiKey or Amazon.
  - [ ] Received: quantity and specification match the order.
- [ ] **Standoffs**, qty 4, $0.50 each, $2.00. M3 x 10 mm nylon standoff with screw. Supplier: Amazon.
  - [ ] Received: quantity and specification match the order.

## Tools and safety equipment (not in the budget)

- [ ] Multimeter with continuity and resistance ranges
- [ ] Bathroom scale (0.1 kg graduation)
- [ ] Vise, pipe cutter for 3/4 in pipe, and pipe wrenches
- [ ] Drill with hole saws or step drill: 22.5 mm (buttons), 28.7 mm and 44.2 mm (drum lid), 16.5, 20.5 and 25.5 mm (glands)
- [ ] Jigsaw or nibbler and file for the 45 x 45 mm REX-C100 cutout
- [ ] Tin snips and pop rivet gun
- [ ] Stopwatch and 159 L (42 gal) contractor bags for the airflow calibration
- [ ] Contact or infrared thermometer for jacket and stack surfaces (all five MAX6675 channels are in use)
- [ ] Insulation tester at 500 V, borrowed or rented, for TBK-TST-001 TP2
- [ ] P100 or N95 respirator, gloves and eye protection for sand and mineral wool

## Before building

- [ ] Every Received box ticked and every arrival check passed.
- [ ] Heater resistances recorded for TBK-TST-001 TP0.
- [ ] Firmware built and host unit tests passing (`pio test -e native` in `firmware/`).
- [ ] Analysis self-test passing (`python docs/05-tests/tbk_tst_001_fit.py selftest`).
