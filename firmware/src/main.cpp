#include <Arduino.h>
#include <math.h>

// Dodge B2500 cluster LED PWM dimmer
// Board: Seeed Studio XIAO RP2040
//
// Hardware behavior:
//   DIM_IN -> resistor divider -> A0
//   D1 PWM -> Q2 -> Q1 P-channel high-side MOSFET
//   PWM pin HIGH means cluster LEDs ON, assuming the schematic in this repo.
//
// Install note:
//   Power board from a full 12 V illumination/headlight-switched feed.
//   Do NOT power board from the dimmed rheostat output.

// ---------------- User calibration constants ----------------

// XIAO RP2040 / RP2040 ADC is treated as 12-bit in the Arduino-Pico core.
static constexpr uint16_t ADC_MAX_COUNT = 4095;

// Resistor divider: DIM_IN -> 100k -> ADC node -> 22k -> GND
static constexpr float ADC_REF_VOLTS = 3.30f;
static constexpr float R_TOP_OHMS = 100000.0f;
static constexpr float R_BOTTOM_OHMS = 22000.0f;
static constexpr float DIVIDER_RATIO = R_BOTTOM_OHMS / (R_TOP_OHMS + R_BOTTOM_OHMS);

// PWM configuration.
// Keep this modest for automotive wiring; 976 Hz is a good starting point.
static constexpr uint32_t PWM_FREQ_HZ = 976;
static constexpr uint16_t PWM_RANGE = 4095;

// Pin assignments.
static constexpr pin_size_t PIN_DIM_ADC = A0;
static constexpr pin_size_t PIN_PWM_GATE = D1;
static constexpr pin_size_t PIN_CAL_BUTTON = D2;

// Set true only if your gate driver hardware inverts desired brightness.
static constexpr bool PWM_INVERTED = false;

// Set true if the factory dimmer reads high at dim and low at bright.
static constexpr bool REVERSE_DIMMER_DIRECTION = false;

// ADC thresholds.
// With the 100k/22k divider, 14.4 V at DIM_IN is about 3220 counts.
// Use serial debug to tune these after bench testing with the real dimmer.
static constexpr uint16_t ADC_OFF_THRESHOLD = 10;    // below this, force off
static constexpr uint16_t ADC_MIN_INPUT = 25;        // dimmest usable reading
static constexpr uint16_t ADC_MAX_INPUT = 3220;      // full-bright reading

// Output duty limits.
// Many LED bulbs do not behave nicely at extremely tiny duty cycles.
// Raise MIN_DUTY if the LEDs flicker or drop out at the bottom of the range.
static constexpr uint16_t DUTY_MIN = 20;             // about 0.5%
static constexpr uint16_t DUTY_MAX = PWM_RANGE;

// Perceptual curve.
// 1.0 = linear.
// 1.4-2.2 often feels better for LEDs.
// Lower this if the low end feels too compressed.
static constexpr float GAMMA = 1.60f;

// Smoothing.
// Alpha closer to 1 = more responsive, less smoothing.
// Alpha closer to 0 = smoother, slower.
static constexpr float FILTER_ALPHA = 0.12f;

// Serial print interval.
static constexpr uint32_t DEBUG_INTERVAL_MS = 500;

// ---------------- Internal state ----------------

static float filteredAdc = 0.0f;
static uint32_t lastDebugMs = 0;

static uint16_t readAdcAveraged(pin_size_t pin, uint8_t samples = 16) {
  uint32_t acc = 0;
  for (uint8_t i = 0; i < samples; i++) {
    acc += analogRead(pin);
    delayMicroseconds(250);
  }
  return static_cast<uint16_t>(acc / samples);
}

static float adcToDimVolts(float adcCounts) {
  const float vAdc = (adcCounts / static_cast<float>(ADC_MAX_COUNT)) * ADC_REF_VOLTS;
  return vAdc / DIVIDER_RATIO;
}

static uint16_t desiredDutyFromAdc(float adcCounts) {
  if (adcCounts <= ADC_OFF_THRESHOLD) {
    return 0;
  }

  float x = (adcCounts - static_cast<float>(ADC_MIN_INPUT)) /
            (static_cast<float>(ADC_MAX_INPUT) - static_cast<float>(ADC_MIN_INPUT));

  if (x < 0.0f) x = 0.0f;
  if (x > 1.0f) x = 1.0f;

  if (REVERSE_DIMMER_DIRECTION) {
    x = 1.0f - x;
  }

  // Apply perceptual gamma curve.
  float curved = powf(x, GAMMA);

  uint16_t duty = static_cast<uint16_t>(
      DUTY_MIN + curved * static_cast<float>(DUTY_MAX - DUTY_MIN));

  if (duty > DUTY_MAX) duty = DUTY_MAX;
  return duty;
}

static void writePwmDuty(uint16_t duty) {
  if (duty > PWM_RANGE) duty = PWM_RANGE;

  uint16_t out = duty;
  if (PWM_INVERTED) {
    out = PWM_RANGE - duty;
  }

  analogWrite(PIN_PWM_GATE, out);
}

void setup() {
#if defined(SERIAL_DEBUG)
  Serial.begin(115200);
  delay(500);
  Serial.println();
  Serial.println("Dodge B2500 cluster LED PWM dimmer starting...");
#endif

  pinMode(PIN_DIM_ADC, INPUT);
  pinMode(PIN_PWM_GATE, OUTPUT);
  pinMode(PIN_CAL_BUTTON, INPUT_PULLUP);

  analogReadResolution(12);

#if defined(ARDUINO_ARCH_RP2040)
  // Earle Philhower RP2040 Arduino core supports these.
  analogWriteFreq(PWM_FREQ_HZ);
  analogWriteRange(PWM_RANGE);
#else
  // Other Arduino cores may ignore frequency/range settings.
  analogWriteResolution(12);
#endif

  writePwmDuty(0);

  uint16_t initial = readAdcAveraged(PIN_DIM_ADC, 32);
  filteredAdc = static_cast<float>(initial);
}

void loop() {
  const uint16_t rawAdc = readAdcAveraged(PIN_DIM_ADC, 16);

  // Exponential moving average smoothing.
  filteredAdc = (FILTER_ALPHA * static_cast<float>(rawAdc)) +
                ((1.0f - FILTER_ALPHA) * filteredAdc);

  const uint16_t duty = desiredDutyFromAdc(filteredAdc);
  writePwmDuty(duty);

#if defined(SERIAL_DEBUG)
  const uint32_t now = millis();
  if (now - lastDebugMs >= DEBUG_INTERVAL_MS) {
    lastDebugMs = now;

    const float dimVolts = adcToDimVolts(filteredAdc);
    const float dutyPct = (static_cast<float>(duty) / static_cast<float>(PWM_RANGE)) * 100.0f;

    Serial.print("raw=");
    Serial.print(rawAdc);
    Serial.print(" filtered=");
    Serial.print(filteredAdc, 1);
    Serial.print(" dimV=");
    Serial.print(dimVolts, 2);
    Serial.print(" duty=");
    Serial.print(duty);
    Serial.print(" dutyPct=");
    Serial.print(dutyPct, 1);
    Serial.println("%");
  }
#endif

  delay(5);
}
