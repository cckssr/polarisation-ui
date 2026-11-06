#pragma once

// ── Pin map (ESP32 DevKit V1, ESP-WROOM-32) ────────────────────────────────────────────
// Avoid the strapping pins 0/2/5/12/15 and the flash pins 6-11.
#define PIN_STEP 25 // DRV8825 STEP
#define PIN_DIR 26  // DRV8825 DIR
#define PIN_EN 27   // DRV8825 /ENABLE (active LOW)
#define PIN_MS1 16  // DRV8825 M0
#define PIN_MS2 17  // DRV8825 M1
#define PIN_MS3 18  // DRV8825 M2

// ── DRV8825 /FAULT (optional, recommended) ────────────────────────────────────
// The DRV8825 has no status register; /FAULT (open drain, low = overcurrent or
// over-temperature) is its only feedback. Wire it to this pin (internal pull-up
// is enabled) or set -1 if not connected: DIAG:DRV? then reports NA.
// Use an input-capable pin: 32/33 work, 34-39 are input-only without pull-up.
#define PIN_FAULT 32
#define SELFTEST_DEG 5.0f // DIAG:SELF? moves this far out and back

// ── DRV8825 /RESET (optional) ─────────────────────────────────────────────────
// With /RESET on a GPIO the firmware can clear a latched overcurrent fault
// (DIAG:DRV:RES) without power-cycling VMOT. Leave -1 while /RESET is tied to
// 3.3 V — never drive a pin that is hard-wired to a supply rail.
// Suggested pin once wired: 19 (free, no boot-strapping role).
#define PIN_RESET 19

// ── Optional home switch ──────────────────────────────────────────────────────
// Set PIN_HOME to -1 if no switch is fitted: MOT:HOME then simply defines the
// current position as 0° (mount the wheel at its clear position first).
#define PIN_HOME -1
#define HOME_ACTIVE_LEVEL LOW // level read when the switch is triggered (INPUT_PULLUP)
#define HOME_DIRECTION -1     // sense of travel towards the switch; keep -1 so the switch sits
                              // at the low end and 0..360 deg lies on the far side of it
#define HOME_SEEK_DPS 20.0f   // constant seek speed, deg/s (no ramp)
#define HOME_BACKOFF_DEG 2.0f // extra travel off the switch before zeroing
#define HOME_MAX_SEEK_DEG 400.0f

// ── Mechanics ─────────────────────────────────────────────────────────────────
#define MOTOR_STEPS_PER_REV 200 // 1.8° motor
#define MICROSTEPS 32           // 1, 2, 4, 8, 16 or 32 — must match the MS1..MS3 pins below
#define GEAR_RATIO 4.0f         // motor revolutions per output revolution (>1 = geared down)
#define DIR_INVERT 0            // 1 flips the sense of positive angles

// ── Idle release ──────────────────────────────────────────────────────────────
// The DRV8825 holds at full current (2 x VREF) whenever it is enabled, which
// heats driver and motor. With a non-zero value the motor is released this many
// ms after a move finishes and re-energised automatically by the next move.
// 0 = hold forever. Change at runtime with CONF:MOT:IDLE <ms>.
// While released the wheel is not held: set 0 for measurements if it can drift.
#define IDLE_DISABLE_MS 0

// ── Motion defaults and limits (output shaft, degrees) ────────────────────────
#define DEFAULT_SPEED_DPS 60.0f
#define DEFAULT_ACCEL_DPS2 180.0f
#define MAX_SPEED_DPS 360.0f
#define DEFAULT_LIMIT_MIN_DEG -360.0f // zero is only a reference; negative angles are fine
#define DEFAULT_LIMIT_MAX_DEG 360.0f

// ── Serial / identity ─────────────────────────────────────────────────────────
#define BAUD_RATE 115200
#define DEVICE_MFR "Custom ESP32"
#define DEVICE_MODEL "ND-Stepper-DRV8825"
#define DEVICE_SERIAL "0"
#define FW_VERSION "1.0.0"

#define ERR_QUEUE_SIZE 8
