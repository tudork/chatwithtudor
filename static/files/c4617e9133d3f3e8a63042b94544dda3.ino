int led1 = 10;
int led2 = 11;
int led3 = 12;
int led4 = 13;

int Pot1 = 0;

void setup()
{
  // initialize the digital pin as an output.
  Serial.begin(9600);
  pinMode(led1, OUTPUT);
  pinMode(led2, OUTPUT);
  pinMode(led3, OUTPUT);
  pinMode(led4, OUTPUT);
}

int a, b, c, d, i;
void loop()
{
  for (int k = 0; k < 16; k ++) {
    delay(1000);
    digitalWrite(led1, HIGH );
    digitalWrite(led2, HIGH );
    digitalWrite(led3, HIGH );
    digitalWrite(led4, HIGH );
    i = k;
    a =  i % 2;
    i = i / 2;
    b =  i % 2;
    i = i / 2;
    c =  i % 2;
    i = i / 2;
    d =  i % 2;
    i = i / 2;
    if (a == 1)
      digitalWrite(led1, LOW );
    if (b == 1)
      digitalWrite(led2, LOW );
    if (c == 1)
      digitalWrite(led3, LOW );
    if (d == 1)
      digitalWrite(led4, LOW );
  }
}
