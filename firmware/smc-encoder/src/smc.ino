#define RED_LED     9
#define GREEN_LED   10
#define MAIN_BUT    2
#define POW_SWITCH  3
#define ENCODER_A   4
#define ENCODER_B   5

#define MCP4131_CS  10

#define ENCODER_MAX_COUNTS      27

// Bounce2 https://github.com/thomasfredericks/Bounce-Arduino-Wiring/
#include <Bounce2.h>

// https://github.com/jmalloc/arduino-mcp4xxx
#include <mcp4xxx.h>

Bounce mainDebouncer = Bounce(); 
Bounce powDebouncer = Bounce();
MCP4XXX pot(MCP4131_CS);

volatile uint8_t lastStateA = 0, lastStateB = 0;
volatile int8_t encoderPosition;

ISR(PCINT2_vect)
{
    uint8_t stateA = PIND & _BV(PIND4);
    uint8_t stateB = PIND & _BV(PIND5);

    // A changed state
    if (stateA != lastStateA) {
        // Positive A flank
        if (stateA) {
            if (stateB) {
                if (encoderPosition > 0) {
                    --encoderPosition;
                }
            } else {
                ++encoderPosition;
            }
        // Negative A flank
        } else {
            if (stateB) {
                ++encoderPosition;
            } else {
                if (encoderPosition > 0) {
                    --encoderPosition;
                }
            }
        }
    // B changed state (the test is unnecessary)
    } else if (stateB != lastStateB) {
        // Positive B flank
        if (stateB) {
            if (stateA) {
                ++encoderPosition;
            } else {
                if (encoderPosition > 0) {
                    --encoderPosition;
                }
            }
        // Negative B flank
        } else {
            if (stateA) {
                if (encoderPosition > 0) {
                    --encoderPosition;
                }
            } else {
                ++encoderPosition;
            }
        }
    }

    lastStateA = stateA;
    lastStateB = stateB;
}

void checkMainButton()
{
    static int8_t lastMainState = 1;
    int8_t state;

    mainDebouncer.update();
    state = mainDebouncer.read();
    if (state != lastMainState) {
        Serial.print("B:");
        Serial.println(!state);

        if (state) {
            tone(9, 800);
            delay(100);
            noTone(9);
        }
    }
    lastMainState = state;
}

void beep()
{
    tone(9, 200);
    delay(100);
    tone(9, 400);
    delay(100);
    tone(9, 600);
    delay(100);
    tone(9, 800);
    delay(100);
    noTone(9);
}

void checkPowerSwitch()
{
    static int8_t lastPowState = 1;
    int8_t state;

    powDebouncer.update();
    state = powDebouncer.read();

    if (state != lastPowState) {
        Serial.print("P:");
        Serial.println(state);

        if (state == 0) {
            encoderPosition = 0;
        } else {
            beep();
        }
    }
    lastPowState = state;
}

void checkEncoder()
{
    static uint8_t lastEncoderPosition = 0;

    pot.set(map(encoderPosition, 0, ENCODER_MAX_COUNTS, 0, 127));

    if (lastEncoderPosition != encoderPosition) {
        Serial.print("V:");
        Serial.println(constrain(map(encoderPosition, 0, ENCODER_MAX_COUNTS,
                0, 100), 0, 100));
        lastEncoderPosition = encoderPosition;
    }
}

void setup()
{
    Serial.begin(115200);

    pinMode(MAIN_BUT, INPUT_PULLUP);
    mainDebouncer.attach(MAIN_BUT);
    mainDebouncer.interval(10);

    pinMode(POW_SWITCH, INPUT_PULLUP);
    powDebouncer.attach(POW_SWITCH);
    powDebouncer.interval(10);

    PCICR |= _BV(PCIE2);
    PCMSK2 |= _BV(PCINT20);
    PCMSK2 |= _BV(PCINT21);

    pot.set(0);
    Serial.println("SMC:0");
}

void loop()
{
    checkMainButton();
    checkPowerSwitch();
    checkEncoder();
}
