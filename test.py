thisCaption = """No problem! Here's the information about the Mercedes CLR GTR:

The Mercedes CLR GTR is a remarkable racing car celebrated for its outstanding performance and sleek design. Powered by a potent 6.0-liter V12 engine, it delivers over 600 horsepower.

Acceleration from 0 to 100 km/h takes approximately 3.7 seconds, with a remarkable top speed surprising 320 km/h.🥇

Incorporating adventure aerodynamic features and cutting-edge stability technologies, the CLR GTR ensures exceptional stability and control, particularly during high-speed maneuvers. 💨

Originally priced at around $1.5 million, the Mercedes CLR GTR is considered one of the most exclusive and prestigious racing cars ever produced. 💰

Its limited production run of just five units adds to its rarity, making it highly sought after by racing enthusiasts and collectors worldwide. 🌎"""


def remove_unsupported_bmp_emojis(text):
    return ''.join(char for char in text if ord(char) <= 0xFFFF)

# Example usage:
text_with_emojis = "Hello 😀🎉 This is a test 🚀"
cleaned_text = remove_unsupported_bmp_emojis(thisCaption)
print(cleaned_text)
