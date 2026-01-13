#include <LiquidCrystal.h>

LiquidCrystal lcd(2, 3, 4, 5, 6, 7);

const int buzzer_Pin = 8;
const int button_1 = 9;
const int button_2 = 10;
const int button_3 = 11;

static int party_1_count = 0;
static int party_2_count = 0;
static int party_3_count = 0;

String winner_name = "";

void setup() {
  pinMode(buzzer_Pin, OUTPUT);
  pinMode(button_1, INPUT);
  pinMode(button_2, INPUT);
  pinMode(button_3, INPUT);

  Serial.begin(9600);
  
  lcd.begin(16, 2);
  lcd.print("SMART VOTING");
  lcd.setCursor(0, 1);
  lcd.print("MACHINE");
  delay(3000);
}

void loop() {
  if (Serial.available()) {
    char a = Serial.read();

    if (a == 'a') {  // Face recognized - Wait for vote input
      lcd.clear();
      lcd.print("Please vote now");

      bool vote_casted = false;
      
      while (!vote_casted) {  // Wait until a button is pressed
        if (digitalRead(button_1) == HIGH) {
          party_1_count++;
          vote_casted = true;
        }
        if (digitalRead(button_2) == HIGH) {
          party_2_count++;
          vote_casted = true;
        }
        if (digitalRead(button_3) == HIGH) {
          party_3_count++;
          vote_casted = true;
        }
      }

      // Confirm vote with buzzer and LCD
      digitalWrite(buzzer_Pin, HIGH);
      delay(500);
      digitalWrite(buzzer_Pin, LOW);
      lcd.clear();
      lcd.print("Vote recorded");
      delay(2000);
    } 
    else if (a == 'c') {  // Admin - Show results
      lcd.clear();
      lcd.print("Winner is:");
      lcd.setCursor(0, 1);

      if (party_1_count > party_2_count && party_1_count > party_3_count) {
        winner_name = "Party A";
      } else if (party_2_count > party_1_count && party_2_count > party_3_count) {
        winner_name = "Party B";
      } else {
        winner_name = "Party C";
      }

      lcd.print(winner_name);
      delay(5000);
    } 
    else if (a == 'b') {  // Invalid voter alert
      lcd.clear();
      lcd.print("Access Denied");
      digitalWrite(buzzer_Pin, HIGH);
      delay(1000);
      digitalWrite(buzzer_Pin, LOW);
    }
  }
}