const int DOT_DELAY = 800;
const int DASH_DELAY = 2500;
const int SPACE_DELAY = 1000;

void setup() {
    pinMode(LED_BUILTIN, OUTPUT);
    Serial.begin(9600); // Initialize serial communication
    Serial.print("******* MORSE CODE TRANSLATOR *******");
    Serial.println("Enter a word or a sentence to be translated into Morse code:");
}

void loop() {
    if (Serial.available() > 0) {
        String inputString = getUserInput(); 
        Serial.print("You entered: ");
        Serial.println(inputString); 
        translateToMorse(inputString); 
    }
}

String getUserInput() {
    String inputString = Serial.readStringUntil('\n'); // Read user input until newline character
    inputString.trim(); // Remove leading and trailing whitespaces
    return inputString;
}

void translateToMorse(String inputString) {
    // Dictionary mapping letters to Morse code
    // Add more letters as needed
    String morseDictionary[26] = {".-", "-...", "-.-.", "-..", ".", "..-.", "--.", "....", "..", ".---", 
                                  "-.-", ".-..", "--", "-.", "---", ".--.", "--.-", ".-.", "...", "-", 
                                  "..-", "...-", ".--", "-..-", "-.--", "--.."};

    // Loop through each character in the input string
    for (int i = 0; i < inputString.length(); i++) {
        char letter = toUpperCase(inputString.charAt(i)); // Convert character to uppercase
        if (letter >= 'A' && letter <= 'Z') { // Check if character is a letter
            String morseCode = morseDictionary[letter - 'A']; // Get Morse code for the letter
            transmitMorseCode(morseCode); // Transmit Morse code
            delay(SPACE_DELAY); // Add delay between characters
        }
    }
}

void blinkDot() {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(DOT_DELAY);
    digitalWrite(LED_BUILTIN, LOW);
}

void blinkDash() {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(DASH_DELAY);
    digitalWrite(LED_BUILTIN, LOW);
}

void transmitMorseCode(String morseCode) {
    for (int i = 0; i < morseCode.length(); i++) {
        char symbol = morseCode.charAt(i);
        if (symbol == '.') {
            blinkDot();
        } else if (symbol == '-') {
            blinkDash();
        }
        delay(DOT_DELAY); // Add delay between dots and dashes
    }
}


