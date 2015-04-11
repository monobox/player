#define RED_LED     9
#define GREEN_LED   10
#define AUDIO_OUT   11
#define MAIN_BUT    2
#define POW_SWITCH  3
#define POT_IN      A0

// Bounce2 https://github.com/thomasfredericks/Bounce-Arduino-Wiring/
#include <Bounce2.h>

Bounce mainDebouncer = Bounce(); 
Bounce powDebouncer = Bounce(); 


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
        Serial.println(!state);
    }
    lastPowState = state;
}

uint16_t getPotValue()
{
    uint16_t sum = 0;

    for (uint8_t i = 0 ; i < 5 ; ++i) {
        sum += analogRead(POT_IN);
        delay(1);
    }

    return sum / 5;
}

void checkPot()
{
    static int lastLevel = -1;
    int currentLevel = constrain(map(getPotValue(), 0, 1023, 0, 100), 0, 100);

    if (lastLevel != currentLevel) {
        Serial.print("V:");
        Serial.println(currentLevel);
        lastLevel = currentLevel;
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

    Serial.println("SMC:0");
}

void loop()
{
    checkMainButton();
    checkPowerSwitch();
    checkPot();
}
