#define RED_LED     9
#define GREEN_LED   10
#define MAIN_BUT    2
#define POW_SWITCH  3
#define ENCODER_A   4
#define ENCODER_B   5

#define ENCODER_MAX_COUNTS      7

// Bounce2 https://github.com/thomasfredericks/Bounce-Arduino-Wiring/
#include <Bounce2.h>

Bounce mainDebouncer = Bounce(); 
Bounce powDebouncer = Bounce();

volatile uint8_t encoderState = 0;
volatile uint8_t encoderPosition = 0;

ISR(PCINT2_vect)
{
    int state = PIND & _BV(PIND4);

    if (state != encoderState) {
        if (!state) {
            if (PIND & _BV(PIND5)) {
                ++encoderPosition;
            } else if (encoderPosition > 0) {
                --encoderPosition;
            }
        }
    }
    encoderState = state;
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
    }
    lastMainState = state;
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
        }
    }
    lastPowState = state;
}

void checkEncoder()
{
    static uint8_t lastEncoderPosition = 0;

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

    Serial.println("SMC:0");
}

void loop()
{
    checkMainButton();
    checkPowerSwitch();
    checkEncoder();
}
